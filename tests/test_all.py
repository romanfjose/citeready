"""End-to-end verification suite for CiteReady Engine, Web API, License Gate, and Edge Worker ZIP."""

from __future__ import annotations

import io
import json
import os
import pathlib
import subprocess
import threading
import unittest
import urllib.error
import urllib.request
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from citeready.engine import analyze_robots_txt, audit_url, build_fix_pack_zip
from citeready.server import CiteReadyHandler

ROOT = pathlib.Path(__file__).resolve().parent.parent


class MockTargetSiteHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        return

    def do_GET(self):
        if self.path == "/":
            body = b"""<!doctype html><html><head>
            <title>AcmeCloud - Fast Serverless Postgres for AI Apps</title>
            <meta name="description" content="Deploy serverless Postgres branches in 300ms with built-in pgvector support." />
            <link rel="canonical" href="http://127.0.0.1/" />
            </head><body><h1>Serverless Postgres</h1><h2>Instant Branching</h2><a href="/pricing">Pricing</a></body></html>"""
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/pricing":
            body = b"<html><head><title>Pricing - AcmeCloud</title></head><body><h1>Simple usage pricing</h1></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/robots.txt":
            body = b"User-agent: *\nAllow: /\nUser-agent: OAI-SearchBot\nDisallow: /\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()


class CiteReadyTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.target_srv = ThreadingHTTPServer(("127.0.0.1", 0), MockTargetSiteHandler)
        cls.target_port = cls.target_srv.server_address[1]
        cls.t1 = threading.Thread(target=cls.target_srv.serve_forever, daemon=True)
        cls.t1.start()

        class LocalTestableHandler(CiteReadyHandler):
            allow_local_test = True

        os.environ["CITEREADY_MASTER_KEY"] = "TEST-LICENSE-KEY-999"
        cls.app_srv = ThreadingHTTPServer(("127.0.0.1", 0), LocalTestableHandler)
        cls.app_port = cls.app_srv.server_address[1]
        cls.t2 = threading.Thread(target=cls.app_srv.serve_forever, daemon=True)
        cls.t2.start()

    @classmethod
    def tearDownClass(cls):
        cls.target_srv.shutdown()
        cls.app_srv.shutdown()

    def test_robots_ai_blocker_detection(self):
        rb = analyze_robots_txt("User-agent: OAI-SearchBot\nDisallow: /\n\nUser-agent: *\nAllow: /\n")
        self.assertIn("OAI-SearchBot", rb["blocked_bots"])
        self.assertFalse(rb["wildcard_disallow_all"])

    def test_audit_and_fixpack_zip_integrity(self):
        res = audit_url(f"http://127.0.0.1:{self.target_port}", crawl_subpages=2)
        self.assertGreaterEqual(len(res.checks), 11)
        self.assertEqual(sum(c.max_points for c in res.checks), 100)
        # OAI-SearchBot was blocked in mock robots.txt -> ai_robots must fail
        ai_chk = next(c for c in res.checks if c.id == "ai_robots")
        self.assertEqual(ai_chk.status, "fail")

        zbytes = build_fix_pack_zip(res)
        with zipfile.ZipFile(io.BytesIO(zbytes), "r") as zf:
            self.assertIsNone(zf.testzip())
            names = zf.namelist()
            self.assertEqual(len(names), 9)
            llms_file = next(n for n in names if n.endswith("public/llms.txt"))
            llms_txt = zf.read(llms_file).decode("utf-8")
            self.assertIn("AcmeCloud", llms_txt)
            self.assertIn("/pricing", llms_txt)

    def test_web_api_and_license_gate(self):
        base = f"http://127.0.0.1:{self.app_port}"
        target = f"http://127.0.0.1:{self.target_port}"

        # 1. Landing page loads
        with urllib.request.urlopen(f"{base}/") as r:
            html_txt = r.read().decode("utf-8")
            self.assertEqual(r.status, 200)
            self.assertIn("CiteReady", html_txt)

        # 2. Audit endpoint returns JSON + preview snippets
        with urllib.request.urlopen(f"{base}/api/audit?url={urllib.parse.quote(target)}") as r:
            payload = json.loads(r.read().decode("utf-8"))
            self.assertIn("audit", payload)
            self.assertIn("llms_excerpt", payload["preview"])

        # 3. Invalid license key returns HTTP 403
        bad_req = urllib.request.Request(
            f"{base}/api/unlock",
            data=json.dumps({"url": target, "license_key": "WRONG-KEY"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(bad_req)
        self.assertEqual(ctx.exception.code, 403)

        # 4. Valid license key returns valid 9-file binary ZIP
        good_req = urllib.request.Request(
            f"{base}/api/unlock",
            data=json.dumps({"url": target, "license_key": "TEST-LICENSE-KEY-999"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(good_req) as r:
            self.assertEqual(r.status, 200)
            self.assertEqual(r.headers.get("Content-Type"), "application/zip")
            zdata = r.read()
        with zipfile.ZipFile(io.BytesIO(zdata), "r") as zf:
            self.assertIsNone(zf.testzip())
            self.assertEqual(len(zf.namelist()), 9)

    def test_cloudflare_worker_syntax_and_pkzip_crc32(self):
        worker_path = ROOT / "web" / "worker.js"
        self.assertTrue(worker_path.exists(), "web/worker.js must be built before running tests")

        node_script = (
            "import('./web/worker.js').then(m => {"
            "  const z = m.buildZipArchive('demo-pack', {'public/llms.txt': '# Hello World\\n', 'AUDIT_REPORT.md': 'OK'});"
            "  process.stdout.write(Buffer.from(z));"
            "});"
        )
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", node_script],
            cwd=str(ROOT),
            capture_output=True,
            check=True,
        )
        with zipfile.ZipFile(io.BytesIO(proc.stdout), "r") as zf:
            self.assertIsNone(zf.testzip())  # Verifies IEEE CRC32 & headers byte-for-byte!
            self.assertEqual(zf.read("demo-pack/public/llms.txt").decode("utf-8"), "# Hello World\n")


if __name__ == "__main__":
    unittest.main()
