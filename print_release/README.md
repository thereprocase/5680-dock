# Revision G - final native fit-and-finish print set

Print one each of 01-14. STL and 3MF are alternatives for the same part; do not
print both formats. Standard 3MF models contain millimeter geometry and baked
orientation, not slicer settings or G-code.

This is the selected print set. Original root print_ready/ and Fusion/Onshape
ports remain Revision F baseline/history. Six parts are revised: ducts, trays,
and outlet rails. Both cradle/arm files are byte-identical to the already-printed
Revision F files. Caps and four pins are also unchanged.

P1S / ASA: 0.4 mm nozzle, 0.20 mm layers, 6 walls, 6 top/bottom layers, 100% fill
of the explicitly hollow CAD, 8 mm outer brim, supports off. Cradles outer-side
down with the supplied diagonal rotation; ducts inlet down; trays grille down;
caps front down; rails lip down; pins button down. Keep the baked orientations.

Fan-interface and rail-to-arm clearances measure 0.30 mm. Pin retention keeps
its intentional interference; fixed load shoulders retain seating contact.
Separate native loft-skin patches close the unintended duct-wall notches.

Final checks: valid native solids, constrained sketches, unchanged printed arms,
wall continuity, assembly/service clearances, closed meshes, and bed/brim/cutter
fit. Physical fit, ASA bridge quality, retention and slicer paths remain to be
checked. Use the root P1S_ASA_Print_Guide.md for material and assembly guidance.
Original fit coupons remain under print_ready/; full-length tray fit needs its
own check because the revised flank clearance is normal to the dovetail slope.

See manifest.json for hashes tying this print set to the native FCStd document.
