from inventor_wing_section import InventorAirfoil
from inventor_connection import inventor, InventorPart
import unittest
import os


class InventorWingSegment(object):
    """This class links the ParametricWingSegment.ipt template, or parts created from it."""
    TEMPLATE = "C:/Users/td6834/Documents/BUDDI/20_CAD/20_Airfoils/ParametricWingSegment.ipt"
    def __init__(self):
        self._part = None
        self._root_section = None
        self._tip_section = None
        self._loft = None

    @staticmethod 
    def create_from_template(target):
        wing = InventorWingSegment()
        wing.part = InventorPart(inventor.new_part_document(
            os.path.basename(target).split(".")[0], 
            InventorWingSegment.TEMPLATE
            ))
        wing.part.part_doc.SaveAs(target, True)
        return wing

    def populate_template(self):
        self._root_section = self._create_section("root")
        self._tip_section = self._create_section("tip")
        
    def _create_section(self, position):
        section = InventorAirfoil(
            self._part.parameters.Item(position + "_section").Value,
            self._part.parameters.Item(position + "_chord").Value * 10,
            self._part.parameters.Item(position + "_te_thickness").Value * 10
            )
        section.print_on_plane(
            self._part, 
            self._part.user_cids.Item("UCS_" + position).XYPlane,
            position + "_section"
            )
        return section

    def _create_loft(self):
        pass


    @property
    def part(self):
        return self._part

    @part.setter
    def part(self, value):
        self._part = value


class TestInventorWingSegment(unittest.TestCase):
    def setUp(self):
        self._segment = InventorWingSegment.create_from_template("C:/Users/td6834/Documents/BUDDI/20_CAD/10_Concept_Design/test_wing.ipt")

    def test_populate_template(self):
        self._segment.populate_template()


if __name__ == "__main__":
    unittest.main()