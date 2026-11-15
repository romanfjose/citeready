"""Production-ready HTTP server for CiteReady Web UI + Audit API + Gumroad License Unlock."""

from __future__ import annotations

import ipaddress
import json
import os
import socket
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from .engine import audit_url, build_fix_pack_zip, generate_fix_files, normalize_url
from .ui_html import UI_TEMPLATE


def is_safe_public_url(raw_url: str, allow_local_test: bool = False) -> tuple[bool, str]:
    """Block SSRF against loopback, link-local, metadata, and private IPs."""
    if allow_local_test:
        return True, ""
    try:
        norm = normalize_url(raw_url)
        host = urllib.parse.urlsplit(norm).hostname or ""
        if not host or "." not in host:
            return False, "Please enter a valid public domain name (e.g. example.com)."
        infos = socket.getaddrinfo(host, None)
        for info in infos:
            ip_str = info[4][0]
            ip_obj = ipaddress.ip_address(ip_str)
            if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_link_local or ip_obj.is_reserved or ip_obj.is_multicast:
                return False, "Scanning private or internal network addresses is blocked."
        return True, ""
    except Exception as exc:
        return False, f"DNS resolution failed for domain: {exc}"


def verify_gumroad_license(license_key: str) -> tuple[bool, str]:
    """Verify a Gumroad license key against SINGLE or AGENCY product IDs (or owner master key)."""
    master_key = os.environ.get("CITEREADY_MASTER_KEY", "").strip()
    if master_key and license_key.strip() == master_key:
        return True, "Master key accepted"

    product_ids = [
        p.strip()
        for p in (
            os.environ.get("GUMROAD_SINGLE_PRODUCT_ID", "H3r8un8nxQck_A_OasTU2Q=="),
            os.environ.get("GUMROAD_AGENCY_PRODUCT_ID", ""),
        )
        if p.strip()
    ]
    if not product_ids:
        return False, "Checkout product IDs are not configured on the server yet."

    for pid in product_ids:
        payload = urllib.parse.urlencode(
            {"product_id": pid, "license_key": license_key.strip(), "increment_uses_count": "true"}
        ).encode("utf-8")
        req = urllib.request.Request(
            "https://api.gumroad.com/v2/licenses/verify",
            data=payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=6.0) as resp:
                data = json.loads(resp.read(32768).decode("utf-8", errors="replace"))
            if data.get("success"):
                purchase = data.get("purchase") or {}
                if purchase.get("refunded") or purchase.get("chargebacked"):
                    return False, "This license key has been refunded or chargebacked."
                return True, "Verified"
        except urllib.error.HTTPError:
            continue
        except Exception as exc:
            return False, f"License verification gateway error: {exc}"

    return False, "Invalid Gumroad license key. Check your Gumroad receipt and try again."


def make_preview_snippets(files: dict[str, str]) -> dict[str, str]:
    llms_lines = files["public/llms.txt"].splitlines()
    schema_lines = files["snippets/schema-jsonld.html"].splitlines()
    return {
        "llms_excerpt": "\n".join(llms_lines[:8]) + "\n\n# ... [Unlock Full Fix-Pack ZIP for complete llms.txt + llms-full.txt + 7 more files]",
        "schema_excerpt": "\n".join(schema_lines[:11]) + "\n<!-- ... [Truncated — Full validated JSON-LD + HSTS/CSP + DMARC inside ZIP] -->",
    }


class CiteReadyHandler(BaseHTTPRequestHandler):
    allow_local_test: bool = False

    def log_message(self, fmt: str, *args: Any) -> None:
        return  # Quiet clean operation

    def _send_json(self, status: int, obj: dict[str, Any]) -> None:
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/":
            single_url = os.environ.get("SINGLE_CHECKOUT_URL", "https://romanfjose.gumroad.com/l/citeready?wanted=true")
            agency_url = os.environ.get("AGENCY_CHECKOUT_URL", single_url)
            html_doc = (
                UI_TEMPLATE.replace("__SINGLE_CHECKOUT_URL__", single_url)
                .replace("__AGENCY_CHECKOUT_URL__", agency_url)
                .encode("utf-8")
            )
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html_doc)))
            self.end_headers()
            self.wfile.write(html_doc)
            return

        if parsed.path == "/api/health":
            self._send_json(200, {"ok": True, "service": "citeready"})
            return

        if parsed.path == "/api/audit":
            qs = urllib.parse.parse_qs(parsed.query)
            target = (qs.get("url") or [""])[0].strip()
            if not target:
                self._send_json(400, {"error": "Missing ?url= query parameter."})
                return
            ok_url, reason = is_safe_public_url(target, allow_local_test=self.allow_local_test)
            if not ok_url:
                self._send_json(400, {"error": reason})
                return
            try:
                res = audit_url(target, crawl_subpages=3)
                files = generate_fix_files(res)
                d = res.to_dict()
                d.pop("crawled_pages", None)
                d.pop("existing_robots", None)
                self._send_json(200, {"audit": d, "preview": make_preview_snippets(files)})
            except Exception as exc:
                self._send_json(502, {"error": str(exc)})
            return

        self._send_json(404, {"error": "Not found"})

    def do_POST(self) -> None:
        parsed = urllib.parse.urlsplit(self.path)
        if parsed.path == "/api/unlock":
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(min(length, 16384))
            try:
                payload = json.loads(body.decode("utf-8"))
            except Exception:
                self._send_json(400, {"error": "Invalid JSON body"})
                return

            target = str(payload.get("url") or "").strip()
            license_key = str(payload.get("license_key") or "").strip()
            if not target or not license_key:
                self._send_json(400, {"error": "Both url and license_key are required."})
                return

            ok_url, reason = is_safe_public_url(target, allow_local_test=self.allow_local_test)
            if not ok_url:
                self._send_json(400, {"error": reason})
                return

            valid, msg = verify_gumroad_license(license_key)
            if not valid:
                self._send_json(403, {"error": msg})
                return

            try:
                res = audit_url(target, crawl_subpages=4)
                zbytes = build_fix_pack_zip(res)
                fname = f"{res.root_domain.replace('.', '-')}-citeready-fixpack.zip"
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.send_header("Content-Length", str(len(zbytes)))
                self.end_headers()
                self.wfile.write(zbytes)
            except Exception as exc:
                self._send_json(502, {"error": str(exc)})
            return

        self._send_json(404, {"error": "Not found"})


def run_server(host: str = "127.0.0.1", port: int = 8787) -> None:
    srv = ThreadingHTTPServer((host, port), CiteReadyHandler)
    print(f"CiteReady Web SaaS listening on http://{host}:{port}")
    srv.serve_forever()
