// Printed socket: slips onto a rod / store-bought topper stabilizer, holds a 10 x 10 mm flake arm.
// Print upright (slot opening up), no supports. All dimensions in mm.
arm_w=10; arm_t=20; fit=0.15; slot_depth=55; rib_h=0.30;
pin_d=4.2;         // hole through socket + the flake's ribbon-loop hole (0 = off)
pin_from_tip=25;   // distance from the arm tip (slot floor) to the centre of the ribbon-loop hole
rod_d=12.7;        // rod / stabilizer post diameter (1/2 in). Measure yours!
rod_fit=0.25;      // extra clearance on the rod bore
rod_depth=45;      // how far the rod enters from below
body_d=44; skirt_d=58; skirt_h=14; H=105;
cross_d=3.5;       // zip-tie hole through the rod bore, set 90 deg to the pin (0 = off)
$fn=72;

module profile() { // revolve outline: flared skirt blending into a slim neck
  rotate_extrude() polygon(concat(
    [[0,0],[skirt_d/2,0],[skirt_d/2,2]],
    [for (t=[0:0.1:1]) let(z=2+(skirt_h+12)*t, r=body_d/2+(skirt_d-body_d)/2*pow(1-t,2.2)) [r,z]],
    [[body_d/2,H-4],[body_d/2-3,H],[0,H]]));
}
sw=arm_t+2*fit; sl=arm_w+2*fit;
difference(){
  profile();
  translate([0,0,-0.01]) cylinder(d=rod_d+rod_fit*2, h=rod_depth);
  translate([0,0,-0.01]) cylinder(d1=rod_d+8, d2=rod_d, h=4);               // lead-in for rod
  difference(){
    translate([-sw/2,-sl/2,H-slot_depth]) cube([sw,sl,slot_depth+1]);
    for (s=[-1,1]) for (y=[-sl/4,sl/4]) translate([s*(sw/2-rib_h/2+0.01),y,H-slot_depth]) cube([rib_h,1.6,slot_depth+1]);
  }
  translate([0,0,H-3]) hull(){ translate([-sw/2,-sl/2,0]) cube([sw,sl,0.01]); translate([-sw/2-2,-sl/2-2,3.01]) cube([sw+4,sl+4,0.01]); }
  if (pin_d>0) translate([0,0,H-slot_depth+pin_from_tip]) rotate([0,90,0]) cylinder(d=pin_d,h=body_d+skirt_d,center=true,$fn=32);
  if (cross_d>0) translate([0,0,rod_depth/2]) rotate([90,0,0]) cylinder(d=cross_d,h=body_d+skirt_d,center=true,$fn=24);
}
