import random
import math
from enum import Enum
from .position import Position

class EtatAvion(Enum):
    EN_VOL = "En vol"
    ATTERRI = "Atterri"
    URGENCE = "Urgence"

class TypeUrgence(Enum):
    AUCUNE = "Aucune"
    CARBURANT = "Carburant faible"
    PANNE = "Panne technique"
    METEO = "Conditions météo"

class Avion:
    def __init__(self, identifiant: str, position: Position, cap: float, vitesse: float):
        self.identifiant = identifiant
        self.position = position
        self.cap = cap
        self.vitesse = vitesse
        self.altitude_cible = position.altitude
        self.vitesse_cible = vitesse
        self.cap_cible = cap
        self.carburant = 100
        self.etat = EtatAvion.EN_VOL
        self.urgence = TypeUrgence.AUCUNE
        self.en_attente = False
        self.temps_attente = 0
        self.temps_urgence = 0
        self.points_urgence_perdus = 0
        self.points_attente_perdus = 0
        self.vitesse_avant_attente = vitesse
        self.altitude_avant_attente = position.altitude

    def mettre_a_jour(self, delta_temps: float):
        if self.etat == EtatAvion.ATTERRI:
            return
        self.carburant -= 0.1 * delta_temps
        if self.carburant <= 0:
            self.carburant = 0
            if self.urgence == TypeUrgence.AUCUNE:
                self.urgence = TypeUrgence.CARBURANT
                self.temps_urgence = 0
                self.points_urgence_perdus = 0
        if random.random() < 0.001 and self.urgence == TypeUrgence.AUCUNE:
            self.urgence = random.choice([TypeUrgence.PANNE, TypeUrgence.METEO])
            self.temps_urgence = 0
            self.points_urgence_perdus = 0
        transition_vitesse = 0.3
        transition_cap = 0.2
        transition_altitude = 0.06
        if not self.en_attente:
            self.vitesse += (self.vitesse_cible - self.vitesse) * transition_vitesse
            delta_cap = self.cap_cible - self.cap
            while delta_cap > 180:
                delta_cap -= 360
            while delta_cap < -180:
                delta_cap += 360
            step = delta_cap * transition_cap
            if abs(step) > abs(delta_cap):
                step = delta_cap
            self.cap += step
            self.cap = self.cap % 360
            self.position.altitude += (self.altitude_cible - self.position.altitude) * transition_altitude
            vitesse_ms = self.vitesse * 1000 / 3600
            cap_rad = math.radians(self.cap)
            dx = vitesse_ms * math.sin(cap_rad) * delta_temps
            dy = -vitesse_ms * math.cos(cap_rad) * delta_temps
            self.position.x += dx
            self.position.y += dy
        else:
            self.temps_attente += delta_temps

    def changer_cap(self, nouveau_cap: float):
        self.cap_cible = nouveau_cap % 360

    def changer_altitude(self, nouvelle_altitude: float):
        self.altitude_cible = float(nouvelle_altitude)

    def changer_vitesse(self, nouvelle_vitesse: float):
        self.vitesse_cible = float(nouvelle_vitesse)

    def activer_attente(self):
        if not self.en_attente:
            self.vitesse_avant_attente = self.vitesse_cible
            self.altitude_avant_attente = self.altitude_cible
            self.en_attente = True
            self.temps_attente = 0
            self.points_attente_perdus = 0
            self.vitesse_cible = 0

    def desactiver_attente(self):
        if self.en_attente:
            self.en_attente = False
            self.temps_attente = 0
            self.points_attente_perdus = 0
            self.vitesse_cible = self.vitesse_avant_attente
            self.altitude_cible = self.altitude_avant_attente

    def atterrir(self):
        self.etat = EtatAvion.ATTERRI
        self.vitesse_cible = 0

    def resoudre_urgence(self):
        self.urgence = TypeUrgence.AUCUNE
        self.temps_urgence = 0
        self.points_urgence_perdus = 0

    def get_couleur(self) -> str:
        if self.urgence != TypeUrgence.AUCUNE:
            return "#FF4444"
        elif self.en_attente:
            return "#FFAA00"
        elif self.etat == EtatAvion.ATTERRI:
            return "#888888"
        else:
            return "#87CEEB"

    def get_info(self) -> str:
        urgence_str = f" • {self.urgence.value}" if self.urgence != TypeUrgence.AUCUNE else ""
        attente_str = "ARRÊTÉ" if self.en_attente else ""
        return f"{self.identifiant}{attente_str}\nAlt: {int(self.position.altitude)}m • V: {int(self.vitesse)}km/h • Cap: {int(self.cap)}° • Fuel: {int(self.carburant)}%{urgence_str}"
