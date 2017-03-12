import pymunk
from pymunk.vec2d import Vec2d
        
class Representation(pymunk.Shape):
    '''Doit être instancié avec 

    Keyword Arguments: position, corps'''

    def __init__(self, **kwargs):
        position = kwargs['position']
        corps = kwargs['corps']
        del kwargs['position']
        del kwargs['corps']
        self.corps = corps
        self.corps.position = Vec2d(position)

    @property
    def corps(self):
        return self.body

    @corps.setter
    def corps(self, value):
        self.body = value

    @property
    def position(self):
        return self.corps.position

class RepresentationDynamique(Representation):
    '''Keyword Arguments: position, masse, moment'''

    def __init__(self, **kwargs):
        masse = kwargs['masse']
        moment = kwargs['moment']
        del kwargs['masse']
        del kwargs['moment']
        kwargs['corps'] = pymunk.Body(masse, moment)
        super().__init__(**kwargs)

class Rectangle(Representation, pymunk.Poly):
    '''Keyword Arguments: hauteur, largeur, position, corps'''

    def __init__(self, **kwargs):
        self.largeur = kwargs['largeur']
        self.hauteur = kwargs['hauteur']
        del kwargs['largeur']
        del kwargs['hauteur']
        #Forcer d'appeler de cette façon car la représentation doit être
        #créé après poly pour que le corps soit initialisé correctement
        pymunk.Poly.__init__(self, None, list(self.genererSommetsRelatifs()))
        super().__init__(**kwargs)

    def genererSommetsRelatifs(self):
        yield Vec2d(-self.largeur / 2, -self.hauteur / 2)
        yield Vec2d(+self.largeur / 2, -self.hauteur / 2)
        yield Vec2d(+self.largeur / 2, +self.hauteur / 2)
        yield Vec2d(-self.largeur / 2, +self.hauteur / 2)

class Cercle(Representation, pymunk.Circle):
    '''Keyword aruments: position, corps, rayon'''

    def __init__(self, **kwargs):
        rayon = kwargs['rayon']
        del kwargs['rayon']
        #Forcer d'appeler de cette façon car la représentation doit être
        #créé après circle pour que le corps soit initialisé correctement
        pymunk.Circle.__init__(self, None, rayon)
        super().__init__(**kwargs)

    @property
    def rayon(self):
        return self.radius