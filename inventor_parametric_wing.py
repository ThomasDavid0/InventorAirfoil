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
        wing.part.part_doc.SaveAs(target, False)
        return wing

    @staticmethod
    def update_part(part):
        wing = InventorWingSegment()
        wing.part = part
        wing.redraw_sections()
        return wing
        
    def read_part(self):
        self._root_section = InventorAirfoil.read_part(self._part,"root")
        self._tip_section = InventorAirfoil.read_part(self._part,"tip")
        try:
            self._loft = self._part.part_doc.ComponentDefinition.Features.LoftFeatures.Item(1)
        except: # TODO this is lazy
            pass 

    def populate_template(self):
        self._create_section(self._root_section, "root")
        self._create_section(self._tip_section, "tip")
        self._create_loft()

    def redraw_sections(self):
        self._root_section.redraw_section()
        self._tip_section.redraw_section()
        self._part.replace_loft_profiles(self._loft, [self._root_section.profile, self._tip_section.profile])

    def _create_section(self, section, position):
        section.print_on_plane(
            self._part, 
            self._part.user_cids.Item("UCS_" + position).XYPlane,
            position + "_section"
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
        _segment.part.part_doc.Save()
        _segment.part.part_doc.Close(False)

    def test_update_part(self):
        wing_part = InventorPart(
            inventor.open_part_document(
                os.getcwd() + "/tests/created_segment.ipt"
            ))
        wing_part.parameters.Item("root_section").Value = "e1098-il"
        wing_part.parameters.Item("root_chord").Value = 15
        wing_part.parameters.Item("root_te_thickness").Value = .2
        
        wing_part.parameters.Item("tip_section").Value = "e1212-il"
        wing_part.parameters.Item("tip_chord").Value = 10
        wing_part.parameters.Item("tip_te_thickness").Value = .1

        _segment = InventorWingSegment.update_part(wing_part)
        _segment.part.part_doc.Close(True)

if __name__ == "__main__":
    unittest.main()