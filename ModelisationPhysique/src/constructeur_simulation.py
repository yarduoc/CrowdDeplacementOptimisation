from lieu_ferme import LieuFerme
from personne import Personne
from obstacle import ObstacleRectangulaire, ObstacleCirculaire
from obstacle import ObstaclePolygonale
import base
from ecouteur import EcouteurPersonne
from espace import Espace
from pymunk.vec2d import Vec2d
from random import random, randint
from source_personne import Source
from math import sqrt
from simulation import Simulation

#TODO: éviter les constante tout à fait arbitraire

class ConstructeurSalle(object):
       
    def __init__(self, donnees_simulation):
        self.donnees_simulation = donnees_simulation
        
        self.espace = Espace()
        self.type = self.donnees_simulation['type']
        
        self.ajouterLieuFerme(
            self.espace,
            self.donnees_simulation['personnes']['zone_apparition'],
            **self.donnees_simulation['lieu_ferme']['salle'])
            
        if self.type == "salle_de_classe" :
            
            self.ajouterRangs(
                self.espace,
                self.donnees_simulation['personnes']['zone_apparition'],
                **self.donnees_simulation['obstacles']['rangs'])
        
        if self.type == "salle_en_T":
            
            self.ajouterFormeT(
                self.donnees_simulation['obstacles']['particulier']['rectangles'],
                self.donnees_simulation['personnes']['zone_apparition'],
                **self.donnees_simulation['lieu_ferme']['salle_couloir'])
                
        if self.type == "salle_en_Y":
            
            self.ajouterFormeY(
                self.donnees_simulation['obstacles']['particulier']['polygones'],
                self.donnees_simulation['personnes']['zone_apparition'],
                **self.donnees_simulation['lieu_ferme']['salle_couloir'])
            
            
        self.ajouterObstacles(
            self.espace,
            self.donnees_simulation['obstacles']['particulier'])
        
        
    
    def ajouterLieuFerme(self,
            espace,
            zone_apparition=None,
            salle_hauteur=None,
            salle_largeur=None,
            porte_largeur=None,
            porte_position=None):

        zone_apparition.update({'x_min' :  50})
        zone_apparition.update({'x_max' : 50 + salle_largeur })
        zone_apparition.update({'y_min' :  50 })
        zone_apparition.update({'y_max' :  50 + salle_hauteur })
        
        
        espace.ajouterLieuFerme(LieuFerme(
            self.donnees_simulation['lieu_ferme']['porte'],
            salle_largeur,
            salle_hauteur,
            Vec2d(50, 50)))
            
    def ajouterFormeT(self,
            rectangles,
            zone_apparition,
            largeur_horizontale=None,
            largeur_verticale=None):
        
        largeur_couloir = largeur_horizontale
        hauteur_obstacle = largeur_verticale
        largeur_obstacle = (self.espace.lieu_ferme.largeur - largeur_couloir)/2
        
        coin_inferieur1 = [50,50]
        coin_inferieur2 = [50 + largeur_couloir + largeur_obstacle  ,50]

        rectangles.append({
            "largeur" : largeur_obstacle,
            "hauteur" : hauteur_obstacle,
            "position" : coin_inferieur1})
        rectangles.append({
            "largeur" : largeur_obstacle,
            "hauteur" : hauteur_obstacle,
            "position" : coin_inferieur2 })
        
        zone_apparition.update({'x_min' :  50 + largeur_obstacle})
        zone_apparition.update({'x_max' :  coin_inferieur2[0]})
        zone_apparition.update({'y_min' :  50})
        zone_apparition.update({'y_max' :  (50 + hauteur_obstacle)*(2/3)})
        
        
        
    def ajouterFormeY(self,
            polygones,
            zone_apparition,
            largeur_horizontale=None,
            largeur_verticale=None):
    
        #cf ficher annexe
        d = self.espace.lieu_ferme.largeur  
        l = self.espace.lieu_ferme.hauteur
        a = largeur_horizontale
        b = largeur_verticale
        c = (d-a)/2
        y = 0
        x = sqrt(a**2 - y**2)
        h = ((d-2*x)/2) * sqrt(2)
        k = sqrt(h**2 - ((d-2*x)/2)**2)
        
        origine = [50,50]
        bordGauche = [[0,0],[c,0],[c,b],[0,b+c]]
        
        polygones.append({'position' : origine, 'sommets' : bordGauche})
        
        bordDroit = [[c+a,0],[d,0],[c+a,b],[d,b+c]]
        
        polygones.append({'position' : origine, 'sommets' : bordDroit})
       
        triangle = [[x,l],[d-x,l],[d/2,l-k]]
        
        polygones.append({'position' : origine, 'sommets' : triangle})
        
        zone_apparition.update({'x_min' : 50 + c} )
        zone_apparition.update({'x_max' : 50 + c+a} )
        zone_apparition.update({'y_min' : 50} )
        zone_apparition.update({'y_max' : (50 + b)*(2/3)})
        
    
    def ajouterObstacles(self, espace, particulier):
        self.ajouterObstaclesParticulier(espace, particulier)
        
    def ajouterObstaclesParticulier(self, espace, obstacles):
        for obstacle in obstacles['rectangles']:
            espace.ajouterObstacle(ObstacleRectangulaire(**obstacle))
        for obstacle in obstacles['cercles']:
            espace.ajouterObstacle(ObstacleCirculaire(**obstacle))
        for obstacle in obstacles['polygones']:
            espace.ajouterObstacle(ObstaclePolygonale(**obstacle))


    def ajouterRangs(self,
            espace,
            zone_apparition,
            largeur_gauche=None,
            largeur_droit = None,
            hauteur = None,
            distance_intermediaire=None,
            distance_au_mur=None,
            position_debut_gauche=None,
            position_debut_droit=None):

        position_gauche_y = position_debut_gauche
        position_droit_y = position_debut_droit
        
        zone_apparition.update({'x_min' :  50})
        zone_apparition.update({'x_max' :  50 + self.espace.lieu_ferme.largeur})
        zone_apparition.update({
            'y_min' :  50 +
                min(position_debut_gauche, position_debut_droit) + hauteur}) 
        zone_apparition.update({'y_max' :  50 + self.espace.lieu_ferme.hauteur})

        #on ajoute les ranges de gauche
        while position_gauche_y + 50 <= self.espace.lieu_ferme.hauteur :
            position_gauche = 50 + distance_au_mur, position_gauche_y
            
            obstacle_gauche = ObstacleRectangulaire(
                hauteur = hauteur,
                largeur = largeur_gauche,
                position = position_gauche)

            espace.ajouterObstacle(obstacle_gauche)

            position_gauche_y += distance_intermediaire + hauteur
            
            
        #on ajoute les rangs à droite
        while position_droit_y + 50 <= self.espace.lieu_ferme.hauteur :
            position_droit_x = (50 + self.espace.lieu_ferme.largeur
                - largeur_droit - distance_au_mur
            position_droit = position_droit_x, position_droit_y
            
            obstacle_droit = ObstacleRectangulaire(
                hauteur = hauteur,
                largeur = largeur_droit,
                position = position_droit)
            espace.ajouterObstacle(obstacle_droit)

            position_droit_y += distance_intermediaire + hauteur
            
        zone_apparition.update({
            'y_max' :
                50 + min(position_droit_y, position_gauche_y)
                - distance_intermediaire - hauteur})


class ConstructeurSimulation(object):

    def __init__(self, donnees_simulation, action_sortie):
        constructeur_salle = ConstructeurSalle(donnees_simulation)

        creer_ecouteur = lambda personne: EcouteurPersonne(personne, action_sortie)
        
        self.simulation = Simulation(
            constructeur_salle.espace,
            donnees_simulation['mise_a_jour_par_seconde'],
            creer_ecouteur)

        self.ajouterPersonnes(
            nombre=donnees_simulation['personnes']['nombre'], 
            **base.fusioner_dictionnaires(
                donnees_simulation['personnes']['caracteristiques'],
                donnees_simulation['personnes']['zone_apparition']))
            
        self.construireSources(
            donnees_simulation['personnes']['sources'],
            **donnees_simulation['personnes']['caracteristiques'])

    def ajouterPersonnes(self,
            nombre=0,
            rayon_min = 30,
            rayon_max = 30,
            masse_surfacique = 1.8,
            y_min=None,
            y_max=None,
            x_min=None,
            x_max=None):
                
        for _ in range(nombre):
            personne = Personne(
                masse_surfacique,
                randint(rayon_min, rayon_max),
                Vec2d(
                    x_min + random()*(x_max-x_min),
                    y_min + random()*(y_max-y_min)),
                self.simulation.espace)

            self.simulation.espace.ajouterPersonne(personne)
            
    def construireSources(self,
            liste_sources,
            rayon_min=30,
            rayon_max=30,
            masse_surfacique=1.8):

        for source in liste_sources:
            self.simulation.sources.append(Source(
                self.simulation.espace,
                source['position'],
                source['periode'],
                rayon_min,
                rayon_max,
                masse_surfacique))
            
