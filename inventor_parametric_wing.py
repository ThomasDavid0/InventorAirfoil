from inventor_wing_section import InventorAirfoil
from inventor_connection import inventor, InventorPart
import unittest
import os


class InventorWingSegment(object):
    """This class links the ParametricWingSegment.ipt template, or parts created from it."""
    TEMPLATE = os.getcwd() + "/templates/ParametricWingSegment.ipt"
    def __init__(self):
        self._part = None
        self._root_section = None
        self._tip_section = None
        self._loft = None

    @staticmethod 
    def create_from_template(target):
        wing = InventorWingSegment()
        wing.part = InventorPart(inventor.new_part_document(
            os.path.basename(target), 
            InventorWingSegment.TEMPLATE
            ))
        wing.part.part_doc.SaveAs(target, True)
        return wing

    @staticmethod
    def update_part(part):
        wing = InventorWingSegment()
        wing.part = part
        
    def read_part(self):
        self._root_section = self._read_props("root")
        self._tip_section = self._read_props("tip")

    def populate_template(self):
        self._create_section(self._root_section, "root")
        self._create_section(self._tip_section, "tip")
        self._create_loft()

    def _create_section(self, section, position):
        section.print_on_plane(
            self._part, 
            self._part.user_cids.Item("UCS_" + position).XYPlane,
            position + "_section"
            )

    def _read_props(self, position):
        return InventorAirfoil(
            self._part.parameters.Item(position + "_section").Value,
            self._part.parameters.Item(position + "_chord").Value * 10,
            self._part.parameters.Item(position + "_te_thickness").Value * 10
            )

    def _create_loft(self):
        self._part.create_loft([self._root_section.profile, self._tip_section.profile])

    @property
    def part(self):
        return self._part

    @part.setter
    def part(self, value):
        self._part = value
        self.read_part()


class TestInventorWingSegment(unittest.TestCase):
    def test_populate_template(self):
        target = os.getcwd() + "/tests/created_segment.ipt"
        _segment = InventorWingSegment.create_from_template(target)
        _segment.populate_template()
        _segment.part.part_doc.SaveAs(target, True)()
        _segment.part.part_doc.Close(False)

    def test_update_part(self):
        _segment = InventorWingSegment.update_part(InventorPart(inventor.application.Documents.Open(os.getcwd() + "/tests/created_segment.ipt")))
        _segment.part.part_doc.Close(True)

if __name__ == "__main__":
    unittest.main()