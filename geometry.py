

class Point(object):
    def __init__(self, x, y, z=0):
        self._x = x
        self._y = y
        self._z = z
    
    @property
    def x(self):
        return self._x
    
    @property 
    def y(self):
        return self._y
    
    @property
    def z(self):
        return self._z
    
    @property
    def array(self):
        return [self._x, self._y, self._z]
        
