from dat_file import AirfoilDatFile, Surfaces
from geometry import Point
from inventor_connection import inventor, InventorPart, InventorSketch

import unittest


class InventorAirfoil(object):
    def __init__(self, airfoiltoolsname, chord, te_thickness):
        self._raw_data = AirfoilDatFile(airfoiltoolsname)
        self._chord = chord
        self._te_thickness = te_thickness
        self._modified_positions = []
        
        self._part = None
        self._plane = None
        self._sketch = None
        self._spline = None
        self._te_line = None
        self._profile = None

    @property
    def raw_data(self):
        return self._raw_data

    @property
    def modified_positions(self):
        if not self._modified_positions:
            self._modified_positions = [self._transform_point(pos) for pos in self._raw_data.positions]
        return self._modified_positions

    def _transform_point(self, in_point):
        return self._apply_te_thickness(self._apply_chord(in_point))

    def _apply_chord(self, in_point):
        return in_point * (self._chord)
    
    def _apply_te_thickness(self, in_point):
        add_thick = 0.5 * self._te_thickness * in_point.x / self._chord
        if in_point.surface == Surfaces.TOP:
            out_point = in_point + Point(0, add_thick)
        elif in_point.surface == Surfaces.BTM:
            out_point = in_point + Point(0, -add_thick)
        out_point.surface = in_point.surface
        return out_point

    def print_on_new_part(self, origin_plane_id = 0):
        self._part = InventorPart(inventor.new_part_document(self._raw_data.name))
        self.print_on_plane(self._part, self._part.origin_planes[origin_plane_id])

    def print_on_plane(self, part, plane, name = "section"):
        self._plane = plane
        self._sketch = InventorSketch(part.create_sketch(name, plane))
        self.print_on_sketch(self._sketch)

    def print_on_sketch(self, sketch):
        self._sketch = sketch
        self._spline = sketch.create_spline(self.modified_positions)
        self._te_line = sketch.sketch.SketchLines.AddByTwoPoints(
            self._spline.FitPoint(1), 
            self._spline.FitPoint(self._spline.FitPointCount)
            ) 
        #sketch.create_line(self.modified_positions[0], self.modified_positions[-1])
        #sketch.sketch.GeometricConstraints.AddCoincident(
        #    self._te_line.StartSketchPoint,
        #    self._spline
        #    )
        #sketch.sketch.GeometricConstraints.AddCoincident(
        #    self._spline, 
        #    self._te_line.EndSketchPoint
        #    )

    def redraw_section(self):
        for i in range(1, len(self.modified_positions)+1):
            if i < self._spline.FitPointCount: # The matched points
                self._spline.FitPoint(i).MoveTo(self._sketch.create_point(self.modified_positions[i-1]))
            elif i == self._spline.FitPointCount: # the new points
                if i < len(self.modified_positions):
                    self._spline.InsertFitPoint(
                        self._sketch.create_point(self.modified_positions[i-1]),
                        self._spline.FitPointCount
                        )

        while self._spline.FitPointCount > i : # The old points
            self._spline.FitPoint(i).Delete()
        # the last point
        self._spline.FitPoint(self._spline.FitPointCount).MoveTo(self._sketch.create_point(self._modified_positions[-1]))

    @staticmethod
    def draw_section_in_new_part(airfoiltoolsname, chord, te_thickness):
        """Downloads a dat file from airfoiltools.com and draws a spline on the yz plane of a new ipt.

        airfoiltoolsname: str: section to be downloaded from http://airfoiltools.com/airfoil/seligdatfile?airfoil=
        chord, float, mm
        te_thickness: float, mm, thickness / 2 will be added to top and bottom linearly from the LE
        """
        _airfoil = InventorAirfoil(airfoiltoolsname, chord, te_thickness)              
        _airfoil.print_on_new_part()

    @property
    def sketch(self):
        return self._sketch
    
    @sketch.setter
    def sketch(self, value):
        self._sketch = value

    @property
    def part(self):
        return self._part
    
    @part.setter
    def part(self, value):
        self._part = value

    @staticmethod
    def read_part(part, position):
        new_section = InventorAirfoil(
            part.parameters.Item(position + "_section").Value,
            part.parameters.Item(position + "_chord").Value * 10,
            part.parameters.Item(position + "_te_thickness").Value * 10
            )
        new_section.part = part
        try:
            new_section.sketch = InventorSketch(part.sketches.Item(position + '_section'))
            new_section._spline = new_section.sketch.sketch.SketchSplines.Item(1)
            new_section._te_line = new_section.sketch.sketch.SketchLines.Item(1)
        except Exception:
            pass
        return new_section

    @property
    def profile(self):
        if not self._profile:
            self._profile = self._sketch.sketch.Profiles.AddForSolid(
                False, 
                inventor.new_object_collection_from_list([self._spline, self._te_line])
                )
        return self._profile

class TestInventorAirfoil(unittest.TestCase):
    def test_draw_airfoil(self):
        InventorAirfoil.draw_section_in_new_part("hobiesm-il", 200, 3)
    
 
if __name__ == "__main__":
    unittest.main()
