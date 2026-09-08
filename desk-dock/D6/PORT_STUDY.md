# Precision 5680 port orientation study — D6

The two Thunderbolt ports belong on the **keyboard-left** edge. In the user's closed, hinge-down, lid-facing setup, that edge is on the **right of the image**, at the far docking end. The USB-C port on the opposite edge is USB 3.2 Gen 2 / DisplayPort, not Thunderbolt.

## Evidence

- [Dell owner's manual, left view](https://www.dell.com/support/manuals/en-us/precision-16-5680-laptop/precision-5680-owners-manual/left?guid=guid-12cd14bb-8db3-47d7-a090-15d75787517a&lang=en-us): HDMI, audio, two Thunderbolt 4 ports, optional Smartcard reader.
- [Dell owner's manual, right view](https://www.dell.com/support/manuals/en-us/precision-16-5680-laptop/precision-5680-owners-manual/right?guid=guid-f0efa586-1b43-447c-a299-f188f5e5c5a5&lang=en-us): SD reader, one USB-C / DisplayPort port and lock slot.
- [Dell-linked visualization mesh](https://content.hmxmedia.com/precision-16-5680-laptop-AR/gltf/precision-16-5680-laptop-AR.glb), downloaded again on 2026-09-08. Decompressed SHA-256: `f201f10ae03de3ec4aefffcc14745deb65b97b597bdba02c8d4b449e4937648a`. It matches the mesh recorded by D1. The earlier report's future retrieval date was not reused.
- The user's local reference photo places the cable on image-right. It is retained outside the repository in the local transfer folder.

## Cause of the wrong-side model

D5 places both ports at construction x=0, then mirrors every solid about the laptop mid-width plane. This makes the exported model a reflected laptop. Its validation checked the reflected expectation, so it passed without establishing actual handedness.

The still-image renderer also used the reversed camera-right vector (`camera × up`). That reversed the image and concealed the CAD reflection. The browser uses standard camera projection, exposing the discrepancy. The browser's software fallback uses the same Three.js camera matrices and was not the cause.

D6 removes the CAD reflection, corrects the raster camera basis to `up × camera`, and reverses docking/withdrawal and plug-detail camera positions consistently. The viewer is exported from the same CAD solids.

## Re-extracted port centers

Millimeters from the rear-case datum, excluding the projecting hinge lip. Thickness coordinates are relative to the nominal closed-laptop midplane. These are visualization-mesh measurements, not toleranced connector drawings.

| Port | Source node | Source side | Distance from rear case | Thickness coordinate |
|---|---|---|---:|---:|
| Rear Thunderbolt 4, chosen docking port | Dell4768 | −X, keyboard-left | 65.979 | +2.231 |
| Front Thunderbolt 4 | Dell4694 | −X, keyboard-left | 82.192 | +1.915 |
| Opposite USB-C / DisplayPort | Dell4638 | +X, keyboard-right | 39.074 | +2.807 |

The second Thunderbolt port has its own thickness coordinate; D5 reused the first port's coordinate for both. D6 models all three rounded USB-C openings and retains each center. HDMI, audio, card slots and the laptop's internal structure remain outside the simplified reference model.

## Coordinate contract

Translate the source mesh by `(W/2, −T/2, −rear_datum)` to the untilted case frame, then add seat height and apply the 5° rigid lean. The linear transform has determinant +1; no reflection is allowed.

- x=0 is keyboard-left and the plug station. x=W is keyboard-right.
- +Y is the lid, user and fans. −Y is the bottom cover and intake grilles.
- +Z is upward. The hinge is down.
- The plug enters along +X; the laptop slides along −X to dock and +18 mm to withdraw.
- A camera on +Y with +Z up must show x=0 on screen-right.

`port-study.json` retains raw bounds, node identities, source coordinates and transformation provenance. `validate.py` probes actual exported port voids and solid material on their opposite edges, checks the plug side, and verifies the raster projection independently. The browser exposes the same camera check through `deskDockOrientation()` for development inspection.

Physical connector engagement depth, fit tolerances and seating still require calibration on the user's hardware. Correcting handedness does not qualify a precision-fit print.
