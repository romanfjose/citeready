"""Core auditing and Fix-Pack ZIP generation engine (zero external dependencies)."""

from __future__ import annotations

import concurrent.futures
import html
import io
import json
import re
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from typing import Any

USER_AGENT = "Mozilla/5.0 (compatible; CiteReadyAudit/1.0; +https://citeready.dev)"
AI_BOTS = ["OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Google-Extended"]


class PageMetadataParser(HTMLParser):
    """Extracts title, meta tags, canonical link, JSON-LD blocks, headings, links, and body text."""

    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.in_title = False
        self.in_script_ld = False
        self.in_ignored = 0
        self.current_ld: list[str] = []
        self.json_ld_raw: list[str] = []
        self.meta: dict[str, str] = {}
        self.canonical: str = ""
        self.headings: list[tuple[str, str]] = []
        self._current_heading_tag: str | None = None
        self._current_heading_buf: list[str] = []
        self.links: list[tuple[str, str]] = []
        self._current_a_href: str | None = None
        self._current_a_buf: list[str] = []
        self.text_chunks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        attr_map = {k.lower(): (v or "") for k, v in attrs}
        if t == "title":
            self.in_title = True
        elif t == "meta":
            name = (attr_map.get("name") or attr_map.get("property") or "").lower().strip()
            content = attr_map.get("content", "").strip()
            if name and content and name not in self.meta:
                self.meta[name] = content
        elif t == "link":
            rel = attr_map.get("rel", "").lower()
            href = attr_map.get("href", "").strip()
            if "canonical" in rel and href and not self.canonical:
                self.canonical = urllib.parse.urljoin(self.base_url, href)
        elif t == "script":
            stype = attr_map.get("type", "").lower()
            if "application/ld+json" in stype:
                self.in_script_ld = True
                self.current_ld = []
            else:
                self.in_ignored += 1
        elif t in ("style", "noscript", "svg", "template"):
            self.in_ignored += 1
        elif t in ("h1", "h2", "h3"):
            self._current_heading_tag = t
            self._current_heading_buf = []
        elif t == "a":
            href = attr_map.get("href", "").strip()
            if href and not href.startswith(("#", "javascript:", "mailto:", "tel:")):
                self._current_a_href = urllib.parse.urljoin(self.base_url, href)
                self._current_a_buf = []

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "title":
            self.in_title = False
        elif t == "script":
            if self.in_script_ld:
                self.in_script_ld = False
                raw = "".join(self.current_ld).strip()
                if raw:
                    self.json_ld_raw.append(raw)
            elif self.in_ignored > 0:
                self.in_ignored -= 1
        elif t in ("style", "noscript", "svg", "template"):
            if self.in_ignored > 0:
                self.in_ignored -= 1
        elif t in ("h1", "h2", "h3") and self._current_heading_tag == t:
            txt = _clean_ws("".join(self._current_heading_buf))
            if txt:
                self.headings.append((t.upper(), txt))
            self._current_heading_tag = None
        elif t == "a" and self._current_a_href:
            txt = _clean_ws("".join(self._current_a_buf))
            self.links.append((self._current_a_href, txt))
            self._current_a_href = None

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.in_script_ld:
            self.current_ld.append(data)
            return
        if self.in_ignored > 0:
            return
        if self._current_heading_tag:
            self._current_heading_buf.append(data)
        if self._current_a_href is not None:
            self._current_a_buf.append(data)
        cleaned = _clean_ws(data)
        if cleaned:
            self.text_chunks.append(cleaned)

    @property
    def title(self) -> str:
        return _clean_ws("".join(self.title_parts))


def _clean_ws(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(s or "")).strip()


def normalize_url(raw_url: str) -> str:
    u = raw_url.strip()
    if not re.match(r"^https?://", u, re.IGNORECASE):
        u = "https://" + u
    parsed = urllib.parse.urlsplit(u)
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    return urllib.parse.urlunsplit((scheme, netloc, path, "", ""))


def fetch_url(url: str, timeout: float = 6.0, max_bytes: int = 350_000) -> dict[str, Any]:
    ctx = ssl.create_default_context()
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,text/plain,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            body_bytes = resp.read(max_bytes)
            headers = {k.lower(): v for k, v in resp.headers.items()}
            ctype = headers.get("content-type", "")
            charset_match = re.search(r"charset=([\w-]+)", ctype, re.IGNORECASE)
            encoding = charset_match.group(1) if charset_match else "utf-8"
            try:
                text = body_bytes.decode(encoding, errors="replace")
            except LookupError:
                text = body_bytes.decode("utf-8", errors="replace")
            return {
                "ok": True,
                "status": resp.status,
                "final_url": resp.geturl(),
                "headers": headers,
                "text": text,
                "elapsed_ms": round((time.monotonic() - t0) * 1000),
                "error": None,
            }
    except urllib.error.HTTPError as e:
        headers = {k.lower(): v for k, v in e.headers.items()} if e.headers else {}
        return {
            "ok": False,
            "status": e.code,
            "final_url": url,
            "headers": headers,
            "text": "",
            "elapsed_ms": round((time.monotonic() - t0) * 1000),
            "error": f"HTTP {e.code}",
        }
    except Exception as e:
        return {
            "ok": False,
            "status": 0,
            "final_url": url,
            "headers": {},
            "text": "",
            "elapsed_ms": round((time.monotonic() - t0) * 1000),
            "error": str(e),
        }


def query_dns_txt(hostname: str, timeout: float = 4.0) -> list[str]:
    """Query DNS TXT records over Cloudflare DNS-over-HTTPS (zero external packages)."""
    q_url = f"https://cloudflare-dns.com/dns-query?name={urllib.parse.quote(hostname)}&type=TXT"
    req = urllib.request.Request(q_url, headers={"Accept": "application/dns-json", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read(65536).decode("utf-8", errors="replace"))
        records: list[str] = []
        for ans in data.get("Answer", []) or []:
            if ans.get("type") == 16:
                raw_txt = str(ans.get("data", "")).strip()
                # Strip surrounding quotes and join split TXT chunks
                cleaned = raw_txt.replace('" "', "").strip('"')
                records.append(cleaned)
        return records
    except Exception:
        return []


def analyze_robots_txt(robots_text: str) -> dict[str, Any]:
    """Check whether AI search citation bots are explicitly blocked in robots.txt (RFC 9309 group semantics)."""
    groups: list[tuple[list[str], list[str], list[str]]] = []
    agents: list[str] = []
    disallows: list[str] = []
    allows: list[str] = []
    seen_rule_in_group = False

    for raw_line in robots_text.splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line or ":" not in line:
            continue
        k, v = [x.strip() for x in line.split(":", 1)]
        kl = k.lower()
        if kl == "user-agent":
            if seen_rule_in_group and agents:
                groups.append((agents, disallows, allows))
                agents, disallows, allows = [], [], []
                seen_rule_in_group = False
            agents.append(v)
        elif kl == "disallow":
            seen_rule_in_group = True
            if v:
                disallows.append(v)
        elif kl == "allow":
            seen_rule_in_group = True
            if v:
                allows.append(v)

    if agents:
        groups.append((agents, disallows, allows))

    blocked_bots: list[str] = []
    wildcard_disallow_all = False
    for g_agents, g_disallows, g_allows in groups:
        if "/" in g_disallows and "/" not in g_allows:
            if "*" in g_agents:
                wildcard_disallow_all = True
            for bot in AI_BOTS:
                if any(a.lower() == bot.lower() for a in g_agents) and bot not in blocked_bots:
                    blocked_bots.append(bot)

    explicitly_mentions_ai = any(bot.lower() in robots_text.lower() for bot in AI_BOTS)
    return {
        "blocked_bots": blocked_bots,
        "wildcard_disallow_all": wildcard_disallow_all,
        "explicitly_mentions_ai": explicitly_mentions_ai,
    }


@dataclass
class CheckItem:
    id: str
    category: str
    title: str
    status: str  # "pass" | "warn" | "fail"
    points: int
    max_points: int
    evidence: str
    fix_summary: str


@dataclass
class AuditResult:
    target_url: str
    final_url: str
    domain: str
    root_domain: str
    timestamp_utc: str
    score: int
    grade: str
    response_ms: int
    site_title: str
    site_description: str
    checks: list[CheckItem] = field(default_factory=list)
    crawled_pages: list[dict[str, Any]] = field(default_factory=list)
    existing_robots: str = ""
    spf_records: list[str] = field(default_factory=list)
    dmarc_records: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _extract_root_domain(netloc: str) -> str:
    host = netloc.split(":")[0].lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    return host


def _grade_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 45:
        return "D"
    return "F"


def audit_url(raw_url: str, crawl_subpages: int = 4) -> AuditResult:
    """Perform a full 12-point live GEO + Metadata + Security + DNS Deliverability audit."""
    target_url = normalize_url(raw_url)
    home_resp = fetch_url(target_url, timeout=7.0)
    if not home_resp["ok"] and home_resp["status"] == 0:
        raise RuntimeError(f"Could not reach {target_url}: {home_resp['error']}")

    final_url = home_resp["final_url"] or target_url
    parsed_final = urllib.parse.urlsplit(final_url)
    origin = f"{parsed_final.scheme}://{parsed_final.netloc}"
    domain = parsed_final.netloc.split(":")[0].lower()
    root_domain = _extract_root_domain(domain)

    parser = PageMetadataParser(final_url)
    try:
        parser.feed(home_resp["text"])
    except Exception:
        pass

    # Parallel fetch of auxiliary endpoints + DNS TXT records
    aux_urls = {
        "robots": f"{origin}/robots.txt",
        "llms": f"{origin}/llms.txt",
        "llms_full": f"{origin}/llms-full.txt",
        "sitemap": f"{origin}/sitemap.xml",
    }

    aux_results: dict[str, Any] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        futs = {k: pool.submit(fetch_url, u, 5.0, 200_000) for k, u in aux_urls.items()}
        f_spf = pool.submit(query_dns_txt, root_domain, 4.0)
        f_dmarc = pool.submit(query_dns_txt, f"_dmarc.{root_domain}", 4.0)
        for k, f in futs.items():
            aux_results[k] = f.result()
        spf_txt = [r for r in f_spf.result() if "v=spf1" in r.lower()]
        dmarc_txt = [r for r in f_dmarc.result() if "v=dmarc1" in r.lower()]

    # Discover internal subpages for rich llms.txt & llms-full.txt synthesis
    seen_urls = {final_url.rstrip("/")}
    candidate_links: list[tuple[str, str]] = []
    for href, anchor in parser.links:
        p = urllib.parse.urlsplit(href)
        if p.netloc.lower() == parsed_final.netloc.lower() and p.scheme in ("http", "https"):
            clean_u = urllib.parse.urlunsplit((p.scheme, p.netloc, p.path, "", "")).rstrip("/")
            if clean_u and clean_u not in seen_urls:
                if not re.search(r"\.(png|jpg|jpeg|gif|svg|webp|pdf|zip|css|js|ico|woff2?)$", p.path, re.I):
                    seen_urls.add(clean_u)
                    candidate_links.append((clean_u, anchor or p.path))
        if len(candidate_links) >= crawl_subpages:
            break

    crawled_pages: list[dict[str, Any]] = [
        {
            "url": final_url,
            "title": parser.title or root_domain,
            "description": parser.meta.get("description") or parser.meta.get("og:description") or "",
            "headings": parser.headings[:10],
            "excerpt": " ".join(parser.text_chunks)[:900],
        }
    ]

    if candidate_links:
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            sub_futs = {pool.submit(fetch_url, u, 4.5, 180_000): (u, a) for u, a in candidate_links}
            for fut, (u, anchor) in sub_futs.items():
                r = fut.result()
                if r["ok"] and "html" in r["headers"].get("content-type", "text/html").lower():
                    sp = PageMetadataParser(u)
                    try:
                        sp.feed(r["text"])
                    except Exception:
                        pass
                    crawled_pages.append(
                        {
                            "url": u,
                            "title": sp.title or anchor or u,
                            "description": sp.meta.get("description") or sp.meta.get("og:description") or "",
                            "headings": sp.headings[:8],
                            "excerpt": " ".join(sp.text_chunks)[:700],
                        }
                    )

    checks: list[CheckItem] = []

    # 1. /llms.txt (15 pts)
    llms_r = aux_results["llms"]
    llms_text = llms_r["text"].strip() if llms_r["ok"] and llms_r["status"] == 200 else ""
    llms_looks_html = bool(re.match(r"^\s*<!doctype\s+html|^\s*<html", llms_text, re.I))
    if llms_text and not llms_looks_html and len(llms_text) >= 60 and "#" in llms_text:
        checks.append(CheckItem("llms_txt", "AI Search (GEO)", "/llms.txt index published", "pass", 15, 15,
                                f"Found valid /llms.txt ({len(llms_text)} chars).", "Keep /llms.txt synced on deploy."))
    elif llms_text and not llms_looks_html:
        checks.append(CheckItem("llms_txt", "AI Search (GEO)", "/llms.txt index published", "warn", 7, 15,
                                f"/llms.txt exists ({len(llms_text)} chars) but lacks standard Markdown H1/section links.",
                                "Deploy spec-compliant public/llms.txt from Fix Pack."))
    else:
        checks.append(CheckItem("llms_txt", "AI Search (GEO)", "/llms.txt index published", "fail", 0, 15,
                                f"Missing /llms.txt (HTTP {llms_r['status'] or 'ERR'} or HTML fallback).",
                                "Drop generated public/llms.txt into your web root."))

    # 2. /llms-full.txt (10 pts)
    llms_full_r = aux_results["llms_full"]
    llms_full_text = llms_full_r["text"].strip() if llms_full_r["ok"] and llms_full_r["status"] == 200 else ""
    llms_full_html = bool(re.match(r"^\s*<!doctype\s+html|^\s*<html", llms_full_text, re.I))
    if llms_full_text and not llms_full_html and len(llms_full_text) >= 150:
        checks.append(CheckItem("llms_full_txt", "AI Search (GEO)", "/llms-full.txt deep context", "pass", 10, 10,
                                f"Found /llms-full.txt ({len(llms_full_text)} chars).", "Maintain full Markdown digest."))
    else:
        checks.append(CheckItem("llms_full_txt", "AI Search (GEO)", "/llms-full.txt deep context", "fail", 0, 10,
                                "Missing /llms-full.txt full-context corpus for RAG & AI agents.",
                                "Deploy generated public/llms-full.txt so LLMs ingest accurate product details."))

    # 3. robots.txt AI crawler rules (10 pts)
    robots_r = aux_results["robots"]
    robots_text = robots_r["text"] if robots_r["ok"] and robots_r["status"] == 200 and "<html" not in robots_r["text"][:200].lower() else ""
    if robots_text:
        rb = analyze_robots_txt(robots_text)
        if rb["wildcard_disallow_all"] or rb["blocked_bots"]:
            blocked_str = ", ".join(rb["blocked_bots"]) or "All crawlers (*)"
            checks.append(CheckItem("ai_robots", "AI Search (GEO)", "AI search citation bots allowed", "fail", 0, 10,
                                    f"robots.txt blocks: {blocked_str}.",
                                    "Update public/robots.txt to allow OAI-SearchBot, PerplexityBot, and ClaudeBot."))
        elif rb["explicitly_mentions_ai"]:
            checks.append(CheckItem("ai_robots", "AI Search (GEO)", "AI search citation bots allowed", "pass", 10, 10,
                                    "robots.txt explicitly configures AI search crawlers without blocking citations.",
                                    "No change needed."))
        else:
            checks.append(CheckItem("ai_robots", "AI Search (GEO)", "AI search citation bots allowed", "warn", 6, 10,
                                    "robots.txt allows default crawling but lacks explicit AI SearchBot rules & llms.txt pointer.",
                                    "Replace or merge public/robots.txt with explicit AI citation rules."))
    else:
        checks.append(CheckItem("ai_robots", "AI Search (GEO)", "AI search citation bots allowed", "fail", 0, 10,
                                "No valid /robots.txt found.", "Deploy generated public/robots.txt with Sitemap & AI SearchBot directives."))

    # 4. sitemap.xml (10 pts)
    sm_r = aux_results["sitemap"]
    sm_ok = sm_r["ok"] and sm_r["status"] == 200 and ("<urlset" in sm_r["text"] or "<sitemapindex" in sm_r["text"])
    if sm_ok or "sitemap:" in robots_text.lower():
        checks.append(CheckItem("sitemap", "AI Search (GEO)", "XML Sitemap discoverable", "pass", 10, 10,
                                "XML Sitemap reachable for search & AI indexers.", "Keep sitemap updated."))
    else:
        checks.append(CheckItem("sitemap", "AI Search (GEO)", "XML Sitemap discoverable", "fail", 0, 10,
                                f"/sitemap.xml missing or invalid (HTTP {sm_r['status'] or 'ERR'}).",
                                "Expose /sitemap.xml and reference it in robots.txt."))

    # 5. Schema.org JSON-LD (12 pts)
    valid_schemas: list[str] = []
    for raw_ld in parser.json_ld_raw:
        try:
            parsed_ld = json.loads(raw_ld)
            items = parsed_ld if isinstance(parsed_ld, list) else [parsed_ld]
            for it in items:
                if isinstance(it, dict):
                    t = it.get("@type") or "Thing"
                    valid_schemas.append(str(t))
        except Exception:
            pass
    if valid_schemas:
        checks.append(CheckItem("json_ld", "Search & Conversion", "Schema.org JSON-LD structured data", "pass", 12, 12,
                                f"Valid JSON-LD types: {', '.join(valid_schemas[:4])}.", "Keep structured data synced."))
    elif parser.json_ld_raw:
        checks.append(CheckItem("json_ld", "Search & Conversion", "Schema.org JSON-LD structured data", "warn", 4, 12,
                                "Found <script type='application/ld+json'> with syntax errors.",
                                "Replace broken block with validated snippets/schema-jsonld.html."))
    else:
        checks.append(CheckItem("json_ld", "Search & Conversion", "Schema.org JSON-LD structured data", "fail", 0, 12,
                                "Zero Schema.org JSON-LD structured data on homepage.",
                                "Paste snippets/schema-jsonld.html into your <head> template."))

    # 6. OpenGraph & Social Preview tags (10 pts)
    og_present = [k for k in ("og:title", "og:description", "og:image") if parser.meta.get(k)]
    if len(og_present) == 3:
        checks.append(CheckItem("opengraph", "Search & Conversion", "OpenGraph social conversion cards", "pass", 10, 10,
                                "og:title, og:description, and og:image all configured.", "No action needed."))
    elif og_present:
        missing_og = [k for k in ("og:title", "og:description", "og:image") if k not in og_present]
        checks.append(CheckItem("opengraph", "Search & Conversion", "OpenGraph social conversion cards", "warn", 5, 10,
                                f"Missing OpenGraph tags: {', '.join(missing_og)}.",
                                "Add missing OpenGraph & twitter:card meta tags from snippets/schema-jsonld.html."))
    else:
        checks.append(CheckItem("opengraph", "Search & Conversion", "OpenGraph social conversion cards", "fail", 0, 10,
                                "No OpenGraph tags found; shared links render blank previews on Slack/X/LinkedIn.",
                                "Include OpenGraph meta block from snippets/schema-jsonld.html."))

    # 7. Title, Meta Description & Canonical (8 pts)
    has_title = bool(parser.title and 10 <= len(parser.title) <= 85)
    desc = parser.meta.get("description", "")
    has_desc = bool(desc and len(desc) >= 40)
    has_canon = bool(parser.canonical)
    pts_meta = (3 if has_title else 1 if parser.title else 0) + (3 if has_desc else 0) + (2 if has_canon else 0)
    status_meta = "pass" if pts_meta == 8 else ("warn" if pts_meta >= 4 else "fail")
    issues_meta = []
    if not has_title:
        issues_meta.append("title missing/suboptimal length")
    if not has_desc:
        issues_meta.append("meta description missing/<40 chars")
    if not has_canon:
        issues_meta.append("canonical link missing")
    checks.append(CheckItem(
        "core_meta", "Search & Conversion", "Title, meta description & canonical URL", status_meta, pts_meta, 8,
        "All core SEO tags valid." if not issues_meta else "Issues: " + "; ".join(issues_meta) + ".",
        "Apply canonical & meta tags in snippets/schema-jsonld.html."
    ))

    # 8. HTTPS + HSTS (7 pts)
    hdrs = home_resp["headers"]
    is_https = parsed_final.scheme == "https"
    hsts = hdrs.get("strict-transport-security", "")
    if is_https and "max-age=" in hsts.lower():
        checks.append(CheckItem("hsts", "Security & Deliverability", "HTTPS + Strict-Transport-Security", "pass", 7, 7,
                                f"HTTPS active with HSTS ({hsts[:48]}).", "No action needed."))
    elif is_https:
        checks.append(CheckItem("hsts", "Security & Deliverability", "HTTPS + Strict-Transport-Security", "warn", 3, 7,
                                "HTTPS active, but Strict-Transport-Security (HSTS) header is missing.",
                                "Deploy configs/vercel.json, configs/_headers, or nginx-security.conf."))
    else:
        checks.append(CheckItem("hsts", "Security & Deliverability", "HTTPS + Strict-Transport-Security", "fail", 0, 7,
                                "Site did not enforce HTTPS + HSTS.", "Enable HTTPS redirect + HSTS header."))

    # 9. Browser Security Headers (8 pts)
    sec_present = []
    sec_missing = []
    for h_key, label in [
        ("content-security-policy", "CSP"),
        ("x-content-type-options", "X-Content-Type-Options"),
        ("x-frame-options", "X-Frame-Options"),
        ("referrer-policy", "Referrer-Policy"),
    ]:
        if hdrs.get(h_key) or (h_key == "x-frame-options" and "frame-ancestors" in hdrs.get("content-security-policy", "")):
            sec_present.append(label)
        else:
            sec_missing.append(label)
    pts_sec = len(sec_present) * 2
    st_sec = "pass" if pts_sec == 8 else ("warn" if pts_sec >= 4 else "fail")
    checks.append(CheckItem(
        "sec_headers", "Security & Deliverability", "Hardened HTTP security headers", st_sec, pts_sec, 8,
        "All 4 core headers active." if not sec_missing else f"Missing headers: {', '.join(sec_missing)}.",
        "Drop in configs/vercel.json or configs/_headers from Fix Pack."
    ))

    # 10. SPF DNS Record (5 pts)
    if spf_txt:
        spf_val = spf_txt[0]
        strict_spf = "-all" in spf_val or "~all" in spf_val
        checks.append(CheckItem(
            "spf", "Security & Deliverability", "SPF email authentication record",
            "pass" if strict_spf else "warn", 5 if strict_spf else 3, 5,
            f"Found SPF on {root_domain}: {spf_val[:70]}",
            "Ensure SPF ends with ~all or -all."
        ))
    else:
        checks.append(CheckItem(
            "spf", "Security & Deliverability", "SPF email authentication record", "fail", 0, 5,
            f"No v=spf1 TXT record found on {root_domain}; outbound emails risk spam filtering.",
            "Add the TXT record in dns/email-deliverability-records.txt."
        ))

    # 11. DMARC Policy (5 pts)
    if dmarc_txt:
        dm_val = dmarc_txt[0]
        enforced = bool(re.search(r"p\s*=\s*(quarantine|reject)", dm_val, re.I))
        checks.append(CheckItem(
            "dmarc", "Security & Deliverability", "DMARC anti-spoofing & inbox placement",
            "pass" if enforced else "warn", 5 if enforced else 2, 5,
            f"Found DMARC on _dmarc.{root_domain}: {dm_val[:70]}" + ("" if enforced else " (p=none offers zero spoofing protection)"),
            "Upgrade DMARC policy to p=quarantine in dns/email-deliverability-records.txt."
        ))
    else:
        checks.append(CheckItem(
            "dmarc", "Security & Deliverability", "DMARC anti-spoofing & inbox placement", "fail", 0, 5,
            f"No _dmarc.{root_domain} TXT record; Gmail/Yahoo bulk-sender rules flag unauthenticated domains.",
            "Publish the _dmarc TXT record in dns/email-deliverability-records.txt."
        ))

    total_score = sum(c.points for c in checks)
    site_title = parser.title or parser.meta.get("og:title") or root_domain
    site_desc = (
        parser.meta.get("description")
        or parser.meta.get("og:description")
        or (crawled_pages[0]["excerpt"][:160] if crawled_pages and crawled_pages[0]["excerpt"] else f"Official website for {root_domain}.")
    )

    return AuditResult(
        target_url=target_url,
        final_url=final_url,
        domain=domain,
        root_domain=root_domain,
        timestamp_utc=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        score=total_score,
        grade=_grade_for_score(total_score),
        response_ms=home_resp["elapsed_ms"],
        site_title=site_title,
        site_description=site_desc,
        checks=checks,
        crawled_pages=crawled_pages,
        existing_robots=robots_text,
        spf_records=spf_txt,
        dmarc_records=dmarc_txt,
    )


def generate_fix_files(result: AuditResult) -> dict[str, str]:
    """Synthesize domain-tailored drop-in deployment files from live crawled site data."""
    parsed = urllib.parse.urlsplit(result.final_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"

    # 1. public/llms.txt (llmstxt.org standard)
    llms_lines = [
        f"# {result.site_title}",
        "",
        f"> {result.site_description}",
        "",
        f"Canonical website: {origin}",
        f"Full LLM context digest: {origin}/llms-full.txt",
        "",
        "## Key Pages",
    ]
    for pg in result.crawled_pages:
        desc_suffix = f": {pg['description'][:140]}" if pg.get("description") else ""
        llms_lines.append(f"- [{pg['title']}]({pg['url']}){desc_suffix}")

    if result.crawled_pages and result.crawled_pages[0].get("headings"):
        llms_lines.extend(["", "## Core Topics Covered"])
        for tag, htxt in result.crawled_pages[0]["headings"][:8]:
            llms_lines.append(f"- {htxt}")

    llms_txt = "\n".join(llms_lines) + "\n"

    # 2. public/llms-full.txt
    full_lines = [
        f"# {result.site_title} — Complete AI & RAG Reference Corpus",
        "",
        f"> {result.site_description}",
        "",
        f"Source Domain: {result.root_domain}",
        f"Generated: {result.timestamp_utc}",
        "",
    ]
    for idx, pg in enumerate(result.crawled_pages, 1):
        full_lines.append(f"---")
        full_lines.append(f"## {idx}. {pg['title']}")
        full_lines.append(f"URL: {pg['url']}")
        if pg.get("description"):
            full_lines.append(f"Summary: {pg['description']}")
        if pg.get("headings"):
            full_lines.append("Outline: " + " | ".join(h for _, h in pg["headings"][:6]))
        if pg.get("excerpt"):
            full_lines.append("")
            full_lines.append(pg["excerpt"])
        full_lines.append("")
    llms_full_txt = "\n".join(full_lines)

    # 3. public/robots.txt
    robots_lines = [
        f"# Optimized robots.txt for {result.root_domain} (Search + AI Citation Ready)",
        "User-agent: *",
        "Allow: /",
        "",
        "# Explicitly welcome AI Answer Engines so your brand gets cited with links",
    ]
    for bot in AI_BOTS:
        robots_lines.append(f"User-agent: {bot}")
        robots_lines.append("Allow: /")
        robots_lines.append("")
    robots_lines.append(f"Sitemap: {origin}/sitemap.xml")
    robots_lines.append(f"# LLM Knowledge Index: {origin}/llms.txt")
    robots_txt = "\n".join(robots_lines) + "\n"

    # 4. snippets/schema-jsonld.html
    schema_obj = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{origin}/#organization",
                "name": result.site_title.split("|")[0].split("—")[0].split("-")[0].strip() or result.root_domain,
                "url": origin,
                "description": result.site_description,
            },
            {
                "@type": "WebSite",
                "@id": f"{origin}/#website",
                "url": origin,
                "name": result.site_title,
                "description": result.site_description,
                "publisher": {"@id": f"{origin}/#organization"},
            },
        ],
    }
    escaped_title = html.escape(result.site_title, quote=True)
    escaped_desc = html.escape(result.site_description, quote=True)
    schema_html = (
        f"<!-- Drop into <head> of {result.root_domain} -->\n"
        f'<link rel="canonical" href="{html.escape(result.final_url, quote=True)}" />\n'
        f'<meta name="description" content="{escaped_desc}" />\n'
        f'<meta property="og:type" content="website" />\n'
        f'<meta property="og:url" content="{html.escape(result.final_url, quote=True)}" />\n'
        f'<meta property="og:title" content="{escaped_title}" />\n'
        f'<meta property="og:description" content="{escaped_desc}" />\n'
        f'<meta property="og:image" content="{origin}/og-image.png" />\n'
        f'<meta name="twitter:card" content="summary_large_image" />\n'
        f'<meta name="twitter:title" content="{escaped_title}" />\n'
        f'<meta name="twitter:description" content="{escaped_desc}" />\n'
        f'<script type="application/ld+json">\n'
        f"{json.dumps(schema_obj, indent=2)}\n"
        f"</script>\n"
    )

    # 5. Security header configs (Vercel, Cloudflare/Netlify _headers, Nginx)
    sec_headers_list = [
        {"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"},
        {"key": "X-Content-Type-Options", "value": "nosniff"},
        {"key": "X-Frame-Options", "value": "SAMEORIGIN"},
        {"key": "Referrer-Policy", "value": "strict-origin-when-cross-origin"},
        {"key": "Permissions-Policy", "value": "camera=(), microphone=(), geolocation=()"},
        {"key": "Content-Security-Policy", "value": "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'; frame-ancestors 'self'; upgrade-insecure-requests"},
    ]
    vercel_json = json.dumps({"headers": [{"source": "/(.*)", "headers": sec_headers_list}]}, indent=2) + "\n"
    cf_headers = "/*\n" + "".join(f"  {h['key']}: {h['value']}\n" for h in sec_headers_list)
    nginx_conf = (
        f"# Security headers for {result.root_domain}\n"
        + "".join(f'add_header {h["key"]} "{h["value"]}" always;\n' for h in sec_headers_list)
    )

    # 6. DNS TXT records for SPF + DMARC
    dns_txt = (
        f"# Email Deliverability & Anti-Spoofing DNS Patch for {result.root_domain}\n"
        f"# Add these TXT records in Cloudflare / Route53 / Namecheap DNS:\n\n"
        f"1) SPF Record (only if you do not already have v=spf1 on {result.root_domain}):\n"
        f"   Type:  TXT\n"
        f"   Host:  @\n"
        f'   Value: "v=spf1 include:_spf.google.com ~all"\n'
        f"   (Replace/append your ESP e.g. include:sendgrid.net or include:amazonses.com)\n\n"
        f"2) DMARC Enforcement Record (Required by Gmail/Yahoo bulk-sender policies):\n"
        f"   Type:  TXT\n"
        f"   Host:  _dmarc\n"
        f'   Value: "v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@{result.root_domain}; adkim=r; aspf=r"\n'
    )

    # 7. Executive Audit Report & 5-Minute Deployment Checklist
    report_lines = [
        f"# CiteReady Audit & Fix Pack — `{result.root_domain}`",
        "",
        f"- **Audited URL:** {result.final_url}",
        f"- **Timestamp:** {result.timestamp_utc}",
        f"- **Baseline Score:** **{result.score}/100 (Grade {result.grade})**",
        f"- **Target Score After Deploying This Pack:** **95–100/100 (Grade A)**",
        "",
        "## Diagnostic Breakdown",
        "",
        "| Status | Category | Check | Score | Evidence |",
        "|---|---|---|---|---|",
    ]
    icon_map = {"pass": "PASS", "warn": "WARN", "fail": "FAIL"}
    for c in result.checks:
        ev = c.evidence.replace("|", "\\|")
        report_lines.append(f"| **{icon_map.get(c.status, c.status)}** | {c.category} | {c.title} | {c.points}/{c.max_points} | {ev} |")

    report_lines.extend([
        "",
        "## 5-Minute Deployment Checklist",
        "",
        "1. **Publish AI Search Index (`+25 pts`):** Copy `public/llms.txt` and `public/llms-full.txt` into your static `public/` root so they resolve at `/llms.txt` and `/llms-full.txt`.",
        "2. **Unblock AI Citation Bots (`+10 pts`):** Merge `public/robots.txt` into your root `/robots.txt`.",
        "3. **Inject Rich Structured Data (`+22 pts`):** Add `snippets/schema-jsonld.html` inside `<head>` on your homepage layout.",
        "4. **Harden Security Headers (`+15 pts`):** Apply `configs/vercel.json` (Vercel), `configs/_headers` (Cloudflare Pages / Netlify), or `configs/nginx-security.conf` (Nginx).",
        "5. **Lock Email Deliverability (`+10 pts`):** Add the `SPF` and `_dmarc` TXT records in `dns/email-deliverability-records.txt`.",
        "",
    ])

    return {
        "public/llms.txt": llms_txt,
        "public/llms-full.txt": llms_full_txt,
        "public/robots.txt": robots_txt,
        "snippets/schema-jsonld.html": schema_html,
        "configs/vercel.json": vercel_json,
        "configs/_headers": cf_headers,
        "configs/nginx-security.conf": nginx_conf,
        "dns/email-deliverability-records.txt": dns_txt,
        "AUDIT_REPORT.md": "\n".join(report_lines),
    }


def build_fix_pack_zip(result: AuditResult) -> bytes:
    """Create an in-memory ZIP archive containing all tailored drop-in fix files."""
    files = generate_fix_files(result)
    buf = io.BytesIO()
    folder = f"{result.root_domain.replace('.', '-')}-citeready-fixpack"
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for rel_path, content in files.items():
            zf.writestr(f"{folder}/{rel_path}", content.encode("utf-8"))
    return buf.getvalue()
