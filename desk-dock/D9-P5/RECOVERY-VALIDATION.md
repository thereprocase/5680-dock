# Salvage verification - 20 September 2026

The supplied `5680-dock-codex-splice-fixes-salvage.zip` was recovered against
base `562aeb326c1f24a4886cca85b368fced76bc955f`. Its SHA-256 is
`6c8f1308c7a32ba4290469ed1dc1eb466ae008dacd3a096654ece5456c6a3449`.

The preferred mail patch was applied as commit
`b90d7e7206b07ca2359356338fc0e4191b615ec1`, retaining the supplied author,
author date and title. The commit ID differs from the reconstructed handoff
commit because it has a new committer timestamp. Independently applying the
binary fallback patch to the base index produced exactly the same tree:
`60fe3210691bc29638b73977fad137973ee442d1`. Later pipeline/documentation
corrections are a separate commit so the recovery itself remains inspectable.

## Rebuild results

Windows Python 3.12, CadQuery 2.8.0 and trimesh 5.1.0 completed the full build.
All 48 installed printed parts exported as valid single solids and watertight
STLs. Part interference, sampled insertion conflicts, laptop overlap and fan
interference were empty/zero. Both fan-seat gap audits were 0.0 mm3.

| Arc | Shell | Positive engagement (mm3) |
| --- | --- | ---: |
| Back | M1 | 2872.4 |
| Front | M2 | 265.2 |
| Fan | M1 | 297.6 |
| Floor | M2 | 181.3 |

Joint fill was 4923.1 of 4929.1 mm3, leaving 5.9 mm3 in the intentional key
clearances. Nominal air volumes were M1 770257.4017438883 mm3 and M2
786384.4889101831 mm3, unchanged from the base rebuild within floating-point
precision; the M1 last-digit difference from the handoff is below 1e-9 mm3.

## Viewer recovery

The published assets remain the recovered 582312-byte binary, revision
`D9-P5-CODEX-SPLICE-LAP-AND-PRINT-POSE`, with cache key `cleanup-20260920f`.
The 51 entries comprise 48 printed bodies, the laptop and two fan references.
All offsets, lengths, index ranges and binary coverage were checked.

A separate local re-export produced 581256 bytes. Its entries and bounds
match, but three parts have different coarse tessellation counts (M2 outer
cradle, accessory socket, accessory clamp bolt); some other entries differ in
vertex ordering. Both binary layouts validate. Byte-for-byte local export
reproducibility is **not claimed**. The re-export was retained separately and
did not overwrite the supplied asset or its provenance.

## Orca review candidates

Native Orca successfully sliced one optional fit/alternate plate and nine
assembly plates from the rebuilt STLs. The 48 installed parts appear exactly
once across plates 01-09. All ten actual-G-code audits passed placement,
orientation, build height, usable bed/exclusion-zone and embedded-G-code checks.
Per-object support and bridge counts are in `plates-verification.json`.
Plate 06 and 09 toolpath previews were visually inspected; this is not a
complete physical support-access or native-GUI review.

Follow-up source fixes remove obsolete plate labels/counts, use the verifier
shipped in this repository, reject any failed plate audit, reserve 12-mm
inter-part spacing and the front-left exclusion zone, and stop packaging
before creating a release directory when required gates fail.

The frozen profile is Generic PETG Starter. The soft-tip geometry included on
plate 09 requires a separate flexible-material slice for use as a soft bumper.
These slices are review candidates, not a released production print kit.

## Enclosure gate and remaining qualification

`verify_enclosure.py` fails for M1 and M2 on **both** the base rebuild and the
recovered rebuild. With both named ports capped, the test still finds the
target air connected to the exterior. Target-overlap values match between the
two revisions; this is not a newly introduced failure from the splice patch.
The legacy test evaluates two bare shell solids and no cured epoxy. It does
not establish that the bonded assembly seals, and no replacement sealing
audit or physical airtightness test has been completed.

The package verifier was run and correctly stopped at this enclosure gate.
No verified production ZIP was generated or published. Resolve and re-audit
the bonded-seam sealing model before releasing a production kit.

Physical thread fit/durability, clamp loads, socket capacity, epoxy procedure,
loaded laptop support, fan screw retention, cooling, support removal and
docking/plug alignment remain unqualified. No printer was operated.
