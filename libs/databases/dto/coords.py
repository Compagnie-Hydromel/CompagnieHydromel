class Coords:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        
    def __str__(self):
        return f'({self.__x}, {self.__y})'
    
    @property
    def x(self):
        return self.__x
    
    @property
    def y(self):
        return self.__y
    
    def dict(self):
        return {
            'x': self.__x,
            'y': self.__y
        }