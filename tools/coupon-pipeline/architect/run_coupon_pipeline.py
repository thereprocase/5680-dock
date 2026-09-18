"""One-command coupon pipeline: place, slice, verify, audit IDs, package.

Run with the Windows CAD python (see ~/.local/bin/cadpy). Example:

  cadpy run_coupon_pipeline.py --profiles profiles/coupon-fast --out v6-orca \
      --stl ../geometry/profile-v5/generated/C_R2_full_rail_plus_3p5mm_plus_1mm_seat_relief_X_to_print_Z.stl \
      --geometry-dir ../geometry/profile-v5 --review ../architect/V5-GEOMETRY-REVIEW.md \
      --readme V5-PRINT-KIT-README.md --package ../../../outputs/5680-design-team/PRINT-ME-V5-C-ONLY \
      --title "V5 C ONLY - RAIL +3.5MM"

Any 1..3 print-oriented STLs from the same geometry directory. Every stage is
the existing reviewed script; this only sequences them and stops on the first
failure. Packaging is optional (omit --package to stop after the audits).
"""
from pathlib import Path
import argparse
import json
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
AUDIT = ROOT / "work/quartet-team/verification/audit_v5_id_holes.py"


def run(step, command):
    print(f"\n== {step}", flush=True)
    result = subprocess.run([sys.executable, *map(str, command)], cwd=HERE)
    if result.returncode != 0:
        sys.exit(f"{step} failed with exit code {result.returncode}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--stl", action="append", type=Path, required=True, help="1..3 print-oriented STLs")
    parser.add_argument("--profiles", type=Path, required=True, help="folder with machine/process/filament/profile-selection.json")
    parser.add_argument("--out", type=Path, required=True, help="new slice folder (must not exist)")
    parser.add_argument("--review", type=Path, required=True, help="geometry review receipt markdown")
    parser.add_argument("--geometry-dir", type=Path, help="geometry folder holding generated/manifest.json (needed for --package)")
    parser.add_argument("--readme", type=Path, help="kit README (needed for --package)")
    parser.add_argument("--package", type=Path, help="package output folder (also writes <folder>.zip)")
    parser.add_argument("--title", default="FIT COUPONS", help="plate name written into OPEN-ME.3mf")
    args = parser.parse_args()
    out = args.out.resolve()
    run("prepare plate", ["prepare_coupon_plate.py", *sum([["--stl", p.resolve()] for p in args.stl], []),
                          "--profiles", args.profiles.resolve(), "--review-receipt", args.review.resolve(), "--out", out])
    run("orca slice", ["run_coupon_orca.py", "--slice-dir", out])
    run("toolpath verification", ["verify_coupon_plate.py", "--dir", out])
    run("identifier audit", [AUDIT, "--folder", out, "--json", out / "id-hole-verification.json", "--png", out / "id-holes-toolpaths.png"])
    summary = json.loads((out / "toolpath-verification.json").read_text(encoding="utf-8"))["summary"]
    print("\n".join(summary))
    if args.package:
        if not (args.geometry_dir and args.readme):
            sys.exit("--package needs --geometry-dir and --readme")
        for name in ("id-hole-verification.md", "verification-coordinate-correction.md"):
            source = HERE / "v5-orca" / name
            if source.is_file() and not (out / name).exists():
                (out / name).write_bytes(source.read_bytes())
        run("package", ["package_coupon_plate_v5.py", "--slice-dir", out, "--geometry-dir", args.geometry_dir.resolve(),
                        "--readme", args.readme.resolve(), "--out", args.package.resolve(), "--title", args.title])
    print("\nDONE:", out)


if __name__ == "__main__":
    main()
