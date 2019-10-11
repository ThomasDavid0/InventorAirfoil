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

    def _read_file(self):       
        with open(self._file) as f:
            lines = f.readlines()

        self._name = lines.pop(0).strip()
        for line in lines:
            try:
                self._positions.append(AirfoilPoint(line))
            except LineReadError:
                pass

    @property
    def name(self):
        return self._name


class TestAirfoilDatFile(unittest.TestCase):
    def setUp(self):
        self._airfoil = AirfoilDatFile("C:/Users/td6834/Documents/BUDDI/20_CAD/20 _Airfoils/naca2412.dat")
    
    def test_name(self):
        self.assertEqual(self._airfoil.name, "NACA 2414")

    def test_points(self):
        self.assertEqual(self._airfoil._positions[0].x, 1.)
        self.assertEqual(self._airfoil._positions[0].y, 0.00147)

if __name__ == "__main__":
    unittest.main()
