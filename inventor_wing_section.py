from dat_file import AirfoilDatFile
from geometry import Point
from inventor_connection import Inventor, InventorPart, InventorSketch

import unittest


class InventorAirfoil(object):
    @staticmethod
    def draw_section_in_new_part(airfoiltoolsname, chord, te_thickness):
        """Downloads a dat file from airfoiltools.com and draws a spline in a new ipt.

        airfoiltoolsname: str: section to be downloaded from http://airfoiltools.com/airfoil/seligdatfile?airfoil=
        chord, float, mm
        te_thickness: float, mm, thickness will be added to top and bottom linearly from max thickness back
        """
        _airfoil = AirfoilDatFile(airfoiltoolsname)
        _inventor = Inventor()
        _part = InventorPart(_inventor.new_part_document(_airfoil.name))
        _sketch = InventorSketch(_part.create_sketch('section', _part.origin_planes[0]), _inventor.application)
        
        scaled_positions = [pos * (chord / 10) for pos in _airfoil.positions]
        
        spline = _sketch.create_spline(scaled_positions)
        # btm_spline = _sketch.create_spline(_airfoil.btm_surface)


class TestInventorAirfoil(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_draw_airfoil(self):
        InventorAirfoil.draw_section_in_new_part("kenmar-il", 100, 3)
    
 
if __name__ == "__main__":
    unittest.main()
