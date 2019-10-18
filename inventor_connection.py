from win32com.client import Dispatch, GetActiveObject, gencache, constants
import unittest
from geometry import Point

class Inventor():
    def __init__(self, start=True):
        self._application = None
        self._mod = None
        if start:
            self.get_inventor()

    @property
    def application(self):
        return self._application
    
    @property
    def mod(self):
        return self._mod

    def get_inventor(self):
        try:
            oApp = GetActiveObject('Inventor.Application')
        except Exception as e:
            print(e)
            oApp = Dispatch('Inventor.Application')
            oApp.Visible = True
        self._mod = gencache.EnsureModule('{D98A091D-3A0F-4C3E-B36E-61F62068D488}', 0, 1, 0)
        self._application = self._mod.Application(oApp)
        
    @property
    def template_path(self):
        return self._application.DesignProjectManager.ActiveDesignProject.TemplatesPath

    def new_part_document(self, name, template = ""):
        if not template:
            template = self.template_path + "/Metric/Standard (mm).ipt"
        new_part = self.application.Documents.Add(constants.kPartDocumentObject, template, True)
        part_doc = self.mod.PartDocument(new_part)
        part_doc.FullFileName = name
        part_doc.DisplayName = name
        return part_doc

    def open_part_document(self, file):
        return self.mod.PartDocument(self.application.Documents.Open(file))

    @property
    def active_part_document(self):
        return self.mod.PartDocument(self.application.ActiveDocument)

    @property
    def open_documents(self):
        return [doc for doc in self.application.Documents]

    def close_document(self, doc):
        doc.Close(True)

    def new_object_collection_from_list(self, things):
        collection = self.application.TransientObjects.CreateObjectCollection()
        for thing in things:
            collection.Add(thing)
        return collection

inventor = Inventor()

class InventorPart(object):
    def __init__(self, part_doc):
        
        self._part_doc = part_doc

    def create_sketch(self, name, plane):
        new_sketch = self._part_doc.ComponentDefinition.Sketches.Add(plane, False)
        new_sketch.Name = name
        return new_sketch

    @property
    def origin_planes(self):
        return [plane for plane in self._part_doc.ComponentDefinition.WorkPlanes]

    @property
    def part_doc(self):
        return self._part_doc

    @property
    def parameters(self):
        # TODO convert this to a more useful dict at some point
        return self._part_doc.ComponentDefinition.Parameters.UserParameters

    @property
    def user_cids(self):
        return self.part_doc.ComponentDefinition.UserCoordinateSystems

    @property
    def work_planes(self):
        return self.part_doc.ComponentDefinition.WorkPlanes

    def create_loft(self, profiles):       
        new_loft = self.part_doc.ComponentDefinition.Features.LoftFeatures.CreateLoftDefinition(
            inventor.new_object_collection_from_list(profiles),
            constants.kJoinOperation
        )
        self.part_doc.ComponentDefinition.Features.LoftFeatures.Add(new_loft)
        return new_loft

    def replace_loft_profiles(self, loft, new_profiles):
        loft.Definition.Sections = inventor.new_object_collection_from_list(new_profiles)

    @property
    def sketches(self):
        return self.part_doc.ComponentDefinition.Sketches

class InventorSketch(object):
    def __init__(self, sketch):
        self._sketch = sketch
        self._transient_geometry = inventor.application.TransientGeometry
        self._transient_objects = inventor.application.TransientObjects

    @property
    def sketch(self):
        return self._sketch

    def create_point(self, location):
        if isinstance(location, Point):
            return self._transient_geometry.CreatePoint2d(location.x * 0.1, location.y * 0.1)
            # TODO for some reason positions can only be written in cm, so hardcoded conversion from mm here
        elif isinstance(location, list):
            return [self.create_point(loc) for loc in location]
        else:
            raise TypeError("Cannot create a Point2D with a " + type(location))

    def create_line(self, start, end):
        p1 = self.create_point(start)
        p2 = self.create_point(end)
        return self._sketch.SketchLines.AddByTwoPoints(p1, p2)

    def create_spline(self, locations):
        points = self.create_point(locations)
        fit_points = self._transient_objects.CreateObjectCollection()
        for point in points:
            fit_points.Add(point)
        return self._sketch.SketchSplines.Add(fit_points)


class TestInventor(unittest.TestCase):
    def setUp(self):
        self._inventor = Inventor()
    
    def test_created(self):
        self.assertTrue(self._inventor.application)

    def test_create_part(self):
        part = self._inventor.new_part_document("test")
        self.assertTrue(part)
        self.assertEqual(part.DisplayName, "test")

        self.assertEqual(part, self._inventor.open_documents[0])
        self._inventor.close_document(part)


class TestInventorPart(unittest.TestCase):
    def setUp(self):
        self._inventor = Inventor()
        self._part = InventorPart(self._inventor.new_part_document('test_part'))

    def test_create_sketch(self):
        sketch = self._part.create_sketch('test_sketch', self._part.origin_planes[0])
        self.assertTrue(sketch)

    def tearDown(self):
        self._inventor.close_document(self._part.part_doc)
        self._part = None

class TestInventorSketch(unittest.TestCase):
    def setUp(self):
        self._inventor = Inventor()
        self._part = InventorPart(self._inventor.new_part_document('test_part_sketch'))
        self._sketch = InventorSketch(self._part.create_sketch('test_sketch', self._part.origin_planes[0]))

    def test_create_line(self):
        line = self._sketch.create_line(Point(10, 10), Point(20, 20))
        self.assertTrue(line)

    def test_create_spline(self):
        spline = self._sketch.create_spline([Point(10, 10), Point(20, 15), Point(30,10)])
        self.assertTrue(spline)

    def tearDown(self):
        self._inventor.close_document(self._part.part_doc)
        self._part = None


if __name__ == "__main__":
    unittest.main()



    