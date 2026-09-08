# Precision 5680 desk dock

**D8 development review:** [removable Y/Z connector module, direct shell feet, lighter covers and explicit print orientations](desk-dock/D8/README.md). See [D8 status and remaining checks](desk-dock/D8/CURRENT_STATUS.md). D8 is not a physically qualified print release; the public viewer and download below still describe D7.

A compact, hinge-down laptop stand built around its cooling plenum. The laptop
leans against the plenum, two recessed fans draw from the hinge exhaust, and a
captured USB-C plug makes the final sideways docking connection.

**[Explore the project](https://thereprocase.github.io/5680-dock/)** ·
**[Open the interactive D7 model](https://thereprocase.github.io/5680-dock/desk-dock.html)** ·
**[Download D7 CAD and print-review package](docs/downloads/Precision_5680_D7_Review.zip)**

## D7 baseline: form follows function

- The laptop leans **5°** on soft plenum contacts. Profiled end seats carry its
  weight; a continuous low lip guides it without a loading-end tab.
- Two **120 × 120 × 25 mm** fans sit in open-top pockets behind slide-in
  grilles. Their discharge stays **18° above the desk**.
- Open bottom covers expose the ducts. Fan wires lay into edge passages;
  shell-mounted tie points keep them clear during service.
- Large printed screws, nuts and pins support hand assembly. A replaceable
  keyed shim sets the original cable's position, and a lift-off cap permits
  cable replacement.
- A resettable printed cam hinge lets the plug holder fold clear after a
  misaligned docking strike. Its separate chassis stop carries seated load.

**Status: an unsliced development prototype.** CAD, sampled motion, interface
and mesh checks are supplied. Printed fits, full-holder stiffness, release
force, stability and cooling have not been physically qualified. The holder's
**≤0.20 mm at 20 N** alignment and **50 N-class** release are test targets,
not demonstrated performance or a protection rating for a mated port.

## Build, inspect, continue

| Start here | What it contains |
|---|---|
| [Project context](PROJECT_CONTEXT.md) | Design decisions, revision history, evidence and next work |
| [D7 design and assembly](desk-dock/D7/REVIEW.md) | Current parts, assembly intent and verification limits |
| [Print preparation](desk-dock/D7/PRINT_PREPARATION.md) | P1S, PETG, 0.4 mm nozzle, poses and fit samples |
| [Holder and breakaway study](desk-dock/D7/arm-study/HOLDER_AND_BREAKAWAY.md) | Load assumptions, calculations and bench acceptance |
| [5680 port study](desk-dock/D6/PORT_STUDY.md) | Correct handedness and source-derived port positions |
| [D7 source](desk-dock/D7/) | Editable CAD, parameters, STEP, individual meshes and validation records |

Use **OrcaSlicer** for deposited-path and support-removal review before printing.
Print the fit samples first. The review archive is also retained at
[`desk-dock/D7/Precision_5680_D7_Review.zip`](desk-dock/D7/Precision_5680_D7_Review.zip).

This repository preserves the earlier 5560 wall-mount work and D1–D6 desk-dock
studies as project history. **D8 is the development revision on this branch.** Old ASA print
guides, wall-mount packages, CFD results and historical “current design” labels
do not qualify D7. The [original 5560 overview](docs/history/5560-README.md) and
Git history remain available for provenance. See [LICENSE](LICENSE).
