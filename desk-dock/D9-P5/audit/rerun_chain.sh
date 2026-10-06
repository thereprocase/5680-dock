#!/usr/bin/env bash
# After a green build_d9.py: reslice, audit plates, run the release gate (expected to stop at
# the legacy enclosure audit), regenerate and validate the viewer, publish it to docs, render
# the clamp views and the loosened sweep. Run from desk-dock/D9-P5.
set -u
cd "$(dirname "$0")/.."
C=~/.local/bin/cadpy
rm -rf plates
$C prepare_and_slice.py > audit/slice.log 2>&1 || { echo "SLICE FAILED"; tail -5 audit/slice.log; exit 1; }
$C verify_plates.py > audit/verify_plates.log 2>&1 || { echo "PLATE AUDIT FAILED"; tail -5 audit/verify_plates.log; exit 1; }
grep -v '^{' audit/verify_plates.log
$C verify_enclosure.py > audit/enclosure.log 2>&1; echo "enclosure gate exit $? (fails on main too)"
$C verify_and_package.py > audit/package.log 2>&1; echo "package gate exit $?"; grep -o "AssertionError.*" audit/package.log | head -1
rm -rf viewer-export && $C export_viewer_p5.py viewer-export > audit/viewer.log 2>&1 && tail -1 audit/viewer.log
$C validate_viewer_bundle.py viewer-export && cp viewer-export/model.bin viewer-export/model.json viewer-export/provenance.json ../../docs/models/desk-dock-p5/ && $C validate_viewer_bundle.py ../../docs/models/desk-dock-p5
$C audit/clamp_views.py > audit/views.log 2>&1 && tail -6 audit/views.log
$C audit/reach_and_sweep.py > audit/sweep.log 2>&1; tail -4 audit/sweep.log
echo CHAIN DONE
