const UI_HTML = "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\" />\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />\n  <title>CiteReady \u2014 Instant AI Search (llms.txt), Schema &amp; DMARC Fixer</title>\n  <meta name=\"description\" content=\"Scan any domain in 3 seconds for ChatGPT/Claude/Perplexity visibility, Schema.org JSON-LD, HTTP security headers, and SPF/DMARC email deliverability. Download a tailored drop-in Fix Pack.\" />\n  <link rel=\"canonical\" href=\"https://citeready.romanfjose.workers.dev/\" />\n  <meta property=\"og:type\" content=\"website\" />\n  <meta property=\"og:url\" content=\"https://citeready.romanfjose.workers.dev/\" />\n  <meta property=\"og:title\" content=\"CiteReady \u2014 Instant AI Search (llms.txt), Schema &amp; DMARC Site Fixer\" />\n  <meta property=\"og:description\" content=\"Free 3-second live HTTP + DNS scanner for /llms.txt, Schema JSON-LD, security headers, and SPF/DMARC \u2014 plus tailored 9-file drop-in Fix Packs.\" />\n  <meta property=\"og:image\" content=\"https://citeready.romanfjose.workers.dev/og-image.svg\" />\n  <meta name=\"twitter:card\" content=\"summary_large_image\" />\n  <script type=\"application/ld+json\">\n  {\n    \"@context\": \"https://schema.org\",\n    \"@type\": \"SoftwareApplication\",\n    \"name\": \"CiteReady\",\n    \"applicationCategory\": \"DeveloperApplication\",\n    \"operatingSystem\": \"Web, Windows, macOS, Linux\",\n    \"url\": \"https://citeready.romanfjose.workers.dev/\",\n    \"description\": \"Instant AI Search (GEO / llms.txt), Schema.org JSON-LD, HTTP Security Header, and SPF/DMARC Deliverability Auditor & Drop-In Fix Pack Generator.\",\n    \"offers\": { \"@type\": \"Offer\", \"price\": \"29.00\", \"priceCurrency\": \"USD\" }\n  }\n  </script>\n  <style>\n    :root {\n      --bg: #090d16;\n      --panel: #111827;\n      --panel-2: #172033;\n      --border: #24324b;\n      --text: #f3f6fc;\n      --muted: #94a3b8;\n      --accent: #38bdf8;\n      --accent-2: #22c55e;\n      --warn: #f59e0b;\n      --danger: #ef4444;\n    }\n    * { box-sizing: border-box; }\n    body {\n      margin: 0;\n      font-family: Inter, -apple-system, BlinkMacSystemFont, \"Segoe UI\", Roboto, sans-serif;\n      background: radial-gradient(circle at 50% 0%, #13203a 0%, var(--bg) 55%);\n      color: var(--text);\n      line-height: 1.55;\n    }\n    .wrap { max-width: 1020px; margin: 0 auto; padding: 32px 20px 80px; }\n    .topbar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 36px; }\n    .brand { font-weight: 800; font-size: 1.2rem; letter-spacing: -0.02em; display: flex; align-items: center; gap: 10px; }\n    .badge { font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 999px; background: rgba(56,189,248,0.14); color: var(--accent); border: 1px solid rgba(56,189,248,0.35); }\n    .hero { text-align: center; max-width: 760px; margin: 0 auto 32px; }\n    h1 { font-size: clamp(1.9rem, 4vw, 2.85rem); line-height: 1.13; margin: 0 0 14px; letter-spacing: -0.03em; }\n    .sub { color: var(--muted); font-size: 1.06rem; margin: 0 auto 26px; }\n    .scan-box {\n      display: flex; gap: 10px; background: var(--panel); padding: 8px; border-radius: 14px;\n      border: 1px solid var(--border); box-shadow: 0 18px 45px rgba(0,0,0,0.4);\n    }\n    .scan-box input {\n      flex: 1; background: transparent; border: none; color: var(--text); font-size: 1.02rem;\n      padding: 12px 14px; outline: none;\n    }\n    .btn {\n      cursor: pointer; border: none; border-radius: 10px; font-weight: 700; font-size: 0.96rem;\n      padding: 12px 22px; transition: transform 0.12s ease, opacity 0.15s ease;\n    }\n    .btn:hover { opacity: 0.94; transform: translateY(-1px); }\n    .btn:disabled { opacity: 0.55; cursor: wait; transform: none; }\n    .btn-primary { background: linear-gradient(135deg, #38bdf8, #2563eb); color: #fff; }\n    .btn-green { background: linear-gradient(135deg, #22c55e, #16a34a); color: #052e16; font-weight: 800; }\n    .btn-outline { background: var(--panel-2); color: var(--text); border: 1px solid var(--border); text-decoration: none; display: inline-flex; align-items: center; justify-content: center; }\n    .trust-row { display: flex; justify-content: center; gap: 22px; flex-wrap: wrap; margin-top: 14px; font-size: 0.83rem; color: var(--muted); }\n    .card { background: var(--panel); border: 1px solid var(--border); border-radius: 16px; padding: 24px; margin-top: 24px; }\n    .score-grid { display: grid; grid-template-columns: 180px 1fr; gap: 24px; align-items: center; }\n    @media (max-width: 680px) {\n      .scan-box { flex-direction: column; }\n      .score-grid { grid-template-columns: 1fr; text-align: center; }\n    }\n    .ring {\n      width: 152px; height: 152px; border-radius: 50%; margin: 0 auto;\n      display: flex; flex-direction: column; align-items: center; justify-content: center;\n      border: 8px solid var(--border); background: var(--panel-2);\n    }\n    .ring .num { font-size: 2.6rem; font-weight: 800; line-height: 1; }\n    .ring .grd { font-size: 0.85rem; color: var(--muted); margin-top: 4px; font-weight: 700; }\n    .checks-list { display: grid; gap: 10px; margin-top: 18px; }\n    .check-row {\n      display: grid; grid-template-columns: 78px 1fr auto; gap: 12px; align-items: center;\n      background: var(--panel-2); border: 1px solid var(--border); border-radius: 10px; padding: 12px 14px;\n    }\n    .pill { font-size: 0.74rem; font-weight: 800; text-align: center; padding: 4px 8px; border-radius: 6px; text-transform: uppercase; }\n    .pill.pass { background: rgba(34,197,94,0.16); color: #4ade80; }\n    .pill.warn { background: rgba(245,158,11,0.16); color: #fbbf24; }\n    .pill.fail { background: rgba(239,68,68,0.18); color: #f87171; }\n    .pts { font-family: ui-monospace, SFMono-Regular, Consolas, monospace; font-size: 0.85rem; color: var(--muted); }\n    pre.preview {\n      background: #070b12; border: 1px solid var(--border); border-radius: 10px; padding: 14px;\n      overflow-x: auto; font-size: 0.82rem; color: #cbd5e1; margin: 10px 0 0; position: relative;\n    }\n    .paywall-box {\n      background: linear-gradient(160deg, rgba(37,99,235,0.16), rgba(34,197,94,0.11));\n      border: 1px solid rgba(56,189,248,0.45); border-radius: 16px; padding: 24px; margin-top: 24px;\n    }\n    .tier-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }\n    @media (max-width: 720px) { .tier-grid { grid-template-columns: 1fr; } }\n    .tier { background: rgba(9,13,22,0.78); border: 1px solid var(--border); border-radius: 12px; padding: 18px; display: flex; flex-direction: column; justify-content: space-between; }\n    .price { font-size: 1.85rem; font-weight: 800; margin: 6px 0; }\n    .unlock-bar { display: flex; gap: 10px; margin-top: 18px; flex-wrap: wrap; }\n    .unlock-bar input {\n      flex: 1; min-width: 230px; background: #090d16; border: 1px solid var(--border);\n      border-radius: 10px; color: var(--text); padding: 11px 14px; font-size: 0.94rem;\n    }\n    .err { color: #f87171; font-size: 0.9rem; margin-top: 10px; }\n    .hidden { display: none; }\n  </style>\n</head>\n<body>\n  <div class=\"wrap\">\n    <div class=\"topbar\">\n      <div class=\"brand\">\u26a1 CiteReady <span class=\"badge\">GEO + SECURITY + DMARC ENGINE</span></div>\n      <div style=\"font-size:0.86rem;color:var(--muted);\">Zero-Signup Live Scanner</div>\n    </div>\n\n    <div class=\"hero\">\n      <h1>Make Your Website Cited by AI Search &amp; Trusted by Inboxes in 5 Minutes</h1>\n      <p class=\"sub\">87% of SaaS &amp; e-commerce sites silently block AI citation crawlers, lack <code>/llms.txt</code> + <code>JSON-LD</code>, or fail Gmail DMARC rules. Scan your live URL and get a tailored, drop-in Fix Pack.</p>\n\n      <form id=\"scanForm\" class=\"scan-box\">\n        <input id=\"urlInput\" type=\"text\" placeholder=\"Enter your domain (e.g. yourstartup.com)\" required />\n        <button id=\"scanBtn\" type=\"submit\" class=\"btn btn-primary\">Run Free 11-Point Audit \u2192</button>\n      </form>\n      <div class=\"trust-row\">\n        <span>\u2713 Live HTTP + DNS TXT inspection</span>\n        <span>\u2713 Auto-builds <code>llms.txt</code> &amp; <code>llms-full.txt</code></span>\n        <span>\u2713 Ready-to-drop Vercel / Cloudflare / Nginx &amp; DMARC patches</span>\n      </div>\n      <div style=\"margin-top:10px;font-size:0.82rem;color:var(--muted);\">\n        Try live scan:\n        <a href=\"?url=citeready.romanfjose.workers.dev\" style=\"color:var(--accent);text-decoration:none;margin:0 6px;\">citeready (Grade A)</a> \u2022\n        <a href=\"?url=news.ycombinator.com\" style=\"color:var(--accent);text-decoration:none;margin:0 6px;\">news.ycombinator.com</a> \u2022\n        <a href=\"?url=example.com\" style=\"color:var(--accent);text-decoration:none;margin:0 6px;\">example.com</a>\n      </div>\n      <div id=\"errBox\" class=\"err hidden\"></div>\n    </div>\n\n    <div id=\"resultSection\" class=\"hidden\">\n      <div class=\"card\">\n        <div class=\"score-grid\">\n          <div id=\"scoreRing\" class=\"ring\">\n            <div id=\"scoreNum\" class=\"num\">--</div>\n            <div id=\"scoreGrade\" class=\"grd\">GRADE -</div>\n          </div>\n          <div>\n            <div style=\"font-size:0.84rem;color:var(--accent);font-weight:700;text-transform:uppercase;\" id=\"resDomain\"></div>\n            <h2 style=\"margin:4px 0 8px;font-size:1.45rem;\" id=\"resTitle\"></h2>\n            <p style=\"margin:0;color:var(--muted);font-size:0.95rem;\" id=\"resSummary\"></p>\n          </div>\n        </div>\n\n        <div id=\"checksContainer\" class=\"checks-list\"></div>\n      </div>\n\n      <div class=\"card\">\n        <h3 style=\"margin:0 0 6px;\">Tailored Fix-Pack Preview (Compiled from Your Live Pages)</h3>\n        <p style=\"margin:0 0 12px;color:var(--muted);font-size:0.9rem;\">Below is a live excerpt of the 9 custom files generated for your domain:</p>\n        <div style=\"font-size:0.8rem;font-weight:700;color:var(--accent);margin-top:8px;\">public/llms.txt (Preview)</div>\n        <pre id=\"llmsPreview\" class=\"preview\"></pre>\n        <div style=\"font-size:0.8rem;font-weight:700;color:var(--accent);margin-top:14px;\">snippets/schema-jsonld.html (Preview)</div>\n        <pre id=\"schemaPreview\" class=\"preview\"></pre>\n      </div>\n\n      <div class=\"paywall-box\">\n        <h3 style=\"margin:0 0 6px;font-size:1.35rem;\">Unlock Your Complete 9-File Drop-In Fix Pack + Pro CLI</h3>\n        <p style=\"margin:0;color:var(--muted);font-size:0.94rem;\">Includes full <code>public/llms.txt</code>, <code>public/llms-full.txt</code>, AI-ready <code>robots.txt</code>, <code>schema-jsonld.html</code>, <code>vercel.json</code> / Cloudflare <code>_headers</code> / <code>nginx.conf</code>, <code>SPF + DMARC</code> DNS records, and the offline Python CLI &amp; Batch Agency Scanner.</p>\n\n        <div class=\"tier\" style=\"margin-top:16px;\">\n          <div style=\"display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:16px;\">\n            <div>\n              <div style=\"font-weight:700;color:var(--accent);font-size:0.82rem;\">COMPLETE PRO FIX-PACK + UNLIMITED CLI LICENSE</div>\n              <div class=\"price\">$29 <span style=\"font-size:0.88rem;font-weight:400;color:var(--muted);\">one-time \u2022 instant license key</span></div>\n              <div style=\"color:var(--muted);font-size:0.88rem;\">\u2713 Instant 9-file ZIP for any audited domain &nbsp;\u2022&nbsp; \u2713 Offline Pro CLI + Batch Agency Mode &nbsp;\u2022&nbsp; \u2713 GitHub CI Action</div>\n            </div>\n            <a id=\"buySingleBtn\" href=\"__SINGLE_CHECKOUT_URL__\" target=\"_blank\" rel=\"noopener\" class=\"btn btn-green\" style=\"text-decoration:none;text-align:center;padding:14px 26px;font-size:1.02rem;\">Get Instant Access + License Key ($29) \u2192</a>\n          </div>\n        </div>\n\n        <div class=\"unlock-bar\">\n          <input id=\"licenseInput\" type=\"text\" placeholder=\"Already purchased? Paste your Gumroad License Key to download ZIP...\" />\n          <button id=\"unlockBtn\" type=\"button\" class=\"btn btn-primary\">Verify &amp; Download Fix-Pack ZIP</button>\n        </div>\n        <div id=\"unlockMsg\" class=\"err hidden\"></div>\n      </div>\n    </div>\n  </div>\n\n  <script>\n    const API_BASE = window.CITEREADY_API_BASE || \"\";\n    let lastAuditedUrl = \"\";\n    const form = document.getElementById(\"scanForm\");\n    const urlInput = document.getElementById(\"urlInput\");\n    const scanBtn = document.getElementById(\"scanBtn\");\n    const errBox = document.getElementById(\"errBox\");\n    const resultSection = document.getElementById(\"resultSection\");\n\n    function colorForScore(s) {\n      if (s >= 80) return \"#22c55e\";\n      if (s >= 55) return \"#f59e0b\";\n      return \"#ef4444\";\n    }\n\n    async function runAudit(targetUrl) {\n      errBox.classList.add(\"hidden\");\n      scanBtn.disabled = true;\n      scanBtn.textContent = \"Auditing Live HTTP + DNS...\";\n      try {\n        const resp = await fetch(API_BASE + \"/api/audit?url=\" + encodeURIComponent(targetUrl));\n        const data = await resp.json();\n        if (!resp.ok || data.error) {\n          throw new Error(data.error || \"Audit failed\");\n        }\n        lastAuditedUrl = data.audit.final_url;\n        const sc = data.audit.score;\n        const ring = document.getElementById(\"scoreRing\");\n        ring.style.borderColor = colorForScore(sc);\n        document.getElementById(\"scoreNum\").textContent = sc;\n        document.getElementById(\"scoreGrade\").textContent = \"GRADE \" + data.audit.grade;\n        document.getElementById(\"resDomain\").textContent = data.audit.root_domain + \" \u2022 \" + data.audit.response_ms + \"ms\";\n        document.getElementById(\"resTitle\").textContent = data.audit.site_title;\n\n        const failed = data.audit.checks.filter(c => c.status !== \"pass\").length;\n        document.getElementById(\"resSummary\").textContent =\n          failed === 0\n            ? \"All 11 GEO, structured metadata, security, and email deliverability checks passed.\"\n            : failed + \" of 11 revenue & visibility checks need attention. Your custom drop-in Fix Pack is ready below.\";\n\n        const container = document.getElementById(\"checksContainer\");\n        container.innerHTML = \"\";\n        for (const c of data.audit.checks) {\n          const row = document.createElement(\"div\");\n          row.className = \"check-row\";\n          row.innerHTML = `\n            <span class=\"pill ${c.status}\">${c.status}</span>\n            <div>\n              <div style=\"font-weight:700;font-size:0.95rem;\">${escapeHtml(c.title)} <span style=\"color:var(--muted);font-weight:400;font-size:0.8rem;\">(${escapeHtml(c.category)})</span></div>\n              <div style=\"color:var(--muted);font-size:0.84rem;\">${escapeHtml(c.evidence)}</div>\n            </div>\n            <div class=\"pts\">${c.points}/${c.max_points}</div>\n          `;\n          container.appendChild(row);\n        }\n\n        document.getElementById(\"llmsPreview\").textContent = data.preview.llms_excerpt;\n        document.getElementById(\"schemaPreview\").textContent = data.preview.schema_excerpt;\n        resultSection.classList.remove(\"hidden\");\n        resultSection.scrollIntoView({ behavior: \"smooth\", block: \"start\" });\n      } catch (err) {\n        errBox.textContent = err.message || String(err);\n        errBox.classList.remove(\"hidden\");\n      } finally {\n        scanBtn.disabled = false;\n        scanBtn.textContent = \"Run Free 11-Point Audit \u2192\";\n      }\n    }\n\n    function escapeHtml(s) {\n      return String(s || \"\").replace(/[&<>\"']/g, ch => ({\"&\":\"&amp;\",\"<\":\"&lt;\",\">\":\"&gt;\",'\"':\"&quot;\",\"'\":\"&#39;\"}[ch]));\n    }\n\n    form.addEventListener(\"submit\", e => {\n      e.preventDefault();\n      if (urlInput.value.trim()) runAudit(urlInput.value.trim());\n    });\n\n    document.getElementById(\"unlockBtn\").addEventListener(\"click\", async () => {\n      const key = document.getElementById(\"licenseInput\").value.trim();\n      const msg = document.getElementById(\"unlockMsg\");\n      msg.classList.add(\"hidden\");\n      if (!key) {\n        msg.textContent = \"Please paste your Gumroad license key from your receipt.\";\n        msg.classList.remove(\"hidden\");\n        return;\n      }\n      if (!lastAuditedUrl) {\n        msg.textContent = \"Run a domain scan above first so we know which Fix-Pack ZIP to build.\";\n        msg.classList.remove(\"hidden\");\n        return;\n      }\n      const btn = document.getElementById(\"unlockBtn\");\n      btn.disabled = true;\n      btn.textContent = \"Verifying License...\";\n      try {\n        const resp = await fetch(API_BASE + \"/api/unlock\", {\n          method: \"POST\",\n          headers: { \"Content-Type\": \"application/json\" },\n          body: JSON.stringify({ url: lastAuditedUrl, license_key: key })\n        });\n        if (!resp.ok) {\n          const errData = await resp.json().catch(() => ({}));\n          throw new Error(errData.error || \"License verification failed.\");\n        }\n        const blob = await resp.blob();\n        const dlUrl = URL.createObjectURL(blob);\n        const a = document.createElement(\"a\");\n        a.href = dlUrl;\n        a.download = (new URL(lastAuditedUrl).hostname.replace(/^www\\./, \"\").replace(/\\./g, \"-\")) + \"-citeready-fixpack.zip\";\n        document.body.appendChild(a);\n        a.click();\n        a.remove();\n        URL.revokeObjectURL(dlUrl);\n      } catch (err) {\n        msg.textContent = err.message || String(err);\n        msg.classList.remove(\"hidden\");\n      } finally {\n        btn.disabled = false;\n        btn.textContent = \"Verify & Download Fix-Pack ZIP\";\n      }\n    });\n\n    // Auto-run if ?url= parameter is present (for personalized founder outreach links!)\n    const params = new URLSearchParams(window.location.search);\n    const prefill = params.get(\"url\");\n    if (prefill) {\n      urlInput.value = prefill;\n      runAudit(prefill);\n    }\n  </script>\n</body>\n</html>\n";

const AI_BOTS = ["OAI-SearchBot", "ChatGPT-User", "PerplexityBot", "ClaudeBot", "Claude-SearchBot", "Google-Extended"];
const UA = "Mozilla/5.0 (compatible; CiteReadyAudit/1.0; +https://citeready.dev)";

function isBlockedHost(hostname) {
  const h = (hostname || "").toLowerCase().trim();
  if (!h || !h.includes(".") || h === "localhost" || h.endsWith(".local") || h.endsWith(".internal")) return true;
  if (/^(127\.|10\.|192\.168\.|169\.254\.|0\.|172\.(1[6-9]|2\d|3[0-1])\.)/.test(h)) return true;
  if (h.startsWith("[") || h.includes(":")) return true;
  return false;
}

function normalizeUrl(raw) {
  let u = String(raw || "").trim();
  if (!/^https?:\/\//i.test(u)) u = "https://" + u;
  const parsed = new URL(u);
  if (!["http:", "https:"].includes(parsed.protocol)) throw new Error("Unsupported protocol");
  if (isBlockedHost(parsed.hostname)) throw new Error("Please enter a valid public domain name.");
  parsed.hash = "";
  return parsed.toString();
}

let SELF_FETCH_FN = null;
let SELF_HOST = "";

async function fetchSafe(url, timeoutMs = 6000) {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  const t0 = Date.now();
  try {
    let resp;
    const uParsed = new URL(url);
    if (SELF_FETCH_FN && SELF_HOST && uParsed.hostname.toLowerCase() === SELF_HOST) {
      resp = await SELF_FETCH_FN(new Request(url, { headers: { "User-Agent": UA } }));
    } else {
      resp = await fetch(url, {
        headers: { "User-Agent": UA, "Accept": "text/html,text/plain,application/xml,*/*" },
        redirect: "follow",
        signal: ctrl.signal,
      });
    }
    const text = (await resp.text()).slice(0, 300000);
    const headers = {};
    resp.headers.forEach((v, k) => { headers[k.toLowerCase()] = v; });
    return { ok: resp.ok, status: resp.status, finalUrl: resp.url || url, headers, text, ms: Date.now() - t0 };
  } catch (err) {
    return { ok: false, status: 0, finalUrl: url, headers: {}, text: "", ms: Date.now() - t0, error: String(err) };
  } finally {
    clearTimeout(timer);
  }
}

async function queryDnsTxt(hostname) {
  try {
    const u = `https://cloudflare-dns.com/dns-query?name=${encodeURIComponent(hostname)}&type=TXT`;
    const r = await fetch(u, { headers: { "Accept": "application/dns-json" } });
    const data = await r.json();
    return (data.Answer || [])
      .filter(a => a.type === 16 && a.data)
      .map(a => String(a.data).replace(/"\s*"/g, "").replace(/^"|"$/g, ""));
  } catch {
    return [];
  }
}

function cleanHtmlText(s) {
  return String(s || "")
    .replace(/<[^>]+>/g, " ")
    .replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&nbsp;/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function parseHtmlMeta(html, baseUrl) {
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const title = titleMatch ? cleanHtmlText(titleMatch[1]) : "";
  const meta = {};
  const metaRe = /<meta\s+[^>]*>/gi;
  let m;
  while ((m = metaRe.exec(html)) !== null) {
    const tag = m[0];
    const nameM = tag.match(/(?:name|property)\s*=\s*["']([^"']+)["']/i);
    const contM = tag.match(/content\s*=\s*["']([^"']*)["']/i);
    if (nameM && contM) {
      const k = nameM[1].toLowerCase().trim();
      if (!meta[k] && contM[1].trim()) meta[k] = cleanHtmlText(contM[1]);
    }
  }
  const canonM = html.match(/<link\s+[^>]*rel\s*=\s*["'][^"']*canonical[^"']*["'][^>]*>/i);
  let canonical = "";
  if (canonM) {
    const hrefM = canonM[0].match(/href\s*=\s*["']([^"']+)["']/i);
    if (hrefM) {
      try { canonical = new URL(hrefM[1], baseUrl).toString(); } catch {}
    }
  }
  const jsonLd = [];
  const ldRe = /<script[^>]*type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  while ((m = ldRe.exec(html)) !== null) {
    if (m[1].trim()) jsonLd.push(m[1].trim());
  }
  const headings = [];
  const hRe = /<(h[1-3])[^>]*>([\s\S]*?)<\/\1>/gi;
  while ((m = hRe.exec(html)) !== null && headings.length < 10) {
    const ht = cleanHtmlText(m[2]);
    if (ht) headings.push([m[1].toUpperCase(), ht]);
  }
  const bodyStrip = html.replace(/<(script|style|noscript|svg)[\s\S]*?<\/\1>/gi, " ");
  const excerpt = cleanHtmlText(bodyStrip).slice(0, 900);
  return { title, meta, canonical, jsonLd, headings, excerpt };
}

function gradeFor(score) {
  if (score >= 90) return "A";
  if (score >= 75) return "B";
  if (score >= 60) return "C";
  if (score >= 45) return "D";
  return "F";
}

async function auditDomain(rawUrl) {
  const targetUrl = normalizeUrl(rawUrl);
  const home = await fetchSafe(targetUrl, 7000);
  if (!home.ok && home.status === 0) throw new Error(`Unreachable host: ${home.error || targetUrl}`);
  const finalUrl = home.finalUrl || targetUrl;
  const uObj = new URL(finalUrl);
  const origin = uObj.origin;
  const rootDomain = uObj.hostname.toLowerCase().replace(/^www\./, "");

  const parts = rootDomain.split(".");
  const orgDomain = parts.length > 2 ? parts.slice(-2).join(".") : rootDomain;

  const [robotsR, llmsR, llmsFullR, sitemapR, spfHost, dmarcHost] = await Promise.all([
    fetchSafe(`${origin}/robots.txt`, 4500),
    fetchSafe(`${origin}/llms.txt`, 4500),
    fetchSafe(`${origin}/llms-full.txt`, 4500),
    fetchSafe(`${origin}/sitemap.xml`, 4500),
    queryDnsTxt(rootDomain),
    queryDnsTxt(`_dmarc.${rootDomain}`),
  ]);

  let spfAll = spfHost;
  let dmarcAll = dmarcHost;
  if (orgDomain !== rootDomain) {
    if (!spfAll.some(x => /v=spf1/i.test(x))) spfAll = await queryDnsTxt(orgDomain);
    if (!dmarcAll.some(x => /v=dmarc1/i.test(x))) dmarcAll = await queryDnsTxt(`_dmarc.${orgDomain}`);
  }

  const spfTxt = spfAll.filter(x => /v=spf1/i.test(x));
  const dmarcTxt = dmarcAll.filter(x => /v=dmarc1/i.test(x));
  const parsed = parseHtmlMeta(home.text, finalUrl);
  const checks = [];

  const llmsText = llmsR.ok && llmsR.status === 200 ? llmsR.text.trim() : "";
  const llmsHtml = /^\s*<!doctype\s+html|^\s*<html/i.test(llmsText);
  if (llmsText && !llmsHtml && llmsText.length >= 60 && llmsText.includes("#")) {
    checks.push({ id: "llms_txt", category: "AI Search (GEO)", title: "/llms.txt index published", status: "pass", points: 15, max_points: 15, evidence: `Found valid /llms.txt (${llmsText.length} chars).` });
  } else if (llmsText && !llmsHtml) {
    checks.push({ id: "llms_txt", category: "AI Search (GEO)", title: "/llms.txt index published", status: "warn", points: 7, max_points: 15, evidence: `/llms.txt exists but lacks Markdown H1/section links.` });
  } else {
    checks.push({ id: "llms_txt", category: "AI Search (GEO)", title: "/llms.txt index published", status: "fail", points: 0, max_points: 15, evidence: `Missing /llms.txt (HTTP ${llmsR.status || "ERR"}).` });
  }

  const lfText = llmsFullR.ok && llmsFullR.status === 200 ? llmsFullR.text.trim() : "";
  const lfHtml = /^\s*<!doctype\s+html|^\s*<html/i.test(lfText);
  if (lfText && !lfHtml && lfText.length >= 150) {
    checks.push({ id: "llms_full_txt", category: "AI Search (GEO)", title: "/llms-full.txt deep context", status: "pass", points: 10, max_points: 10, evidence: `Found /llms-full.txt (${lfText.length} chars).` });
  } else {
    checks.push({ id: "llms_full_txt", category: "AI Search (GEO)", title: "/llms-full.txt deep context", status: "fail", points: 0, max_points: 10, evidence: `Missing /llms-full.txt full-context corpus for AI agents.` });
  }

  const rbText = robotsR.ok && robotsR.status === 200 && !/<html/i.test(robotsR.text.slice(0, 200)) ? robotsR.text : "";
  if (rbText) {
    const groups = [];
    let gAgents = [], gDis = [], gAll = [], seenRule = false;
    for (const rawLn of rbText.split(/\r?\n/)) {
      const ln = rawLn.split("#")[0].trim();
      const idx = ln.indexOf(":");
      if (!ln || idx < 0) continue;
      const k = ln.slice(0, idx).trim().toLowerCase();
      const v = ln.slice(idx + 1).trim();
      if (k === "user-agent") {
        if (seenRule && gAgents.length) {
          groups.push({ gAgents, gDis, gAll });
          gAgents = []; gDis = []; gAll = []; seenRule = false;
        }
        gAgents.push(v);
      } else if (k === "disallow") {
        seenRule = true; if (v) gDis.push(v);
      } else if (k === "allow") {
        seenRule = true; if (v) gAll.push(v);
      }
    }
    if (gAgents.length) groups.push({ gAgents, gDis, gAll });
    const blockedBots = [];
    let wildcardBlocked = false;
    for (const g of groups) {
      if (g.gDis.includes("/") && !g.gAll.includes("/")) {
        if (g.gAgents.includes("*")) wildcardBlocked = true;
        for (const bot of AI_BOTS) {
          if (g.gAgents.some(a => a.toLowerCase() === bot.toLowerCase()) && !blockedBots.includes(bot)) blockedBots.push(bot);
        }
      }
    }
    const mentionsAi = AI_BOTS.some(b => rbText.toLowerCase().includes(b.toLowerCase()));
    if (wildcardBlocked || blockedBots.length) {
      checks.push({ id: "ai_robots", category: "AI Search (GEO)", title: "AI search citation bots allowed", status: "fail", points: 0, max_points: 10, evidence: `robots.txt blocks: ${blockedBots.join(", ") || "All crawlers (*)"}.` });
    } else if (mentionsAi) {
      checks.push({ id: "ai_robots", category: "AI Search (GEO)", title: "AI search citation bots allowed", status: "pass", points: 10, max_points: 10, evidence: "robots.txt explicitly configures AI search crawlers." });
    } else {
      checks.push({ id: "ai_robots", category: "AI Search (GEO)", title: "AI search citation bots allowed", status: "warn", points: 6, max_points: 10, evidence: "robots.txt lacks explicit OAI-SearchBot / PerplexityBot rules." });
    }
  } else {
    checks.push({ id: "ai_robots", category: "AI Search (GEO)", title: "AI search citation bots allowed", status: "fail", points: 0, max_points: 10, evidence: "No valid /robots.txt found." });
  }

  const smOk = (sitemapR.ok && sitemapR.status === 200 && /<(urlset|sitemapindex)/i.test(sitemapR.text)) || /sitemap:/i.test(rbText);
  checks.push({
    id: "sitemap", category: "AI Search (GEO)", title: "XML Sitemap discoverable",
    status: smOk ? "pass" : "fail", points: smOk ? 10 : 0, max_points: 10,
    evidence: smOk ? "XML Sitemap reachable." : `/sitemap.xml missing (HTTP ${sitemapR.status || "ERR"}).`
  });

  let validSchemas = [];
  for (const raw of parsed.jsonLd) {
    try {
      const obj = JSON.parse(raw);
      const arr = Array.isArray(obj) ? obj : [obj];
      arr.forEach(it => { if (it && typeof it === "object") validSchemas.push(String(it["@type"] || "Thing")); });
    } catch {}
  }
  if (validSchemas.length) {
    checks.push({ id: "json_ld", category: "Search & Conversion", title: "Schema.org JSON-LD structured data", status: "pass", points: 12, max_points: 12, evidence: `Valid JSON-LD: ${validSchemas.slice(0, 3).join(", ")}.` });
  } else {
    checks.push({ id: "json_ld", category: "Search & Conversion", title: "Schema.org JSON-LD structured data", status: "fail", points: 0, max_points: 12, evidence: "Zero valid Schema.org JSON-LD blocks on homepage." });
  }

  const ogKeys = ["og:title", "og:description", "og:image"].filter(k => parsed.meta[k]);
  checks.push({
    id: "opengraph", category: "Search & Conversion", title: "OpenGraph social conversion cards",
    status: ogKeys.length === 3 ? "pass" : (ogKeys.length ? "warn" : "fail"),
    points: ogKeys.length === 3 ? 10 : (ogKeys.length ? 5 : 0), max_points: 10,
    evidence: ogKeys.length === 3 ? "All core OpenGraph tags configured." : `Present: ${ogKeys.length}/3 OpenGraph tags.`
  });

  const hasTitle = parsed.title.length >= 10 && parsed.title.length <= 85;
  const hasDesc = (parsed.meta["description"] || "").length >= 40;
  const hasCanon = Boolean(parsed.canonical);
  const ptsMeta = (hasTitle ? 3 : (parsed.title ? 1 : 0)) + (hasDesc ? 3 : 0) + (hasCanon ? 2 : 0);
  checks.push({
    id: "core_meta", category: "Search & Conversion", title: "Title, meta description & canonical URL",
    status: ptsMeta === 8 ? "pass" : (ptsMeta >= 4 ? "warn" : "fail"), points: ptsMeta, max_points: 8,
    evidence: ptsMeta === 8 ? "Core SEO metadata valid." : "Missing or suboptimal title, meta description, or canonical URL."
  });

  const isHttps = uObj.protocol === "https:";
  const hsts = home.headers["strict-transport-security"] || "";
  const ptsHsts = isHttps && /max-age=/i.test(hsts) ? 7 : (isHttps ? 3 : 0);
  checks.push({
    id: "hsts", category: "Security & Deliverability", title: "HTTPS + Strict-Transport-Security",
    status: ptsHsts === 7 ? "pass" : (ptsHsts === 3 ? "warn" : "fail"), points: ptsHsts, max_points: 7,
    evidence: ptsHsts === 7 ? "HTTPS + HSTS active." : "Strict-Transport-Security (HSTS) header missing."
  });

  const secNames = [
    ["content-security-policy", "CSP"],
    ["x-content-type-options", "X-Content-Type-Options"],
    ["x-frame-options", "X-Frame-Options"],
    ["referrer-policy", "Referrer-Policy"]
  ];
  const secMissing = secNames.filter(([k]) => !home.headers[k]).map(([, lbl]) => lbl);
  const ptsSec = (4 - secMissing.length) * 2;
  checks.push({
    id: "sec_headers", category: "Security & Deliverability", title: "Hardened HTTP security headers",
    status: ptsSec === 8 ? "pass" : (ptsSec >= 4 ? "warn" : "fail"), points: ptsSec, max_points: 8,
    evidence: secMissing.length === 0 ? "All 4 security headers active." : `Missing: ${secMissing.join(", ")}.`
  });

  if (spfTxt.length) {
    const strictSpf = /[-~]all/i.test(spfTxt[0]);
    checks.push({ id: "spf", category: "Security & Deliverability", title: "SPF email authentication record", status: strictSpf ? "pass" : "warn", points: strictSpf ? 5 : 3, max_points: 5, evidence: `Found SPF: ${spfTxt[0].slice(0, 65)}` });
  } else {
    checks.push({ id: "spf", category: "Security & Deliverability", title: "SPF email authentication record", status: "fail", points: 0, max_points: 5, evidence: `No v=spf1 TXT record on ${rootDomain}.` });
  }

  if (dmarcTxt.length) {
    const enforced = /p\s*=\s*(quarantine|reject)/i.test(dmarcTxt[0]);
    checks.push({ id: "dmarc", category: "Security & Deliverability", title: "DMARC anti-spoofing & inbox placement", status: enforced ? "pass" : "warn", points: enforced ? 5 : 2, max_points: 5, evidence: `Found DMARC (${enforced ? "enforced" : "p=none warning-only"}).` });
  } else {
    checks.push({ id: "dmarc", category: "Security & Deliverability", title: "DMARC anti-spoofing & inbox placement", status: "fail", points: 0, max_points: 5, evidence: `No _dmarc.${rootDomain} TXT record found.` });
  }

  const score = checks.reduce((acc, c) => acc + c.points, 0);
  const siteTitle = parsed.title || parsed.meta["og:title"] || rootDomain;
  const siteDesc = parsed.meta["description"] || parsed.meta["og:description"] || parsed.excerpt.slice(0, 160) || `Official website for ${rootDomain}.`;

  return {
    audit: {
      target_url: targetUrl, final_url: finalUrl, domain: uObj.hostname, root_domain: rootDomain,
      timestamp_utc: new Date().toISOString(), score, grade: gradeFor(score), response_ms: home.ms,
      site_title: siteTitle, site_description: siteDesc, checks
    },
    parsed
  };
}

function generateFixFilesJs(audit, parsed) {
  const uObj = new URL(audit.final_url);
  const origin = uObj.origin;
  const topicLines = (parsed.headings || []).slice(0, 8).map(([, h]) => `- ${h}`).join("\n");
  const llmsTxt = `# ${audit.site_title}\n\n> ${audit.site_description}\n\nCanonical website: ${origin}\nFull LLM context digest: ${origin}/llms-full.txt\n\n## Key Pages\n- [${audit.site_title}](${audit.final_url}): ${audit.site_description}\n` + (topicLines ? `\n## Core Topics Covered\n${topicLines}\n` : "");
  const llmsFull = `# ${audit.site_title} — Complete AI & RAG Reference Corpus\n\n> ${audit.site_description}\n\nSource Domain: ${audit.root_domain}\nGenerated: ${audit.timestamp_utc}\n\n---\n## 1. ${audit.site_title}\nURL: ${audit.final_url}\n\n${parsed.excerpt}\n`;
  const robots = `# Optimized robots.txt for ${audit.root_domain}\nUser-agent: *\nAllow: /\n\n` + AI_BOTS.map(b => `User-agent: ${b}\nAllow: /\n`).join("\n") + `\nSitemap: ${origin}/sitemap.xml\n# LLM Index: ${origin}/llms.txt\n`;
  const schemaObj = {
    "@context": "https://schema.org",
    "@graph": [
      { "@type": "Organization", "@id": `${origin}/#organization`, name: audit.site_title, url: origin, description: audit.site_description },
      { "@type": "WebSite", "@id": `${origin}/#website`, url: origin, name: audit.site_title, description: audit.site_description, publisher: { "@id": `${origin}/#organization` } }
    ]
  };
  const schemaHtml = `<!-- Drop into <head> of ${audit.root_domain} -->\n<link rel="canonical" href="${audit.final_url}" />\n<meta name="description" content="${audit.site_description.replace(/"/g, "&quot;")}" />\n<meta property="og:type" content="website" />\n<meta property="og:url" content="${audit.final_url}" />\n<meta property="og:title" content="${audit.site_title.replace(/"/g, "&quot;")}" />\n<meta property="og:description" content="${audit.site_description.replace(/"/g, "&quot;")}" />\n<meta property="og:image" content="${origin}/og-image.png" />\n<meta name="twitter:card" content="summary_large_image" />\n<script type="application/ld+json">\n${JSON.stringify(schemaObj, null, 2)}\n</script>\n`;
  const hdrs = [
    { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
    { key: "X-Content-Type-Options", value: "nosniff" },
    { key: "X-Frame-Options", value: "SAMEORIGIN" },
    { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
    { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
    { key: "Content-Security-Policy", value: "default-src 'self' https: data: 'unsafe-inline' 'unsafe-eval'; frame-ancestors 'self'; upgrade-insecure-requests" }
  ];
  const vercelJson = JSON.stringify({ headers: [{ source: "/(.*)", headers: hdrs }] }, null, 2) + "\n";
  const cfHeaders = "/*\n" + hdrs.map(h => `  ${h.key}: ${h.value}\n`).join("");
  const nginxConf = hdrs.map(h => `add_header ${h.key} "${h.value}" always;\n`).join("");
  const dnsTxt = `# Email Deliverability DNS Patch for ${audit.root_domain}\n\n1) SPF TXT on @:\n"v=spf1 include:_spf.google.com ~all"\n\n2) DMARC TXT on _dmarc:\n"v=DMARC1; p=quarantine; pct=100; rua=mailto:dmarc@${audit.root_domain}"\n`;
  const reportMd = `# CiteReady Audit & Fix Pack — ${audit.root_domain}\n\n- Baseline Score: **${audit.score}/100 (Grade ${audit.grade})**\n- Target Score After Deploy: **95–100/100 (Grade A)**\n\n## Checks\n` + audit.checks.map(c => `- [${c.status.toUpperCase()}] (${c.points}/${c.max_points}) **${c.title}** — ${c.evidence}`).join("\n") + "\n";

  return {
    "public/llms.txt": llmsTxt,
    "public/llms-full.txt": llmsFull,
    "public/robots.txt": robots,
    "snippets/schema-jsonld.html": schemaHtml,
    "configs/vercel.json": vercelJson,
    "configs/_headers": cfHeaders,
    "configs/nginx-security.conf": nginxConf,
    "dns/email-deliverability-records.txt": dnsTxt,
    "AUDIT_REPORT.md": reportMd,
  };
}

// Pure-JS PKZIP builder (Store method 0 + standard IEEE 802.3 CRC32) — zero dependencies!
const CRC_TABLE = (() => {
  const t = new Uint32Array(256);
  for (let i = 0; i < 256; i++) {
    let c = i;
    for (let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[i] = c >>> 0;
  }
  return t;
})();

function crc32(bytes) {
  let c = 0xFFFFFFFF;
  for (let i = 0; i < bytes.length; i++) c = CRC_TABLE[(c ^ bytes[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

export function buildZipArchive(folderPrefix, filesObj) {
  const enc = new TextEncoder();
  const entries = [];
  let localTotal = 0;
  let centralTotal = 0;

  for (const [relPath, content] of Object.entries(filesObj)) {
    const nameBytes = enc.encode(`${folderPrefix}/${relPath}`);
    const dataBytes = enc.encode(content);
    const sum = crc32(dataBytes);
    entries.push({ nameBytes, dataBytes, sum, offset: localTotal });
    localTotal += 30 + nameBytes.length + dataBytes.length;
    centralTotal += 46 + nameBytes.length;
  }

  const out = new Uint8Array(localTotal + centralTotal + 22);
  const view = new DataView(out.buffer);
  let pos = 0;

  for (const e of entries) {
    view.setUint32(pos, 0x04034b50, true);
    view.setUint16(pos + 4, 20, true);
    view.setUint16(pos + 6, 0x0800, true); // UTF-8 flag
    view.setUint16(pos + 8, 0, true);      // Store (uncompressed)
    view.setUint16(pos + 10, 0, true);
    view.setUint16(pos + 12, 0x5421, true);
    view.setUint32(pos + 14, e.sum, true);
    view.setUint32(pos + 18, e.dataBytes.length, true);
    view.setUint32(pos + 22, e.dataBytes.length, true);
    view.setUint16(pos + 26, e.nameBytes.length, true);
    view.setUint16(pos + 28, 0, true);
    out.set(e.nameBytes, pos + 30);
    out.set(e.dataBytes, pos + 30 + e.nameBytes.length);
    pos += 30 + e.nameBytes.length + e.dataBytes.length;
  }

  const centralStart = pos;
  for (const e of entries) {
    view.setUint32(pos, 0x02014b50, true);
    view.setUint16(pos + 4, 20, true);
    view.setUint16(pos + 6, 20, true);
    view.setUint16(pos + 8, 0x0800, true);
    view.setUint16(pos + 10, 0, true);
    view.setUint16(pos + 12, 0, true);
    view.setUint16(pos + 14, 0x5421, true);
    view.setUint32(pos + 16, e.sum, true);
    view.setUint32(pos + 20, e.dataBytes.length, true);
    view.setUint32(pos + 24, e.dataBytes.length, true);
    view.setUint16(pos + 28, e.nameBytes.length, true);
    view.setUint16(pos + 30, 0, true);
    view.setUint16(pos + 32, 0, true);
    view.setUint16(pos + 34, 0, true);
    view.setUint16(pos + 36, 0, true);
    view.setUint32(pos + 38, 0, true);
    view.setUint32(pos + 42, e.offset, true);
    out.set(e.nameBytes, pos + 46);
    pos += 46 + e.nameBytes.length;
  }

  view.setUint32(pos, 0x06054b50, true);
  view.setUint16(pos + 4, 0, true);
  view.setUint16(pos + 6, 0, true);
  view.setUint16(pos + 8, entries.length, true);
  view.setUint16(pos + 10, entries.length, true);
  view.setUint32(pos + 12, centralTotal, true);
  view.setUint32(pos + 16, centralStart, true);
  view.setUint16(pos + 20, 0, true);
  return out;
}

async function verifyLicenseEdge(licenseKey, env) {
  const master = (env.CITEREADY_MASTER_KEY || "").trim();
  if (master && licenseKey.trim() === master) return { ok: true };
  const pids = [env.GUMROAD_SINGLE_PRODUCT_ID || "H3r8un8nxQck_A_OasTU2Q==", env.GUMROAD_AGENCY_PRODUCT_ID].map(x => (x || "").trim()).filter(Boolean);
  if (!pids.length) return { ok: false, error: "Product IDs not configured yet." };

  for (const pid of pids) {
    const body = new URLSearchParams({ product_id: pid, license_key: licenseKey.trim(), increment_uses_count: "true" });
    const r = await fetch("https://api.gumroad.com/v2/licenses/verify", { method: "POST", body });
    const data = await r.json().catch(() => ({}));
    if (data && data.success) {
      if (data.purchase && (data.purchase.refunded || data.purchase.chargebacked)) {
        return { ok: false, error: "This license was refunded." };
      }
      return { ok: true };
    }
  }
  return { ok: false, error: "Invalid Gumroad license key." };
}

const SEC_HEADERS = {
  "Strict-Transport-Security": "max-age=63072000; includeSubDomains; preload",
  "X-Content-Type-Options": "nosniff",
  "X-Frame-Options": "SAMEORIGIN",
  "Referrer-Policy": "strict-origin-when-cross-origin",
  "Content-Security-Policy": "default-src 'self' https: data: blob: 'unsafe-inline'; frame-ancestors 'self'"
};

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type"
};

async function handleRequest(request, env) {
    const url = new URL(request.url);
    const origin = url.origin;
    SELF_HOST = url.hostname.toLowerCase();
    SELF_FETCH_FN = (req) => handleRequest(req, env);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS_HEADERS });
    }
    if (request.method === "GET" && url.pathname === "/") {
      const singleUrl = env.SINGLE_CHECKOUT_URL || "https://romanfjose.gumroad.com/l/citeready?wanted=true";
      const agencyUrl = env.AGENCY_CHECKOUT_URL || singleUrl;
      const html = UI_HTML.replace(/__SINGLE_CHECKOUT_URL__/g, singleUrl).replace(/__AGENCY_CHECKOUT_URL__/g, agencyUrl);
      return new Response(html, { headers: { "Content-Type": "text/html; charset=utf-8", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/robots.txt") {
      const rb = "User-agent: *\nAllow: /\n\n" + AI_BOTS.map(b => `User-agent: ${b}\nAllow: /\n`).join("\n") + `\nSitemap: ${origin}/sitemap.xml\n`;
      return new Response(rb, { headers: { "Content-Type": "text/plain; charset=utf-8", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/llms.txt") {
      const lt = `# CiteReady — Instant AI Search (llms.txt), Schema & DMARC Site Fixer\n\n> Scan any website in 3 seconds for AI search citation readiness (/llms.txt, /llms-full.txt, AI crawler rules), Schema.org JSON-LD, HTTP security headers, and SPF/DMARC email deliverability.\n\nCanonical website: ${origin}/\nFull LLM context digest: ${origin}/llms-full.txt\n\n## Key Pages\n- [CiteReady Live Scanner](${origin}/): Free 11-point live HTTP & DNS audit with tailored 9-file Fix-Pack builder.\n- [CiteReady Pro CLI & License](https://romanfjose.gumroad.com/l/citeready): One-time $29 Fix-Pack unlock + offline Python CLI & CI Action.\n`;
      return new Response(lt, { headers: { "Content-Type": "text/plain; charset=utf-8", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/llms-full.txt") {
      const lft = `# CiteReady — Complete AI & RAG Reference Corpus\n\n> CiteReady audits live domains across 11 technical visibility, conversion, security, and email deliverability signals and compiles a drop-in 9-file Fix-Pack ZIP (public/llms.txt, public/llms-full.txt, public/robots.txt, snippets/schema-jsonld.html, configs/vercel.json, configs/_headers, configs/nginx-security.conf, dns/email-deliverability-records.txt, and AUDIT_REPORT.md).\n\nWeb App: ${origin}/\nCheckout & Pro CLI ($29 one-time): https://romanfjose.gumroad.com/l/citeready\n`;
      return new Response(lft, { headers: { "Content-Type": "text/plain; charset=utf-8", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/sitemap.xml") {
      const sm = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n  <url><loc>${origin}/</loc></url>\n</urlset>\n`;
      return new Response(sm, { headers: { "Content-Type": "application/xml; charset=utf-8", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/og-image.svg") {
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630"><rect width="1200" height="630" fill="#090d16"/><text x="80" y="260" fill="#38bdf8" font-family="sans-serif" font-size="64" font-weight="bold">CiteReady</text><text x="80" y="350" fill="#f3f6fc" font-family="sans-serif" font-size="40">Instant AI Search (llms.txt), Schema &amp; DMARC Fixer</text></svg>`;
      return new Response(svg, { headers: { "Content-Type": "image/svg+xml", ...SEC_HEADERS } });
    }
    if (request.method === "GET" && url.pathname === "/api/audit") {
      const target = (url.searchParams.get("url") || "").trim();
      if (!target) return Response.json({ error: "Missing ?url= parameter" }, { status: 400 });
      try {
        const { audit, parsed } = await auditDomain(target);
        const files = generateFixFilesJs(audit, parsed);
        return Response.json({
          audit,
          preview: {
            llms_excerpt: files["public/llms.txt"].split("\n").slice(0, 8).join("\n") + "\n\n# ... [Unlock Full Fix-Pack ZIP]",
            schema_excerpt: files["snippets/schema-jsonld.html"].split("\n").slice(0, 11).join("\n") + "\n<!-- ... [Truncated] -->"
          }
        }, { headers: CORS_HEADERS });
      } catch (err) {
        return Response.json({ error: err.message || String(err) }, { status: 400, headers: CORS_HEADERS });
      }
    }
    if (request.method === "POST" && url.pathname === "/api/unlock") {
      const body = await request.json().catch(() => ({}));
      const target = String(body.url || "").trim();
      const key = String(body.license_key || "").trim();
      if (!target || !key) return Response.json({ error: "url and license_key required" }, { status: 400, headers: CORS_HEADERS });
      const check = await verifyLicenseEdge(key, env || {});
      if (!check.ok) return Response.json({ error: check.error }, { status: 403, headers: CORS_HEADERS });
      try {
        const { audit, parsed } = await auditDomain(target);
        const files = generateFixFilesJs(audit, parsed);
        const prefix = `${audit.root_domain.replace(/\./g, "-")}-citeready-fixpack`;
        const zipBytes = buildZipArchive(prefix, files);
        return new Response(zipBytes, {
          headers: {
            "Content-Type": "application/zip",
            "Content-Disposition": `attachment; filename="${prefix}.zip"`,
            ...CORS_HEADERS
          }
        });
      } catch (err) {
        return Response.json({ error: err.message || String(err) }, { status: 502, headers: CORS_HEADERS });
      }
    }
    return Response.json({ error: "Not found" }, { status: 404 });
}

export default {
  async fetch(request, env) {
    return handleRequest(request, env);
  }
};
