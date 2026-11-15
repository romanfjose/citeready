# ⚡ CiteReady

**Instant AI Search (`llms.txt`), Schema.org `JSON-LD`, HTTP Security Header & `SPF/DMARC` Deliverability Auditor + Drop-In Fix Pack Generator.**

👉 **[Run Live 3-Second Web Audit (Zero Install / Zero Signup)](https://romanfjose.github.io/citeready/)**

---

## Why CiteReady?

88% of newly-launched SaaS and e-commerce domains silently lose organic citations and inbox placement due to 4 preventable gaps:
1. **Invisible to AI Answer Engines:** Missing `/llms.txt` and `/llms-full.txt`, or accidentally blocking `OAI-SearchBot`, `PerplexityBot`, and `ClaudeBot` in `robots.txt`.
2. **Zero Structured Entity Data:** Missing or invalid `Schema.org` `application/ld+json` and OpenGraph preview metadata.
3. **Unauthenticated Outbound Email:** Missing or `p=none` `_dmarc` / `v=spf1` DNS TXT records (flagged under Gmail & Yahoo bulk-sender rules).
4. **Missing Security Headers:** Missing `Strict-Transport-Security` (HSTS), `Content-Security-Policy`, `X-Content-Type-Options`, and `X-Frame-Options`.

CiteReady checks **11 live HTTP + DNS-over-HTTPS signals** in ~3 seconds (zero external Python dependencies) and compiles a **9-file drop-in Fix Pack** tailored from your live pages:
- `public/llms.txt` & `public/llms-full.txt` (`llmstxt.org` spec)
- `public/robots.txt` (AI search citation ready)
- `snippets/schema-jsonld.html` (validated `Organization` + `WebSite` JSON-LD + OpenGraph)
- `configs/vercel.json`, `configs/_headers` (Cloudflare/Netlify), `configs/nginx-security.conf`
- `dns/email-deliverability-records.txt` (`SPF` + enforced `DMARC`)
- `AUDIT_REPORT.md` (5-minute deployment checklist)

---

## CLI Quickstart (Zero Dependencies — Python 3.10+)

```bash
git clone https://github.com/romanfjose/citeready.git
cd citeready

# Run a 11-point live audit in your terminal
python -m citeready.cli scan https://yourdomain.com

# CI/CD regression gate (exits non-zero if score < 85)
python -m citeready.cli scan https://yourdomain.com --min-score 85
```

## Instant Web Fix-Pack & Pro Bundle

- **Free Live Web Scanner:** [https://romanfjose.github.io/citeready/](https://romanfjose.github.io/citeready/)
- **1-Click Web ZIP Unlock + Agency Batch Pack (\$29 one-time):** [Get CiteReady Pro on Gumroad](https://romanfjose.gumroad.com/l/citeready)
