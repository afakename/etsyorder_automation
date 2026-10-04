// Optional adapter for flakes that have no 10 x 10 mm arm.
// Print this, glue/epoxy the flat plate onto the back of the flake's lowest point.
arm_w=10; arm_t=10; tab_len=50; plate=34; plate_t=2.4;
union(){
  translate([-arm_t/2,-arm_w/2,0]) cube([arm_t,arm_w,tab_len]);
  translate([-plate/2,-plate/2,tab_len-plate_t]) cube([plate,plate,plate_t]);
  // gusset so the plate doesn't snap off the tab
  hull(){ translate([-arm_t/2,-arm_w/2,tab_len-12]) cube([arm_t,arm_w,.01]);
          translate([-plate/2,-plate/2,tab_len-plate_t]) cube([plate,plate,.01]); }
}
