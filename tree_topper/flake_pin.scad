// Retaining pin for the ribbon-loop hole. Print lying down. Use a dowel/bolt instead if you prefer.
pin_d=4.2-0.35; len=50; head_d=9; head_h=3;
cylinder(d=pin_d,h=len,$fn=32);
translate([0,0,-head_h]) cylinder(d=head_d,h=head_h,$fn=40);
// small barb near the tip: pushes through, resists backing out
translate([0,0,len-6]) cylinder(d1=pin_d,d2=pin_d+0.8,h=3,$fn=32);
