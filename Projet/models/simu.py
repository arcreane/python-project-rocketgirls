import random
import math
from typing import List, Optional
from . avions import Avion, EtatAvion, TypeUrgence
from .position import Position


class Simulation:
    def __init__(self):
        self. avions: List[Avion] = []
        self.temps_ecoule = 0
        self.score = 0
        self.niveau = 1
        self.avions_atterris = 0
        self.collisions_evitees = 0
        self. avion_selectionne: Optional[Avion] = None
        self.aire_atterrissage = Position(0, 0, 0)
        self.prochain_id = 1
        self.simulation_en_cours = False
        self.temps_debut = 0
        self.temps_dernier_niveau = 0
        self.jeu_termine = False  # ← AJOUTÉ : indicateur de fin de jeu
        self.victoire = False  # ← AJOUTÉ : indicateur de victoire

    def demarrer_simulation(self):
        """Démarre la simulation"""
        self.simulation_en_cours = True
        self.temps_debut = self.temps_ecoule
        self. temps_dernier_niveau = self.temps_ecoule
        self.jeu_termine = False
        self.victoire = False
        print("Simulation démarrée!")

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

        cap = random.uniform(0, 360)

        identifiant = f"FL{self.prochain_id:04d}"
        self.prochain_id += 1

        position = Position(
            x=math.sin(angle) * distance,
            y=math.cos(angle) * distance,
            altitude=altitude
        )

        nouvel_avion = Avion(identifiant, position, cap, vitesse)
        self.avions.append(nouvel_avion)

    def mettre_a_jour(self, delta_temps: float):
        """Met à jour toute la simulation"""
        self.temps_ecoule += delta_temps

        # Seulement si la simulation est en cours
        if not self.simulation_en_cours:
            return

        # Vérifier la condition de victoire : Niveau 5 terminé (fin des 3 minutes du niveau 5)
        if self.niveau >= 5:
            temps_niveau_5 = self.temps_ecoule - self.temps_dernier_niveau
            if temps_niveau_5 >= 180:  # 3 minutes = 180 secondes
                self.jeu_termine = True
                self.victoire = True
                self.simulation_en_cours = False
                print("VICTOIRE !  Vous avez terminé le jeu ! BRAVOOOO")
                return

        # Ajout d'avions selon le niveau
        if self.temps_ecoule % (30 / self.niveau) < delta_temps:
            if len([a for a in self.avions if a.etat != EtatAvion. ATTERRI]) < 10:
                self.ajouter_avion_aleatoire()

        # Augmentation du niveau TOUTES LES 3 MINUTES (180 secondes)
        if self.temps_ecoule - self.temps_dernier_niveau >= 180:
            self. niveau += 1
            self. temps_dernier_niveau = self.temps_ecoule
            print(f" NIVEAU {self.niveau} atteint!")

        # Mise à jour des avions
        for avion in self.avions:
            avion.mettre_a_jour(delta_temps)

            # Perte de points pour les urgences non résolues
            if avion. urgence != TypeUrgence. AUCUNE:
                avion.temps_urgence += delta_temps

                perte_points = int(avion.temps_urgence)
                if perte_points > avion.points_urgence_perdus:
                    points_a_perdre = perte_points - avion.points_urgence_perdus
                    self.score = max(0, self.score - points_a_perdre)
                    avion.points_urgence_perdus = perte_points
                    if points_a_perdre > 0:
                        print(f" {avion.identifiant} - Urgence non résolue: -{points_a_perdre} point(s)")

            # Vérification de l'atterrissage final
            if (avion.etat == EtatAvion.EN_APPROCHE and
                    self.distance_atterrissage(avion) < 100 and
                    avion.position.altitude < 50 and
                    avion.vitesse < 100):
                avion. atterrir()
                self.avions_atterris += 1
                self.score += 100 * self.niveau
                print(f" {avion.identifiant} a atterri avec succès!   +{100 * self.niveau} points")

        # Vérification des collisions
        self.detecter_collisions()

        # Nettoyage des avions atterris
        self.avions = [a for a in self.avions if a.etat != EtatAvion. ATTERRI or random.random() < 0.99]

    def distance_atterrissage(self, avion: Avion) -> float:
        """Calcule la distance à la piste d'atterrissage"""
        dx = avion.position.x - self.aire_atterrissage.x
        dy = avion.position.y - self. aire_atterrissage. y
        return math.sqrt(dx * dx + dy * dy)

    def detecter_collisions(self):
        """Détecte les collisions entre avions"""
        for i, avion1 in enumerate(self.avions):
            if avion1.etat == EtatAvion.ATTERRI:
                continue

            for j, avion2 in enumerate(self.avions[i + 1:], i + 1):
                if avion2.etat == EtatAvion.ATTERRI:
                    continue

                dx = avion1.position.x - avion2.position.x
                dy = avion1. position.y - avion2. position.y
                distance_horizontale = math.sqrt(dx * dx + dy * dy)

                distance_verticale = abs(avion1.position.altitude - avion2.position.altitude)

                if distance_horizontale < 500 and distance_verticale < 100:
                    self.score = max(0, self.score - 500)
                    self.collisions_evitees += 1
                    print(f"Collision évitée de justesse!   -{500} points")

    def selectionner_avion(self, identifiant: str):
        """Sélectionne un avion par son identifiant"""
        for avion in self.avions:
            if avion.identifiant == identifiant:
                self.avion_selectionne = avion
                return
        self.avion_selectionne = None

    def donner_instruction_cap(self, nouveau_cap: float):
        """Donne l'instruction de changer de cap à l'avion sélectionné"""
        if self.avion_selectionne:
            self.avion_selectionne. changer_cap(nouveau_cap)

    def donner_instruction_altitude(self, delta_altitude: float):
        """Donne l'instruction de changer d'altitude à l'avion sélectionné"""
        if self.avion_selectionne:
            nouvelle_altitude = self.avion_selectionne.position. altitude + delta_altitude
            self.avion_selectionne. changer_altitude(nouvelle_altitude)

    def donner_instruction_vitesse(self, delta_vitesse: float):
        """Donne l'instruction de changer de vitesse à l'avion sélectionné"""
        if self.avion_selectionne:
            nouvelle_vitesse = self.avion_selectionne.vitesse + delta_vitesse
            self. avion_selectionne.changer_vitesse(nouvelle_vitesse)

    def demander_atterrissage(self):
        """Demande l'atterrissage pour l'avion sélectionné - AVEC CONDITIONS"""
        if not self.avion_selectionne:
            return

        avion = self.avion_selectionne
        distance = self.distance_atterrissage(avion)

        if distance < 1000 and avion.position.altitude < 600:
            avion.preparer_atterrissage()
            print(f"{avion.identifiant} autorisé pour l'approche finale!")
            print(f"   Distance: {int(distance)}m, Altitude: {int(avion.position.altitude)}m")
        else:
            print(f"{avion.identifiant} - Conditions non remplies pour l'approche:")
            if distance >= 1000:
                print(f"   Distance trop grande: {int(distance)}m (doit être < 1000m)")
            if avion.position. altitude >= 600:
                print(f"   Altitude trop élevée: {int(avion.position.altitude)}m (doit être < 600m)")

    def mettre_en_attente(self):
        """Met l'avion sélectionné en attente"""
        if self.avion_selectionne:
            self.avion_selectionne. activer_attente()

    def resoudre_urgence(self):
        """Résoud l'urgence de l'avion sélectionné - +25 points"""
        if self.avion_selectionne and self.avion_selectionne.urgence != TypeUrgence.AUCUNE:
            temps_urgence = self.avion_selectionne.temps_urgence
            self.avion_selectionne.resoudre_urgence()
            self.score += 25
            print(f"Urgence résolue pour {self.avion_selectionne.identifiant}!   +25 points")
            print(f"   (Urgence durée: {int(temps_urgence)}s)")