import random
import math
from typing import List, Optional
from .avions import Avion, Position, EtatAvion


class Simulation:
    def __init__(self):
        self.avions: List[Avion] = []
        self.temps_ecoule = 0
        self.score = 0
        self.niveau = 1
        self.avions_atterris = 0
        self.collisions_evitees = 0
        self.avion_selectionne: Optional[Avion] = None
        self.aire_atterrissage = Position(0, 0, 0)
        self.prochain_id = 1
        self.simulation_en_cours = False

    def demarrer_simulation(self):
        """Démarre la simulation"""
        self.simulation_en_cours = True
        print("A vous de jouer !")

    def arreter_simulation(self):
        """Arrête la simulation"""
        self.simulation_en_cours = False
        print("Simulation arrêtée!")

    def ajouter_avion_aleatoire(self):
        """Ajoute un nouvel avion à une position aléatoire"""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(15000, 30000)
        altitude = random.randint(2000, 8000)
        vitesse = random.randint(400, 600)
        cap = (angle + math.pi) % (2 * math.pi)

        identifiant = f"FL{self.prochain_id:04d}"
        self.prochain_id += 1

        position = Position(
            x=math.sin(angle) * distance,
            y=math.cos(angle) * distance,
            altitude=altitude
        )

        nouvel_avion = Avion(identifiant, position, math.degrees(cap), vitesse)
        self.avions.append(nouvel_avion)
        print(f"Avion {identifiant} généré")

    def mettre_a_jour(self, delta_temps: float):
        """Met à jour toute la simulation"""
        self.temps_ecoule += delta_temps

        if not self.simulation_en_cours:
            return

        # Génération d'avions
        intervalle_generation = 10.0 / self.niveau
        if int(self.temps_ecoule / intervalle_generation) > int(
                (self.temps_ecoule - delta_temps) / intervalle_generation):
            if len([a for a in self.avions if a.etat != EtatAvion.ATTERRI.value]) < 10:
                self.ajouter_avion_aleatoire()

        if self.temps_ecoule > self.niveau * 60:
            self.niveau += 1

        for avion in self.avions:
            avion.mettre_a_jour(delta_temps)

            if (avion.etat == EtatAvion.EN_APPROCHE.value and
                    self.distance_atterrissage(avion) < 1000 and
                    avion.position.altitude < 600):
                avion.atterrir()
                self.avions_atterris += 1
                self.score += 100 * self.niveau

        self.detecter_collisions()
        self.avions = [a for a in self.avions if a.etat != EtatAvion.ATTERRI.value or random.random() < 0.99]

    def distance_atterrissage(self, avion: Avion) -> float:
        dx = avion.position.x - self.aire_atterrissage.x
        dy = avion.position.y - self.aire_atterrissage.y
        return math.sqrt(dx * dx + dy * dy)

    def detecter_collisions(self):
        for i, avion1 in enumerate(self.avions):
            if avion1.etat == EtatAvion.ATTERRI.value:
                continue

            for j, avion2 in enumerate(self.avions[i + 1:], i + 1):
                if avion2.etat == EtatAvion.ATTERRI.value:
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
        if self.avion_selectionne:
            self.avion_selectionne.preparer_atterrissage()

    def mettre_en_attente(self):
        if self.avion_selectionne:
            self.avion_selectionne.activer_attente()

    def resoudre_urgence(self):
        if self.avion_selectionne:
            self.avion_selectionne.resoudre_urgence()
            self.score += 50