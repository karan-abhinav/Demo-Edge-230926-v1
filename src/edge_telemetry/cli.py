"""Tiny CLI so the labs have something to run and something to break."""

import argparse
import json

from .anomaly import detect
from .features import summarize
from .ingest import device_ids, load_runs
from .store import build


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="edge-telemetry")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("devices", help="list device ids in the CSV")
    sub.add_parser("seed", help="rebuild the SQLite database from the CSV")

    p_sum = sub.add_parser("summary", help="summarise one numeric field")
    p_sum.add_argument("--field", default="temp_c")
    p_sum.add_argument("--device")

    p_det = sub.add_parser("detect", help="list anomalous runs")
    p_det.add_argument("--device")

    args = parser.parse_args(argv)

    if args.command == "devices":
        print("\n".join(device_ids()))
    elif args.command == "seed":
        print(f"inserted {build()} rows")
    elif args.command == "summary":
        print(json.dumps(summarize(load_runs(device_id=args.device), args.field), indent=2))
    elif args.command == "detect":
        print(json.dumps(detect(load_runs(device_id=args.device)), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
