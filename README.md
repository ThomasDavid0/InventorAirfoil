WIP python tool to read an airfoil .dat file, make a few changes to it, then draw it in Autodesk Inventor

To install (python 3.6):
pip install -r requirements.txt

To Run:
from inventor_wing_section import InventorAirfoil
InventorAirfoil.draw_section_in_new_part(airfoiltoolsname, chord, te_thickness)

This will download the requested airfoil dat file from "http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + name, scale it to the desired chord (mm), add the requested te_thickness (mm), find inventor, create a new ipt, create a sketch and draw two splines.