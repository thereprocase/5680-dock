# Compact plenum study — 5° laptop lean, 18° fan discharge

The selected local candidate moves the fan centers from y=95 mm to y=58 mm: **37 mm inward**. The laptop leans 5° onto the plenum, and the fan tops lean toward it at 18° from vertical. The upper suction-face edge is **14.8 mm from the lid**, measured normal to the lid plane.

The two connected cavities total **1.82 L**, down from 3.17 L in the first wide local D6. Cavity volume alone is not an airflow criterion. The lower passage is retained to feed the fans, while the upper space tapers as less flow remains to feed the upper part of each disk.

## How far to push it

The table holds the final 5°/18° angles fixed. Fan-center y is the CAD datum, not the full enclosure depth.

| Fan-center y | Fan-top gap to lid | Analytical upper inlet clearance | Screen |
|---:|---:|---:|---|
| 70 mm | 26.7 mm | 25.2 mm | Roomy |
| 64 mm | 20.8 mm | 18.7 mm | Pass |
| 60 mm | 16.8 mm | 14.4 mm | Pass |
| **58 mm** | **14.8 mm** | **12.3 mm** | **Selected compact candidate** |
| 56 mm | 12.8 mm | 10.1 mm | Below chosen inlet allowance |
| 54 mm | 10.8 mm | 7.9 mm | Below chosen inlet allowance |
| 52 mm | 8.8 mm | 5.8 mm | Very restricted upper inlet |

This is the thinnest sampled candidate meeting the chosen **12 mm inlet-clearance allowance** and a **2 m/s maximum upper-feeder velocity** at an assumed 30 CFM total. These are engineering screening choices, not experimentally established performance limits. The practical minimum could move in either direction after testing.

## CAD and flow checks

Each branch is a single connected valid cavity. Normal rays through the CAD cavity are sampled at the fan center and five radii, with 16 angles on each radius: **81 rays per fan**. The selected candidate has **12.5 mm minimum sampled clear depth** and **35.5 mm at the fan axis**. The corners of the fan frame are not the rotating airflow aperture.

At an assumed equal 15 CFM per branch:

- The smaller hinge mouth has 2.59 m/s velocity; its area and rounded opening remain unchanged.
- The lower transfer section carries about 0.74 m/s in the smaller branch.
- A uniform fan-disk loading assumption gives a maximum upper-feeder velocity of about 0.94 m/s. This continuity screen does not predict actual inlet-flow distribution.
- The inherited baseline loss-coefficient sensitivity gives approximately 3.1–7.3 Pa for the smaller branch. **That is not a reliable bound on close-inlet system effects**; distorted inflow, laptop resistance, leakage and acoustics remain outside the calculation.

`airflow.py` reproduces the sweep, measured CAD clearances and 20/30/40 CFM sensitivity in `airflow-sizing.json`.

## Why leave any space

[Fantech's installation guidance](https://www.fantech.com.au/Content.aspx?ContentID=L5&category=dos-and-donts) explains that restricted or uneven entry can starve part of a fan and degrade performance or noise. It does not establish a safe minimum gap for this enclosure.

As one example of the slim fan class, the [Noctua NF-A12x15 PWM specification](https://www.noctua.at/en/products/nf-a12x15-pwm/specifications) gives 55.44 CFM maximum free-air flow and 1.53 mm water maximum static pressure (about 15 Pa). Those are different operating endpoints; they do not establish flow through this laptop and plenum. Two fans in parallel do not double available pressure. The user's actual fan model is not yet established.

## Physical validation needed

The model is a compact development candidate, not a demonstrated airflow optimum. A prototype should compare branch flow, plenum pressure, laptop temperatures and sound at fixed laptop load and fan speed. Test fans-off behavior and seal leakage too. A small spacer that adds 4–6 mm behind the fan would make a useful comparison against this compact candidate; it is not included as qualified hardware in this revision.

The direct plenum bearing, source-handed ports and sampled docking clearances remain checked at the final angles. Desk-edge stability, wall strength, fastening and physical fit remain open.
