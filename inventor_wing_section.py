from dat_file import AirfoilDatFile
from geometry import Point
from inventor_connection import Inventor, InventorPart, InventorSketch
from tkinter  import filedialog
import urllib.request
from urllib.error import HTTPError
import unittest


class AirfoilNotFound(Exception):
    pass


class Airfoil(object):
    def __init__(self, section_name, chord, te_thickness):
        self._section_name = section_name
        self._chord = chord
        self._te_thickness = te_thickness
        self._airfoil_dat = None
    
    @property
    def section_name(self):
        return self._section_name
        
    def download_airfoil_file(self):
        if not self._airfoil_dat:
            print("Downloading file from airfoiltools.com")
            try:
                airfoil_file = urllib.request.urlretrieve("http://airfoiltools.com/airfoil/seligdatfile?airfoil=" + self.section_name)
                print("Downloaded file from airfoiltools.com")
                return airfoil_file
            except HTTPError as ex:
                print("Error downloading file from airfoiltools.com: " + str(ex))
                raise AirfoilNotFound
    
    def top_surface(self):
        self.download_airfoil_file()
        
    def btm_surface(self):
        self.download_airfoil_file()


class TestAirfoil(unittest.TestCase):
    def setUp(self):
        pass
    
    def test_download(self):
        _airfoil = Airfoil("naca2410-il", 100, 5)
        file = _airfoil.download_airfoil_file()
        airfoil = AirfoilDatFile(file[0])
        self.assertEqual(airfoil.name, "NACA 2410")

    def test_not_exist(self):
        _airfoil = Airfoil("ssss", 100, 5)
        with self.assertRaises(AirfoilNotFound):
            file = _airfoil.download_airfoil_file()
    
 
if __name__ == "__main__":
    unittest.main()
