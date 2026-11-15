"""CiteReady Pro CLI — Single-site audit, Fix-Pack ZIP builder, Agency Batch Scanner, and Web Server."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Sequence

from .engine import audit_url, build_fix_pack_zip, generate_fix_files


def cmd_scan(args: argparse.Namespace) -> int:
    res = audit_url(args.url, crawl_subpages=args.subpages)
    if args.json:
        print(json.dumps(res.to_dict(), indent=2))
    else:
        print(f"\n=== CiteReady Audit: {res.final_url} ===")
        print(f"Score: {res.score}/100 (Grade {res.grade}) | Latency: {res.response_ms}ms\n")
        for c in res.checks:
            tag = {"pass": "[PASS]", "warn": "[WARN]", "fail": "[FAIL]"}[c.status]
            print(f"  {tag:6} ({c.points:2}/{c.max_points:2}) {c.title} — {c.evidence}")

    if args.out_zip:
        zbytes = build_fix_pack_zip(res)
        out_p = pathlib.Path(args.out_zip)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        out_p.write_bytes(zbytes)
        if not args.json:
            print(f"\n[+] Wrote Fix-Pack ZIP ({len(zbytes):,} bytes) -> {out_p}")

    if args.out_dir:
        out_d = pathlib.Path(args.out_dir)
        files = generate_fix_files(res)
        for rel, content in files.items():
            fp = out_d / rel
            fp.parent.mkdir(parents=True, exist_ok=True)
            fp.write_text(content, encoding="utf-8")
        if not args.json:
            print(f"[+] Extracted {len(files)} drop-in files -> {out_d}")

    if args.min_score and res.score < args.min_score:
        return 2
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    in_path = pathlib.Path(args.input_file)
    urls = [ln.strip() for ln in in_path.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.strip().startswith("#")]
    out_dir = pathlib.Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = []

    for u in urls:
        try:
            r = audit_url(u, crawl_subpages=3)
            zpath = out_dir / f"{r.root_domain.replace('.', '-')}-fixpack.zip"
            zpath.write_bytes(build_fix_pack_zip(r))
            summary.append({"url": r.final_url, "domain": r.root_domain, "score": r.score, "grade": r.grade, "zip": str(zpath)})
            print(f"[OK] {r.root_domain:28} | {r.score:3}/100 ({r.grade}) -> {zpath.name}")
        except Exception as exc:
            summary.append({"url": u, "error": str(exc)})
            print(f"[ERR] {u:27} | {exc}")

    report_json = out_dir / "batch_summary.json"
    report_json.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\n[+] Batch summary saved -> {report_json}")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    from .server import run_server
    run_server(host=args.host, port=args.port)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="citeready", description="CiteReady Pro — AI Search (GEO), Schema, Security & DMARC Fix-Pack Engine")
    sub = p.add_subparsers(dest="cmd", required=True)

    s_scan = sub.add_parser("scan", help="Audit a live URL and optionally output a Fix-Pack ZIP")
    s_scan.add_argument("url", help="Target website URL or domain")
    s_scan.add_argument("--subpages", type=int, default=4, help="Max internal pages to crawl for llms-full.txt (default: 4)")
    s_scan.add_argument("--out-zip", help="Write tailored Fix-Pack ZIP to this file path")
    s_scan.add_argument("--out-dir", help="Write extracted drop-in files to this directory")
    s_scan.add_argument("--min-score", type=int, default=0, help="Exit code 2 if score is below threshold (CI gate)")
    s_scan.add_argument("--json", action="store_true", help="Print raw JSON output")
    s_scan.set_defaults(func=cmd_scan)

    s_batch = sub.add_parser("batch", help="Audit a list of domains and generate Agency Fix-Pack ZIPs")
    s_batch.add_argument("input_file", help="Text file with one URL/domain per line")
    s_batch.add_argument("--out-dir", default="agency_packs", help="Output directory for generated ZIP packs")
    s_batch.set_defaults(func=cmd_batch)

    s_serve = sub.add_parser("serve", help="Run the CiteReady interactive web dashboard locally")
    s_serve.add_argument("--host", default="127.0.0.1")
    s_serve.add_argument("--port", type=int, default=8787)
    s_serve.set_defaults(func=cmd_serve)

    parsed = p.parse_args(argv)
    return parsed.func(parsed)


if __name__ == "__main__":
    sys.exit(main())
