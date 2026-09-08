# Plug-arm load and printed PETG inputs

Research checked 2026-09-08. Sources below are USB-IF, connector/filament
manufacturers, and an original experimental paper. The actual PETG brand,
printing quality, arm temperature and Dell connector forces remain unmeasured.

## Calculation inputs to use now

- Treat **20 N** as a provisional axial design scenario informed by ordinary
  USB-C mating tests. It is not a guaranteed force limit for this mechanical
  dock. Friction, misalignment, cable reaction and a user's off-axis push can add
  loads absent from a bare connector test.
- Add **40 N** as a chosen overload sensitivity, not a measured Dell force or
  a standard mating requirement. In a linear model it doubles the 20 N stress
  and deflection. Check the printed arm separately from the laptop: do not
  apply a 40 N proof load through the laptop port.
- Use **E = 0.8, 1.2, 1.5 and 1.8 GPa** as explicitly assumed stiffness cases.
  The 1.5 GPa case is consistent with one manufacturer's printed PETG tensile
  data. The lower cases are engineering sensitivity values, not measured warm
  moduli for the user's spool. Some printed PETG formulations exceed 2 GPa.
- The sweep is not a validated temperature model or confidence interval. Do not
  label 0.8 GPa as the modulus at a particular temperature. The linear-elastic
  calculation also does not predict creep, joint slip, rail clearance or local
  indentation. At otherwise identical conditions its predicted deflection
  changes by 2.25 times between E = 1.8 and 0.8 GPa.
- Identify whether the analyzed section is a solid wall, explicitly hollow CAD
  section, or partially filled printed volume. A solid-coupon material modulus
  does not make a 20%-infill gross section solid. Use actual walls/voids for the
  bending section and avoid counting sparse infill as fully dense PETG.

## USB-C force evidence

### Current literal standard: USB-IF Release 2.5

[USB-IF official Release 2.5 page](https://www.usb.org/document-library/usb-type-cr-cable-and-connector-specification-release-25)
links the [March 2026 release archive](https://www.usb.org/sites/default/files/USB%20Type-C%202.5%20Release%20202603.zip),
posted 2026-04-08. The clean 442-page PDF was downloaded directly and read;
page 136, sections 3.8.1.1-3.8.1.3, states these **requirements, not measurements**:

| Quantity | Value and conditions |
|---|---|
| Initial insertion | 5-20 N; EIA 364-13; maximum 12.5 mm/min |
| Initial extraction | 8-20 N after five conditioning cycles, measured on sixth extraction |
| Later early extraction | On extraction 32, within 33% of initial result and still 8-20 N |
| Extraction after durability | 6-20 N after 10,000 cycles; maximum 12.5 mm/min |
| Durability cycling | At least 10,000 cycles; 500 +/- 50 cycles/hour |

Both force clauses exclude docking applications. They inform this prototype's
load cases without guaranteeing its total operating force. Section 3.8.1.5's
40 N for one minute concerns **cable pull-out/strain relief with the plug
clamped**, not connector extraction or permissible load on a Dell port.

Archive retrieval initially returned 403, then succeeded with a normal browser
User-Agent and public USB-IF referer. No authentication was needed. Local
reference PDF: `D:/codex-work/scratch/usb-c-load-research/USB Type-C Spec R2.5 - March 2026.pdf`.
SHA-256: `6636cd61387a2f78b0fa96c8ea86ccc0f39ec59f98821cdb57b206d31445a328`.

The independently accessible [USB-IF Compliance Document Rev. 2.1b, June 2021](https://www.usb.org/sites/default/files/USB%20Type-C_Compliance%20Document_Rev_2_1b_June_2021.pdf),
page 14 Table 3-2 and pages 34-35 Table 4-7, gives the same force ranges and
measurement speed. It describes the docking exception as direct docking
without a cable. This is the compliance document currently linked in the USB-IF
library; its 2025 listing date does not change its printed June 2021 revision.

### Actual measured USB-C plug test: Molex 2188470001

[Molex test summary revision A, 2022-12-28](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/productspecificationpdf/218/218847/2188470001TS-000.pdf?inline=),
sheet 9, Group E, reports **measured results for five specimens**. The methods
on sheet 4 specify 12.5 mm/min. Sheet 13 identifies a HongHaiKeJi MC-1220S force
tester; numerical room temperature/humidity are not supplied.

| Measured force, N | Minimum | Average | Maximum |
|---|---:|---:|---:|
| Insertion after preconditioning | 11.39 | 11.95 | 12.64 |
| Early extraction | 14.93 | 15.69 | 16.32 |
| Extraction after 25 additional cycles | 14.57 | 15.31 | 16.02 |
| Extraction after durability to 10,000 cycles | 11.05 | 11.46 | 12.42 |

This is a 24-pin vertical SMT **plug**, not an identified Dell cable. It supplies
summary statistics, not individual sample traces or force-displacement curves.
Those measured columns must not be confused with the adjacent specification
column (5-20 N / 8-20 N / 6-20 N).

### Actual measured USB-C receptacle test: Molex 204711 family

[Molex 2047110001-TS revision B, 2024-12-24](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/testsummarypdf/204/204711/2047110001-TS-000.pdf?inline=),
sheet 7 Group E, supplies another five-specimen result set:

| Measured extraction force, N | Minimum | Average | Maximum |
|---|---:|---:|---:|
| Following initial conditioning | 12.20 | 13.78 | 15.70 |
| Following 25-cycle stage | 13.00 | 14.32 | 16.10 |
| Following stage labeled 2,500 cycles | 7.90 | 8.58 | 10.20 |
| Following stage labeled 5,000 cycles | 6.30 | 7.34 | 8.80 |
| Following stage labeled 7,500 cycles | 6.70 | 7.44 | 8.80 |

This is a receptacle report, with EIA-364 qualification and a Japan Instrument
Max-1KN-H load tester listed. Its summary does not give a numerical force-test
speed/ambient or a mating-plug identity. The final stage is printed as 1,000
cycles after 7,500; the inconsistent label is not silently corrected or used
here. Its insertion test appears in the sequence but no insertion results are
shown in the performance table. These are min/mean/max results, not raw curves.

### Dell evidence and limits of the search

[Dell's connector handling guidance](https://www.dell.com/support/kbdoc/en-us/000198334/how-to-correctly-plug-and-unplug-the-usb-type-c-connector-on-a-dell-dock)
requires straight, aligned insertion/removal and avoiding twist, side pressure
and a taut cable. It provides no force measurements. No public Dell 5680 or
Dell cable force-displacement report was located in this bounded search.

Searches also found standard-range-only cable datasheets, a Micro-B test report
with raw curves (wrong connector family), and mirrored third-party USB-C
receptacle reports whose full curve pages could not be retrieved reliably.
None is being presented as measured Dell or ordinary retail cable data. The
two Molex reports establish real connector-family test results; measuring the
chosen cable in the actual laptop remains the way to establish this dock's
force and alignment needs.

## Printed PETG at ordinary test conditions

### Prusament PETG

[Prusa Polymers technical datasheet v1.1, updated 2022-02-16](https://prusament.com/wp-content/uploads/2022/10/PETG_Prusament_TDS_2021_10_EN.pdf),
pages 2–3, explicitly separates printed-specimen results from filament results:

| Printed specimen property | Horizontal | Vertical XZ, using manufacturer's label |
|---|---:|---:|
| Tensile modulus, ISO 527-1 | 1.5 ± 0.1 GPa | 1.6 ± 0.1 GPa |
| Flexural modulus, ISO 178 | 1.7 ± 0.1 GPa | 1.6 ± 0.1 GPa |

Specimens were made on an Original Prusa i3 MK3 with Slic3r Prusa Edition
1.40.0, 0.20 mm layers, two perimeters, 100% rectilinear infill, no top/bottom
solid layers, 200 mm/s stated speed, 250 °C nozzle and 80 °C bed. The sheet does
not state a numerical mechanical-test ambient temperature. Its 24 °C/22% RH
footnote belongs to moisture absorption, not the tensile table. Keep the
orientation labels; do not silently equate “Vertical XZ” with a pure Z tensile
test. The sheet supplies 68 °C HDT at both 0.45 and 1.8 MPa, not an E(T) curve.

### Polymaker PETG

[Polymaker PETG TDS v2.0, file dated 2025-11-17](https://polymaker.com/wp-content/uploads/lana-downloads/TDS_Polymaker_PETG_V2.0_2025-11-17.pdf)
provides explicit printed XY and Z specimens:

| Printed specimen property | XY | Z |
|---|---:|---:|
| Young's modulus, ISO 527 / GB/T 1040 | 2311.11 ± 92.41 MPa | 2202.91 ± 52.34 MPa |
| Bending modulus, ISO 178 / GB/T 9341 | 2277.34 ± 198.09 MPa | 1958.74 ± 126.39 MPa |

The specimen-making block specifies 240 °C printing temperature, 80 °C bed,
three top/bottom layers, two shells, 100% infill, cooling off and ambient
environment. A numerical ambient temperature is not assigned to that block;
23 °C is separately associated with density/moisture data. The recommended
printing settings are not identical to this specimen protocol. Thermal values
are Tg 71.24 °C by DSC at 10 °C/min; HDT 69 °C at 0.45 MPa and 65 °C at 1.8 MPa.
Neither HDT nor Tg is a guaranteed service temperature or static modulus curve.

## Temperature dependence: original printed-specimen experiment

[Redutko, Kalwik and Szarek, Archives of Metallurgy and Materials 67 (2022), 333–339](https://www.journals.pan.pl/Content/122552/PDF/AMM-2022-1-45-Redutko.pdf?handler=pdf),
DOI [10.24425/amm.2022.137763](https://doi.org/10.24425/amm.2022.137763),
studied PETG and, separately, copper-filled PLA. The unaged PETG control had a
reported storage modulus of **1192 MPa at 67.9 °C**, followed by a sharp drop.
This is dynamic storage modulus E′, not static Young's modulus.

The PETG specimens were printed flat with full infill on a Zortrax M200 Plus:
0.4 mm nozzle, 0.14 mm layers, 245 °C extrusion, 30 °C bed and 40 mm/s. DMA used
three-point bending, 10 Hz, 80 µm amplitude and 2 °C/min heating under ISO 6721.
The paper has inconsistencies in its stated cold endpoint and some E′/E″ prose;
use its warm control result only as evidence that stiffness can decline before
nominal Tg. Do not transfer aged-in-body-fluid data or this specialist PETG
directly to the dock. It does not establish the user's static E at 40 or 50 °C.

## Material-model boundary

The modulus numbers above come from **printed FDM/FFF specimens**, not
injection-molded bulk resin. No injection-molded resin modulus has been used as
the dock's material property. Tensile modulus, flexural modulus and dynamic
storage modulus are distinct measurements; the simple beam calculation's
isotropic E remains an approximation. For final qualification, measure actual
plug insertion/extraction force, arm displacement and arm temperature on a
printed prototype, including a warm held-load check for permanent movement.
