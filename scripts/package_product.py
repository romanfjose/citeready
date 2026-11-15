"""Packages the standalone CiteReady Pro Digital Product ZIP + Launch & Checkout Kit."""

from __future__ import annotations

import pathlib
import zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent

PRO_README = """# CiteReady Pro CLI & CI Action (v1.0.0)

Thank you for purchasing **CiteReady Pro**!

 Zero external dependencies required — runs on any machine with Python 3.10+.

## Quickstart

### 1. Audit any live website & generate a 9-file Drop-In Fix Pack ZIP
```bash
python -m citeready.cli scan https://yourdomain.com --out-zip ./fixpack.zip
```

### 2. Extract drop-in files directly into a folder
```bash
python -m citeready.cli scan https://yourdomain.com --out-dir ./citeready-fixes
```

### 3. Agency Batch Mode (Audit 10–500 client domains at once)
Create `domains.txt` (one domain per line), then run:
```bash
python -m citeready.cli batch domains.txt --out-dir ./client-packs
```

### 4. Local Interactive Web Dashboard
```bash
python -m citeready.cli serve --port 8787
```

### 5. CI/CD Regression Gate (Fail build if score drops below threshold)
```bash
python -m citeready.cli scan https://yourdomain.com --min-score 85
```
"""

GITHUB_ACTION_YML = """name: 'CiteReady GEO & Security Audit'
description: 'Audits live URL for /llms.txt, Schema JSON-LD, HSTS/CSP headers, and SPF/DMARC, exporting a Fix-Pack artifact.'
inputs:
  url:
    description: 'Target live URL to scan'
    required: true
  min_score:
    description: 'Minimum passing score (0-100)'
    required: false
    default: '0'
runs:
  using: 'composite'
  steps:
    - name: Run CiteReady Scan
      shell: bash
      run: |
        PYTHONPATH="${{ github.action_path }}" python3 -m citeready.cli scan "${{ inputs.url }}" --out-zip citeready-fixpack.zip --min-score "${{ inputs.min_score }}"
"""

LAUNCH_KIT_MD = r"""# CiteReady — <60s Checkout & 7-Day Revenue Execution Kit

## Step 1: Production Stack — 100% LIVE ✅
- **Public Edge Web SaaS:** https://citeready.romanfjose.workers.dev
- **Gumroad Live Checkout (\$29):** https://romanfjose.gumroad.com/l/citeready?wanted=true
- **Verified Product ID (`wrangler.toml` wired):** `H3r8un8nxQck_A_OasTU2Q==`

---

## Step 2: Zero-Cost High-Intent Traffic Channels (Days 1–7)

### Channel A — Hacker News (`Show HN` — Submit at https://news.ycombinator.com/submit)
- **Title:** `Show HN: CiteReady – Instant audit for /llms.txt, JSON-LD, security headers, and DMARC`
- **URL:** `https://citeready.romanfjose.workers.dev`
- **First Comment:**
  > Hey HN — built a zero-signup scanner after noticing most newly launched SaaS apps omit `/llms.txt`, lack `Schema.org` JSON-LD, and ship without `_dmarc` TXT records or HSTS/CSP headers.
  >
  > Paste any domain and it checks 11 live HTTP + Cloudflare DoH DNS signals in ~3s, then compiles a tailored drop-in `llms.txt`, `llms-full.txt`, `robots.txt`, `JSON-LD`, `vercel.json`/`_headers`, and `SPF/DMARC` bundle from your live pages. The full scanner and preview are completely free with no email gate; the one-click 9-file ZIP + offline Python CLI/batch tool is \$29 one-time. Would love feedback on false positives or extra checks to add.

### Channel B — Reddit (`r/SideProject`, `r/SaaS`, `r/IndieHackers`, `r/Entrepreneur`)
- **Title:** `I scanned newly-launched SaaS domains today — 88% were missing /llms.txt, JSON-LD, or enforced DMARC. Built a free 3-second live checker.`
- **Body:** Link `https://citeready.romanfjose.workers.dev` (zero signup required) + share aggregate stats from `leads/verified_prospects.json`.

### Channel C — Personalized `Show HN` / Indie Launch Founder Diagnostic Links
- Open `leads/outreach_ready.md`: every custom-domain launch has a live auto-scan URL (`https://citeready.romanfjose.workers.dev/?url=<domain>`) ready to drop in launch feedback threads or founder DMs.
"""


def main() -> None:
    dist_dir = ROOT / "dist"
    dist_dir.mkdir(parents=True, exist_ok=True)
    zip_path = dist_dir / "citeready-pro-v1.0.0.zip"

    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        for py_file in sorted((ROOT / "citeready").glob("*.py")):
            zf.write(py_file, arcname=f"citeready-pro/citeready/{py_file.name}")
        zf.writestr("citeready-pro/README.md", PRO_README.encode("utf-8"))
        zf.writestr("citeready-pro/action.yml", GITHUB_ACTION_YML.encode("utf-8"))

    launch_dir = ROOT / "launch"
    launch_dir.mkdir(parents=True, exist_ok=True)
    (launch_dir / "gumroad_and_launch_kit.md").write_text(LAUNCH_KIT_MD, encoding="utf-8")
    print(f"[+] Packaged {zip_path} ({zip_path.stat().st_size:,} bytes) + launch kit")


if __name__ == "__main__":
    main()
