import random
import math
from typing import List, Optional
from .avions import Avion, EtatAvion, TypeUrgence
from .position import Position

SPAWN_BASE_INTERVAL = 60.0
MAX_AVIONS_SIMULTANES = 6

class Simulation:
    def __init__(self):
        self.avions: List[Avion] = []
        self.temps_ecoule = 0.0
        self.score = 0
        self.niveau = 1
        self.avions_atterris = 0
        self.collisions_evitees = 0
        self.avion_selectionne: Optional[Avion] = None
        self.aire_atterrissage = Position(0, 0, 0)
        self.prochain_id = 1
        self.simulation_en_cours = False
        self.temps_debut = 0.0
        self.jeu_termine = False
        self.victoire = False
        self.temps_dernier_spawn = 0.0

    def demarrer_simulation(self):
        self.simulation_en_cours = True
        self.temps_debut = self.temps_ecoule
        self.temps_dernier_spawn = self.temps_ecoule
        self.jeu_termine = False
        self.victoire = False

    def arreter_simulation(self):
        self.simulation_en_cours = False

    def ajouter_avion_aleatoire(self):
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(15000, 30000)
        altitude = random.randint(2000, 8000)
        vitesse = random.randint(400, 600)
        cap = random.uniform(0, 360)
        identifiant = f"FL{self.prochain_id:04d}"
        self.prochain_id += 1
        position = Position(math.sin(angle) * distance, math.cos(angle) * distance, altitude)
        nouvel_avion = Avion(identifiant, position, cap, vitesse)
        self.avions.append(nouvel_avion)

    def mettre_a_jour(self, delta_temps: float):
        self.temps_ecoule += delta_temps
        if not self.simulation_en_cours:
            return
        interval = SPAWN_BASE_INTERVAL
        nb_en_vol = len([a for a in self.avions if a.etat != EtatAvion.ATTERRI])
        if (self.temps_ecoule - self.temps_dernier_spawn) >= interval and nb_en_vol < MAX_AVIONS_SIMULTANES:
            self.ajouter_avion_aleatoire()
            self.temps_dernier_spawn = self.temps_ecoule
        for avion in list(self.avions):
            avion.mettre_a_jour(delta_temps)
            if avion.urgence != TypeUrgence.AUCUNE:
                avion.temps_urgence += delta_temps
                perte_points = int(avion.temps_urgence)
                if perte_points > avion.points_urgence_perdus:
                    points_a_perdre = perte_points - avion.points_urgence_perdus
                    self.score = max(0, self.score - points_a_perdre)
                    avion.points_urgence_perdus = perte_points
            if avion.en_attente:
                tranches_10s = int(avion.temps_attente // 10)
                if tranches_10s > avion.points_attente_perdus:
                    points_a_perdre = (tranches_10s - avion.points_attente_perdus) * 5
                    self.score = max(0, self.score - points_a_perdre)
                    avion.points_attente_perdus = tranches_10s
        self.detecter_collisions()
        self.avions = [a for a in self.avions if a.etat != EtatAvion.ATTERRI]

    def distance_atterrissage(self, avion: Avion) -> float:
        dx = avion.position.x - self.aire_atterrissage.x
        dy = avion.position.y - self.aire_atterrissage.y
        return math.sqrt(dx * dx + dy * dy)

    def detecter_collisions(self):
        for i, avion1 in enumerate(self.avions):
            if avion1.etat == EtatAvion.ATTERRI:
                continue
            for j, avion2 in enumerate(self.avions[i + 1:], i + 1):
                if avion2.etat == EtatAvion.ATTERRI:
                    continue
                dx = avion1.position.x - avion2.position.x
                dy = avion1.position.y - avion2.position.y
                distance_horizontale = math.sqrt(dx * dx + dy * dy)
                distance_verticale = abs(avion1.position.altitude - avion2.position.altitude)
                if distance_horizontale < 500 and distance_verticale < 100:
                    self.score = max(0, self.score - 500)
                    self.collisions_evitees += 1

    def selectionner_avion(self, identifiant: str):
        for avion in self.avions:
            if avion.identifiant == identifiant:
                self.avion_selectionne = avion
                return
        self.avion_selectionne = None

    def donner_instruction_cap(self, nouveau_cap: float):
        if self.avion_selectionne:
            self.avion_selectionne.changer_cap(nouveau_cap)

    def donner_instruction_altitude(self, delta_altitude: float):
        if self.avion_selectionne:
            nouvelle_altitude = self.avion_selectionne.position.altitude + delta_altitude
            self.avion_selectionne.changer_altitude(nouvelle_altitude)

    def donner_instruction_vitesse(self, delta_vitesse: float):
        if self.avion_selectionne:
            nouvelle_vitesse = self.avion_selectionne.vitesse + delta_vitesse
            self.avion_selectionne.changer_vitesse(nouvelle_vitesse)

    def demander_atterrissage(self):
        if not self.avion_selectionne:
            return
        avion = self.avion_selectionne
        cond_alt = avion.position.altitude <= 100.0
        cond_vit = avion.vitesse <= 50.0
        distance = self.distance_atterrissage(avion)
        cond_zone_verte = distance < 5000.0 and avion.position.altitude < 1000.0
        if cond_alt and cond_vit and cond_zone_verte:
            avion.atterrir()
            try:
                self.avions.remove(avion)
            except ValueError:
                pass
            self.avions_atterris += 1
            self.score += 500
            self.avion_selectionne = None

    def mettre_en_attente(self):
        if self.avion_selectionne:
            self.avion_selectionne.activer_attente()

    def desactiver_attente(self):
        if self.avion_selectionne:
            self.avion_selectionne.desactiver_attente()

    def resoudre_urgence(self):
        if self.avion_selectionne and self.avion_selectionne.urgence != TypeUrgence.AUCUNE:
            self.avion_selectionne.resoudre_urgence()
            self.score += 25
