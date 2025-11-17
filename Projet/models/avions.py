import math
import random
from enum import Enum
from dataclasses import dataclass
from typing import Tuple


class EtatAvion(Enum):
    EN_VOL = "En vol"
    EN_APPROCHE = "En approche"
    ATTERRI = "Atterri"
    URGENCE = "Urgence"


class TypeUrgence(Enum):
    AUCUNE = "Aucune"
    CARBURANT = "Carburant faible"
    PANNE = "Panne technique"
    METEO = "Conditions météo"


@dataclass
class Position:
    x: float
    y: float
    altitude: float


class Avion:
    def __init__(self, identifiant: str, position: Position, cap: float, vitesse: float):
        self.identifiant = identifiant
        self.position = position
        self.cap = cap  # en degrés
        self.vitesse = vitesse  # en km/h
        self.altitude_cible = position.altitude
        self.vitesse_cible = vitesse
        self.cap_cible = cap
        self.carburant = 100  # %
        self.etat = EtatAvion.EN_VOL
        self.urgence = TypeUrgence.AUCUNE
        self.en_attente = False
        self.temps_attente = 0

    def mettre_a_jour(self, delta_temps: float):
        """Met à jour la position et l'état de l'avion"""
        if self.etat == EtatAvion.ATTERRI:
            return

        # Gestion du carburant
        self.carburant -= 0.1 * delta_temps
        if self.carburant <= 0:
            self.carburant = 0
            self.urgence = TypeUrgence.CARBURANT

        # Gestion des urgences aléatoires
        if random.random() < 0.001 and self.urgence == TypeUrgence.AUCUNE:
            self.urgence = random.choice([TypeUrgence.PANNE, TypeUrgence.METEO])

        # Transition vers les valeurs cibles (pour un mouvement fluide)
        transition_vitesse = 0.1
        transition_cap = 0.05
        transition_altitude = 0.02

        self.vitesse += (self.vitesse_cible - self.vitesse) * transition_vitesse
        self.cap += (self.cap_cible - self.cap) * transition_cap
        self.position.altitude += (self.altitude_cible - self.position.altitude) * transition_altitude

        # Conversion vitesse km/h -> m/s pour le déplacement
        vitesse_ms = self.vitesse * 1000 / 3600

        # Calcul du déplacement
        cap_rad = math.radians(self.cap)
        dx = vitesse_ms * math.sin(cap_rad) * delta_temps
        dy = vitesse_ms * math.cos(cap_rad) * delta_temps

        # Mise à jour de la position
        self.position.x += dx
        self.position.y += dy

        # Gestion de l'attente
        if self.en_attente:
            self.temps_attente += delta_temps
            if self.temps_attente > 30:  # 30 secondes d'attente max
                self.en_attente = False
                self.temps_attente = 0

    def changer_cap(self, nouveau_cap: float):
        """Change le cap de l'avion"""
        self.cap_cible = nouveau_cap % 360

    def changer_altitude(self, nouvelle_altitude: float):
        """Change l'altitude de l'avion"""
        self.altitude_cible = max(1000, min(10000, nouvelle_altitude))

    def changer_vitesse(self, nouvelle_vitesse: float):
        """Change la vitesse de l'avion"""
        self.vitesse_cible = max(200, min(800, nouvelle_vitesse))

    def activer_attente(self):
        """Met l'avion en attente (tour d'attente)"""
        self.en_attente = True
        self.temps_attente = 0

    def preparer_atterrissage(self):
        """Prépare l'avion pour l'atterrissage"""
        self.etat = EtatAvion.EN_APPROCHE
        self.altitude_cible = 500
        self.vitesse_cible = 300

    def atterrir(self):
        """Fait atterrir l'avion"""
        self.etat = EtatAvion.ATTERRI
        self.vitesse_cible = 0

    def resoudre_urgence(self):
        """Résout l'urgence en cours"""
        self.urgence = TypeUrgence.AUCUNE

    def get_couleur(self) -> str:
        """Retourne la couleur en fonction de l'état"""
        if self.urgence != TypeUrgence.AUCUNE:
            return "#FF4444"  # Rouge pour urgence
        elif self.en_attente:
            return "#FFAA00"  # Orange pour attente
        elif self.etat == EtatAvion.EN_APPROCHE:
            return "#00FF00"  # Vert pour approche
        else:
            return "#4444FF"  # Bleu pour vol normal

    def get_info(self) -> str:
        """Retourne les informations de l'avion sous forme de texte"""
        urgence_str = f" • {self.urgence.value}" if self.urgence != TypeUrgence.AUCUNE else ""
        attente_str = " ⏱️" if self.en_attente else ""
        return f"{self.identifiant}{attente_str}\nAlt: {int(self.position.altitude)}m • V: {int(self.vitesse)}km/h • Cap: {int(self.cap)}° • Fuel: {int(self.carburant)}%{urgence_str}"