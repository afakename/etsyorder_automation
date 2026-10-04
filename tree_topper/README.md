# Universal snowflake tree topper base

- `tree_topper.scad` – parametric source (OpenSCAD). `tree_topper.stl` – ready to print.
- 92 x 92 x 118 mm, prints upright, no supports, fits a 256 mm bed. Single watertight body.
- Spring-like ribbon coil cone with 3 ribs and a base ring; branches can poke out between turns.
- Inside: a 3-lobe spiral bore (~21 mm mean dia, lobes grip a 16-22 mm leader as you twist it on).
- Top: 10.3 x 10.3 mm slot, 50 mm deep, funnel lead-in, 4 crush ribs for friction/snap hold.
- `flake_tab.scad` – glue-on 10 x 10 mm tab for flakes without a suitable arm.

Tune at the top of the scad file: `fit` (looser/tighter arm), `bore_r` (leader size), `slot_depth`,
`pin_d` (cross hole for a pin), `base_r`, `H`. Print PETG or PLA, 4 walls, 20-30% infill.
First print tip: do a 20 mm tall slice test of the slot/bore to check fit before the full part.
Re-export: `openscad -o tree_topper.stl tree_topper.scad` (~2 min).
