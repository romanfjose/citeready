"""Builds the self-contained zero-dependency Cloudflare Worker (web/worker.js + wrangler.toml)."""

from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from citeready.ui_html import UI_TEMPLATE  # noqa: E402

WORKER_JS_BODY = r"""
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
"""


def main() -> None:
    web_dir = ROOT / "web"
    web_dir.mkdir(parents=True, exist_ok=True)
    worker_code = f"const UI_HTML = {json.dumps(UI_TEMPLATE)};\n" + WORKER_JS_BODY
    (web_dir / "worker.js").write_text(worker_code, encoding="utf-8")

    wrangler_toml = (
        'name = "citeready"\n'
        'main = "web/worker.js"\n'
        'compatibility_date = "2026-01-01"\n\n'
        "[vars]\n"
        'SINGLE_CHECKOUT_URL = "https://romanfjose.gumroad.com/l/citeready?wanted=true"\n'
        'AGENCY_CHECKOUT_URL = "https://romanfjose.gumroad.com/l/citeready?wanted=true"\n'
        'GUMROAD_SINGLE_PRODUCT_ID = "H3r8un8nxQck_A_OasTU2Q=="\n'
        'GUMROAD_AGENCY_PRODUCT_ID = ""\n'
    )
    (ROOT / "wrangler.toml").write_text(wrangler_toml, encoding="utf-8")

    # Also build GitHub Pages frontend (docs/index.html) backed by CORS API so github.io URLs never trigger .workers.dev spam filters!
    docs_dir = ROOT / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    gh_pages_html = (
        UI_TEMPLATE
        .replace("__SINGLE_CHECKOUT_URL__", "https://romanfjose.gumroad.com/l/citeready?wanted=true")
        .replace("__AGENCY_CHECKOUT_URL__", "https://romanfjose.gumroad.com/l/citeready?wanted=true")
        .replace("https://citeready.romanfjose.workers.dev/", "https://romanfjose.github.io/citeready/")
        .replace("<script>", '<script>\n    window.CITEREADY_API_BASE = "https://citeready.romanfjose.workers.dev";', 1)
    )
    (docs_dir / "index.html").write_text(gh_pages_html, encoding="utf-8")
    (docs_dir / ".nojekyll").write_text("", encoding="utf-8")
    print(f"[+] Built web/worker.js ({len(worker_code):,} chars), docs/index.html, and wrangler.toml")


if __name__ == "__main__":
    main()
