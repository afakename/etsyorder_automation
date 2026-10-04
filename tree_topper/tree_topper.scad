// Universal snowflake tree topper base  (print upright, no supports needed)
// A conical "spring" cone with a twist-on leader grip inside and a
// rectangular slot at the top that takes any flake's 10 x 10 mm arm.
// All dimensions in mm.  Tune the parameters below and re-export.

// ---- flake arm ----
arm_w      = 10;     // arm width
arm_t      = 10;     // arm thickness
fit        = 0.15;   // clearance per side (raise if arm won't enter)
slot_depth = 50;     // how deep the arm sits (deeper = steadier)
rib_h      = 0.30;   // crush-rib height on the two broad faces (friction/snap)
pin_d      = 0;      // >0 adds a cross hole for an optional locking pin

// ---- tree leader grip ----
bore_r     = 10.5;   // mean bore radius (leader / branch bundle ~ 16-22 mm)
lobe       = 1.8;    // depth of the spiral grip lobes
lobes      = 3;      // number of spiral lobes
bore_depth = 62;
thread_pitch = 22;   // axial travel per full twist of the grip spiral

// ---- cone ----
H          = 118;    // overall height
core_d1    = 40;     // core diameter at bottom
core_d2    = 32;     // core diameter at top
base_r     = 46;     // outer radius of cone at base (9" flake: wide base = stable)
coil_turns = 4.5;
wire_w     = 7;      // coil width (radial)
wire_h     = 6;      // coil height (axial)
struts     = 3;      // straight ribs that tie the coil to the core

$fn = 64;
core_r = function(z) (core_d1 + (core_d2-core_d1)*z/H)/2;
cone_r = function(z) base_r - (base_r - core_r(H-8))*z/(H-8);

module core() {
  difference() {
    cylinder(d1=core_d1, d2=core_d2, h=H);
    // spiral-lobed leader bore, opens at the bottom
    translate([0,0,-0.01])
      linear_extrude(height=bore_depth, twist=-360*bore_depth/thread_pitch, slices=bore_depth*3, convexity=10)
        polygon([for (a=[0:3:359]) let(r=bore_r+lobe*cos(lobes*a)) [r*cos(a), r*sin(a)]]);
    // lead-in chamfer for the bore
    translate([0,0,-0.01]) cylinder(r1=bore_r+lobe+3, r2=bore_r, h=4);
    // arm slot
    sw = arm_t + 2*fit; sl = arm_w + 2*fit;
    difference() {
      translate([-sw/2, -sl/2, H-slot_depth]) cube([sw, sl, slot_depth+1]);
      // crush ribs on the broad faces
      for (s=[-1,1]) for (y=[-sl/4, sl/4])
        translate([s*(sw/2 - rib_h/2 + 0.01), y, H-slot_depth]) cube([rib_h, 1.6, slot_depth+1], center=false);
    }
    // lead-in funnel at top of slot
    translate([0,0,H-3]) hull() {
      translate([-sw/2, -sl/2, 0]) cube([sw, sl, 0.01]);
      translate([-sw/2-2, -sl/2-2, 3.01]) cube([sw+4, sl+4, 0.01]);
    }
    if (pin_d > 0)
      translate([0,0,H-slot_depth/2]) rotate([0,90,0]) cylinder(d=pin_d, h=core_d1+2, center=true);
  }
}

// ribbon coil spiralling up the cone surface
module coil() {
  n = 120; zmax = H-8;
  for (i=[0:n-1]) {
    z1 = zmax*i/n;  z2 = zmax*(i+1)/n;
    a1 = 360*coil_turns*i/n; a2 = 360*coil_turns*(i+1)/n;
    hull() {
      seg(z1, a1);
      seg(z2, a2);
    }
  }
}
module seg(z, a) {
  r = cone_r(z) - wire_w/2;
  translate([r*cos(a), r*sin(a), z + wire_h/2]) rotate([0,0,a])
    scale([wire_w/2, wire_w/2, wire_h/2]) sphere(r=1, $fn=16);
}

// straight ribs from base rim up the cone surface into the core
module struts() {
  for (k=[0:struts-1]) rotate([0,0,k*360/struts])
    rotate([90,0,0]) linear_extrude(height=3.2, center=true)
      polygon([[core_r(0)-2, 0],[base_r, 0],[base_r-2.5, 3.5],[core_r(H-8)+1.5, H-8],[core_r(H-8)-2, H-8]]);
}

// open spoked base ring so the whole thing prints flat and stays rigid
module base_ring() {
  difference() {
    cylinder(r=base_r, h=3);
    translate([0,0,-1]) cylinder(r=base_r-wire_w, h=5);
  }
}

union() {
  core();
  coil();
  struts();
  base_ring();
  // join strut pockets so core isn't cut through by struts' bore overlap
}
