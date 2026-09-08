# D7 review and assembly

D7 uses the plenum as the laptop support and fan enclosure. The laptop leans 5 degrees onto compliant plenum contacts; the fans retain their 18-degree plane. The underside intake stays open, and the continuous low lip keeps the loading end clear.

Each fan drops into an oversized, open-top pocket. Its grille slides down the front rails and closes the top with an integral return. Two small friction lands retain the grille without loose fan hardware. Remove the laptop before lifting a grille and fan along the inclined service path; allow approximately 140 mm of travel.

The bottom covers open the ducts. Their edge saddles close around laid-in fan wires, so connectors do not pass through small holes. Shell-mounted tie lugs retain the fan leads while the covers are removed. Keep the USB cable's service loop separate from these lugs and free through the breakaway motion.

The connector holder uses broad locating surfaces and a replaceable keyed shim for measured height, depth and lateral calibration. One printed coarse lock clamps the stack. A lift-off cap grips the overmold and uses a transverse push pin. A separate fixed chassis stop carries seated docking load. See the [cassette guide](CASSETTE_ASSEMBLY.md).

The resettable hinge separates the alignment surfaces from a replaceable preload spring. It targets at most 0.20 mm axial movement under 20 N and a 50 N-class misalignment release. The actual release depends on load direction, print fit, friction, temperature and preload. It is not an omnidirectional force limiter or an impact-force ceiling. Use the [holder and breakaway study](arm-study/HOLDER_AND_BREAKAWAY.md) for the mechanism, calculations and detached bench checks.

## Intended assembly

1. Print and fit the coarse-thread, cap-pin, grille and panel interfaces first.
2. Join the plenum halves with the deck bridges and printed locks. Lay the fan leads through the open edge passages, fit the panel seals and close the bottom covers.
3. Lower the fans into their pockets, leave accessible lead loops or disconnects, and slide the grilles down to their stops.
4. Assemble the carrier, cam hinge, unloaded printed spring and large axle. Set preload only within the shoulder limit described in the breakaway guide.
5. Fit the keyed cassette shim, original cable, cap and push pin. Install the independent stop and its compliant tip.
6. Check holder movement, release and repeatable reset with a dummy plug and measured load before introducing the laptop. Then calibrate the real plug and chassis stop with the laptop supported.

Panel, bridge and cassette locks use custom 8 x 2 mm printed threads with 6.7 mm cores. The chassis stop and hinge preload interface use 10 mm threads; the hinge axle is 10 mm and the cap pin is 6.5 mm. These are matched printed interfaces, not ISO metric hardware. The [cassette guide](CASSETTE_ASSEMBLY.md) gives the exact fits.

## What to inspect

Use the viewer's assembled, fan service, exploded, intake and plug-detail views. Exploded offsets show parts; they do not establish removal paths. Inspect the original port handedness, intended soft contacts, intake and rubber-foot clearance, access to hand controls, fan retention, and free USB cable travel.

The current [geometry validation](validation.json), [service checks](service-validation.json), [bearing checks](alignment-validation.json) and [airflow screen](airflow-sizing.json) record their own scope. The [isolated fan/body check](service_isolated_validation.json) identifies the intentional grille friction contacts. Refer to the regenerated [geometry](geometry.json) and [print manifests](print-manifest.json) for current parts and dimensions.

These checks do not qualify PETG fit, warm creep, vibration retention, desk stability, connector pull retention, release force or cooling. The package remains unsliced; OrcaSlicer was not relaunched after its crash and no printer was used. Follow [print preparation](PRINT_PREPARATION.md), then validate the physical prototype. The [source port study](../D6/PORT_STUDY.md), [airflow study](../D6/AIRFLOW_STUDY.md) and [material/load audit](arm-study/material-load-sources.md) retain the evidence and assumptions.
