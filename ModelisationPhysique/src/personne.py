from representation_categories import RepresentationCategorie
from representation import CercleDynamique
import test_point_suivre
from fonctions_annexes import convertirMetresPixels, convertirSurfacePixelsSurfaceMetres
import math
import pymunk
import math
from pymunk.vec2d import Vec2d

class Personne(CercleDynamique):

    VITESSE_MAXIMALE = convertirMetresPixels(1.3)
    COEFFICIENT_EVITEMENT = 0.4

    #On choisi la distance maximale parcouru par l'agent en une seconde
    #comme rayon de proximité
    RAYON_DE_PROXIMITE = VITESSE_MAXIMALE 

    TEST_DIRECTION = test_point_suivre.TestDichotomieCompactageObstacle

    def __init__(self,
            masse_surfacique,
            rayon,
            position,
            espace):

        super().__init__(
            masse_surfacique=masse_surfacique,
            rayon=rayon,
            position=position)
        
        self.force_deplacement = self.rayon * 10**4
        self.filter = pymunk.ShapeFilter(
            categories=RepresentationCategorie.PERSONNE.value)
        self.espace = espace
        self.test_direction = Personne.TEST_DIRECTION(
            position=position,
            espace=espace,
            rayon=self.rayon,
            position_voulue=self.sortieLaPlusProche())
        self.vitesse_maximale_propre = Personne.VITESSE_MAXIMALE
    
    def sortieLaPlusProche(self):
        liste_centres = self.espace.lieu_ferme.avoirCentrePortes()
        distmin = self.position.get_distance(liste_centres[0])
        centre_min = liste_centres[0]
        
        for centre in (liste_centres):
            dist = self.position.get_distance(centre)
            if dist < distmin :
                distmin, centre_min = dist, centre
                
        return centre_min
    
    def pointEstAInterieur(self, point):
        return point.get_distance(self.body.position) < self.rayon

    def personneEstTropProche(self, personne):    
        return (personne.body.position.get_distance(self.body.position)
            < (2 + Personne.COEFFICIENT_EVITEMENT) * self.rayon)

    def estTropProcheDePersonne(self):
        return any(map(lambda personne: self.personneEstTropProche(personne),
            self.espace.ensemble_personnes))

    def estSortie(self):
        return self.espace.lieu_ferme.pointEstAExterieur(self.position)
    
    def avoirCarreProximite(self):
        
        gauche = self.position.x - Personne.RAYON_DE_PROXIMITE
        droite = self.position.x + Personne.RAYON_DE_PROXIMITE
        haut = self.position.y + Personne.RAYON_DE_PROXIMITE
        bas = self.position.y - Personne.RAYON_DE_PROXIMITE
        
        return pymunk.BB(gauche,bas,droite,haut)
        
        
    def avoirNombreDePersonnesAProximite(self):
        personnes_proches = self.espace.bb_query(
            self.avoirCarreProximite(),
            pymunk.ShapeFilter(mask=RepresentationCategorie.PERSONNE.value))
        
        return len(personnes_proches)

    def avoirSurfaceZoneDeProximite(self):
        return self.avoirCarreProximite().area()

    def mettreAJourDensite(self):
        #Densite en personnes par metres carrès
        surface_proximite = convertirSurfacePixelsSurfaceMetres(
            self.avoirSurfaceZoneDeProximite())
        self.densite = (self.avoirNombreDePersonnesAProximite()
            / surface_proximite)
            
    def miseAJourVitesseMax(self):
        if self.densite == 0 :
            self.vitesse_maximale_propre =  Personne.VITESSE_MAXIMALE
        else :
            self.vitesse_maximale_propre = (
                Personne.VITESSE_MAXIMALE * min(1, self.densite**(-0.8)))
        
    def traiterVitesse(self):
        if self.corps.velocity.length > self.vitesse_maximale_propre :
            self.corps.velocity.length = self.vitesse_maximale_propre

    def mettreAJourForce(self):
        if not self.estSortie():
            self.test_direction.update(self.position)
            force = self.test_direction.point_a_suivre - self.body.position
            if force != Vec2d(0, 0):
                force.length = self.force_deplacement
            self.body.apply_force_at_local_point(force, Vec2d(0, 0))

    def update(self):
        self.mettreAJourDensite()
        self.miseAJourVitesseMax()
        self.traiterVitesse()
        self.mettreAJourForce()

