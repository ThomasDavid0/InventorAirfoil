from enum import Enum
import io
import unittest

from geometry import Point


class DatFileFormats(Enum):
    SELIG=0
    LEDNICER=1


class LineReadError(Exception):
    pass


class AirfoilPoint(Point):
    def __init__(self, dat_line):
        self._read_dat_line(dat_line)

    def _read_dat_line(self, dat_line):
        simple = dat_line.strip().split()
        try:
            self._x = float(simple[0])
            self._y = float(simple[1])
        except:
            raise LineReadError


class AirfoilDatFile(object):
    def __init__(self, file):
        self._file = file
        self._name = ""
        self._format = DatFileFormats.SELIG
        self._positions=[]
        self._read_file()
        self._top_surface = []
        self._btm_surface = []

    def _read_file(self):       
        with open(self._file) as f:
            lines = f.readlines()

        self._name = lines.pop(0).strip()
        for line in lines:
            try:
                self._positions.append(AirfoilPoint(line))
            except LineReadError:
                pass
    
    def _sort_points(self):
        if self._format == DatFileFormats.SELIG:
            self._sort_selig()
        elif self._format == DatFileFormats.LEDNICER:
            print ("LEDNICER Not Supported")

    def _sort_selig(self):
        # TODO this is a bodge
        i=0
        while self._positions[i].x > self._positions[i+1].x:
            i+=1
        self._top_surface = self._positions[i:0:-1].copy()
        self._top_surface.append(self._positions[0])
        self._btm_surface = self._positions[i:].copy()

    @property
    def name(self):
        return self._name

    @property
    def top_surface(self):
        """top surface points, sorted from LE to TE, including central LE point"""
        return self._top_surface

    @property
    def btm_surface(self):
        """btm surface points, sorted from LE to TE, including central LE point"""
        return self._btm_surface


class TestAirfoilDatFile(unittest.TestCase):
    def setUp(self):
        self._airfoil = AirfoilDatFile("./examples/naca2412.dat")
    
    def test_name(self):
        self.assertEqual(self._airfoil.name, "NACA 2414")

    def test_points(self):
        self.assertEqual(self._airfoil._positions[0].x, 1.)
        self.assertEqual(self._airfoil._positions[0].y, 0.00147)

    def test_sort_selig(self):
        self._airfoil._sort_selig()

        self.assertEqual(self._airfoil.top_surface[0].x, 0)
        self.assertEqual(self._airfoil.top_surface[0].y, 0)
        self.assertEqual(self._airfoil.top_surface[-1].x, 1)
        self.assertEqual(self._airfoil.top_surface[-1].y, 0.00147)
        self.assertEqual(self._airfoil.btm_surface[0].x, 0)
        self.assertEqual(self._airfoil.btm_surface[0].y, 0)
        self.assertEqual(self._airfoil.btm_surface[-1].x, 1)
        self.assertEqual(self._airfoil.btm_surface[-1].y, -0.00147)

if __name__ == "__main__":
    unittest.main()
