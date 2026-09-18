# D8 R7: peg bracket, 8-degree lean (supersedes R6)

**18 September 2026.** User concept: drop-in pegs with a bearing foot and a
fence head give a moment connection to the frame without an extra backing
fence, so the stand is as slim as the fence allows.

## Pieces

| Piece | Per | What it is |
| --- | --- | --- |
| Frame | dock end (identical) | base, brace, tower whose top is the deck (z 51), 8-degree lid rail, 6-mm outer wall; two 22-mm channels along X in the tower top: 6 mm under the fence line, 13 mm under the seat |
| Fence peg | machine and end | a plank: 5.4-mm foot in the fence channel, 6-mm wall standing on the deck, 64 mm tall at the plug end, 15 mm at the far end. Thickness differences: offset the wall from the foot |
| Seat peg | machine | 12.4-mm foot in the seat channel, R2 seat curve with the V5 C relief above. Hinge differences: change the head |
| Pin | end | one 36-mm D9 fan pin from the outer face through the outer wall (6), fence foot (6), tower web (8.3) and seat foot (13), ending 2.7 mm into the tower beyond: a double-supported shear pin |

Peg bores sit 0.15 mm lower than the frame bore, so driving the pin cams both
pegs down onto the deck: no rattle in use. Disassembly: pull the pin by its
lugged head and lift the pegs; 4-mm push-out holes under both channels take a
rod if a foot ever sticks. Outer face of the stand at the socket: unleaned
y = -25.3 mm (R6 with its backing wall was -32.6).

Receipts in `checks.json`: pegs blocked within 2 mm in all six directions by
frame plus pin; cam interference below 0.1 mm3; laptop, rubber-foot, keepout
and lift checks clean at 8 degrees; plug-end fence catches a tipping laptop
from 4 degrees; docking sweep 8.5 mm clear at the plug end, 0.47 mm through
the far end (hence the short far peg).

`--d9-source --base-thickness 4 --tag d9-source --lock-x 16` writes the frame,
the pegs and the socket void (channels, pin bore, push-outs) that D9 P5
subtracts from its fused cradle, all with the bore centred on the 16-mm crop.
Nominal CAD only; pegs are not yet dressed with fillets.
