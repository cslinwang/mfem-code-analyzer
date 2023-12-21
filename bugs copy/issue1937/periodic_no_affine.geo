// Gmsh project created on Mon Sep 14 09:33:57 2015
a = 1.;
R = 0.2;
b = a;

d = .6;

Point(1) = {0, 0, 0, d};
Point(2) = {a, 0, 0, d};
Point(3) = {a, b, 0, d};
Point(4) = {0, b, 0, d};
Point(5) = {R,0,0,d};
Point(6) = {a-R,0,0,d};
Point(7) = {a,R,0,d};
Point(8) = {a,b-R,0,d};
Point(9) = {a-R,b,0,d};
Point(10) = {R,b,0,d};
Point(11) = {0,b-R,0,d};
Point(12) = {0,R,0,d};

Line(1) = {1, 5};
Line(2) = {5, 6};
Line(3) = {6, 2};
Line(4) = {2, 7};
Line(5) = {7, 8};
Line(6) = {8, 3};
Line(7) = {3, 9};
Line(8) = {9, 10};
Line(9) = {10, 4};
Line(10) = {4, 11};
Line(11) = {11, 12};
Line(12) = {12, 1};


Periodic Line{1} = {-9};
Periodic Line{2} = {-8};
Periodic Line{3} = {-7};
Periodic Line{4} = {-12};
Periodic Line{5} = {-11};
Periodic Line{6} = {-10};

Line Loop(17) = {1,2,3,4,5,6,7,8,9,10,11,12};
Plane Surface(18) = {17};

For li In {1:12}
    Physical Line(li)  = {li}; 
EndFor

Physical Surface(1) = {18};


Mesh 2;
Mesh.MshFileVersion = 2.2;

