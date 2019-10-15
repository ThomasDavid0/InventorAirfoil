from enum import Enum
import io
import unittest
import urllib.request
from urllib.error import HTTPError
from geometry import Point


class DatFileFormats(Enum):
    SELIG=0
    LEDNICER=1


class LineReadError(Exception):
    pass

class AirfoilNotFound(Exception):
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
    
    def __mul__(self, value):
        return Point(self.x*value, self.y*value)

class AirfoilDatFile(object):
    def __init__(self, airfoiltoolsname=""):
        self._airfoiltoolsname = airfoiltoolsname
        self._file = ""
        self._name = ""
        self._format = DatFileFormats.SELIG
        self._positions=[]
        self._top_surface = []
        self._btm_surface = []
        if self._airfoiltoolsname:
            self._read_file()

    def _read_file(self):       
        with open(self.file) as f:
            lines = f.readlines()

        self._name = lines.pop(0).strip()
        for line in lines:
            try:
                self._positions.append(AirfoilPoint(line))
            except LineReadError:
                pass
        self._sort_points()
    
    def _sort_points(self):
        if self._format == DatFileFormats.SELIG:
            self._sort_selig()
        elif self._format == DatFileFormats.LEDNICER:
            raise LineReadError("LEDNICER Not Supported")

    def _sort_selig(self):
        # TODO this is a bodge
        i=0
        while self._positions[i].x > self._positions[i+1].x:
            i+=1
        self._top_surface = self._positions[i:0:-1].copy()
        self._top_surface.append(self._positions[0])
        self._btm_surface = self._positions[i:].copy()
    
    @staticmethod
    def download_airfoil_file(airfoiltoolsname):
        print("Downloading file from airfoiltools.com")
        try:
            _file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + airfoiltoolsname)
            print("Finished downloading file from airfoiltools.com")
        except HTTPError as ex:
            print("Error downloading file from airfoiltools.com: " + str(ex))
            raise AirfoilNotFound("")
        return _file

    @property
    def file(self):
        if not self._file:
            self._file = AirfoilDatFile.download_airfoil_file(self._airfoiltoolsname)[0]
        return self._file

    @file.setter
    def file(self, value):
        self.__init__("")
        self._file = value
        self._read_file()

    @property
    def airfoiltoolsname(self):
        return self._airfoiltoolsname

    @airfoiltoolsname.setter
    def airfoiltoolsname(self, value):
        self.__init__(value)
        
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

    @property
    def positions(self):
        return self._positions

    @staticmethod
    def from_file(file):
        _airfoil = AirfoilDatFile()
        _airfoil.file = file
        return _airfoil

class TestAirfoilDatFile(unittest.TestCase):
    def setUp(self):
        self._airfoil = AirfoilDatFile.from_file("./examples/naca2412.dat")

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

    def test_download(self):
        _airfoil = AirfoilDatFile("naca2410-il")
        self.assertEqual(_airfoil.name, "NACA 2410")

    def test_not_exist(self):
        with self.assertRaises(AirfoilNotFound):
            _airfoil = AirfoilDatFile("ssss")

if __name__ == "__main__":
    unittest.main()
