from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QListWidget, QGroupBox,
                               QSpinBox, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from .radar import RadarWidget


class FenetrePrincipale(QMainWindow):
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.setWindowTitle("Simulateur de Contrôle Aérien - IPSA")
        self.setGeometry(100, 100, 1400, 800)

        self.timer_simulation = QTimer()
        self.timer_simulation.timeout.connect(self.mettre_a_jour_simulation)
        self.timer_simulation.start(100)

        self.init_ui()

    def init_ui(self):
        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        panel_gauche = self.creer_panel_gauche()
        layout_principal.addWidget(panel_gauche, 1)

        panel_central = self.creer_panel_central()
        layout_principal.addWidget(panel_central, 2)

        panel_droit = self.creer_panel_droit()
        layout_principal.addWidget(panel_droit, 1)

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

    def creer_panel_gauche(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()

        titre = QLabel("ATC SIMULATOR")
        titre.setFont(QFont("Arial", 16, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)

        # SECTION CONTRÔLE SIMULATION
        controle_group = QGroupBox("CONTRÔLE SIMULATION")
        controle_layout = QVBoxLayout()

        self.btn_commencer = QPushButton("🚀 COMMENCER")
        self.btn_commencer.setMinimumHeight(50)
        self.btn_commencer.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_commencer.clicked.connect(self.commencer_simulation)

        self.btn_arreter = QPushButton("⏹️ ARRÊTER")
        self.btn_arreter.setMinimumHeight(40)
        self.btn_arreter.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.btn_arreter.clicked.connect(self.arreter_simulation)
        self.btn_arreter.setEnabled(False)

        self.btn_reinitialiser = QPushButton("🔄 RÉINITIALISER")
        self.btn_reinitialiser.setMinimumHeight(40)
        self.btn_reinitialiser.clicked.connect(self.reinitialiser_simulation)

        controle_layout.addWidget(self.btn_commencer)
        controle_layout.addWidget(self.btn_arreter)
        controle_layout.addWidget(self.btn_reinitialiser)
        controle_group.setLayout(controle_layout)
        layout.addWidget(controle_group)

        # STATISTIQUES
        stats_group = QGroupBox("STATISTIQUES")
        stats_layout = QVBoxLayout()

        self.label_score = QLabel("Score: 0")
        self.label_avions = QLabel("Avions: 0")
        self.label_niveau = QLabel("Niveau: 1")
        self.label_atterrissages = QLabel("Atterrissages: 0")
        self.label_collisions = QLabel("Collisions évitées: 0")
        self.label_etat_simulation = QLabel("État: En attente")

        for label in [self.label_score, self.label_avions, self.label_niveau,
                      self.label_atterrissages, self.label_collisions, self.label_etat_simulation]:
            label.setFont(QFont("Arial", 10))
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # LISTE DES AVIONS
        avions_group = QGroupBox("AVIONS EN VOL")
        avions_layout = QVBoxLayout()

        self.liste_avions = QListWidget()
        self.liste_avions.itemClicked.connect(self.selectionner_avion_liste)
        avions_layout.addWidget(self.liste_avions)

        avions_group.setLayout(avions_layout)
        layout.addWidget(avions_group)

        panel.setLayout(layout)
        return panel

    def creer_panel_central(self):
        panel = QFrame()
        layout = QVBoxLayout()

        # MESSAGE D'ACCUEIL
        self.label_accueil = QLabel("🎯 SIMULATEUR DE CONTRÔLE AÉRIEN\n\n"
                                    "Cliquez sur 'COMMENCER' pour démarrer la simulation\n"
                                    "et gérer l'espace aérien !")
        self.label_accueil.setAlignment(Qt.AlignCenter)
        self.label_accueil.setFont(QFont("Arial", 16))
        self.label_accueil.setStyleSheet("color: #666666; background-color: #f0f0f0; padding: 20px;")

        self.radar = RadarWidget(self.simulation)

        layout.addWidget(self.label_accueil)
        layout.addWidget(self.radar)

        # Masquer le radar au début
        self.radar.setVisible(False)

        panel.setLayout(layout)
        return panel

    def creer_panel_droit(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()

        # AVION SÉLECTIONNÉ
        selection_group = QGroupBox("AVION SÉLECTIONNÉ")
        selection_layout = QVBoxLayout()

        self.label_avion_selectionne = QLabel("Aucun avion sélectionné\n\n"
                                              "La simulation n'est pas encore démarrée")
        self.label_avion_selectionne.setWordWrap(True)
        self.label_avion_selectionne.setFont(QFont("Arial", 10))
        selection_layout.addWidget(self.label_avion_selectionne)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # INSTRUCTIONS
        instructions_group = QGroupBox("INSTRUCTIONS")
        instructions_layout = QVBoxLayout()

        self.controles_actifs = False

        # ALTITUDE
        alt_group = QGroupBox("Altitude")
        alt_layout = QHBoxLayout()
        self.btn_monter = QPushButton("Monter +500m")
        self.btn_descendre = QPushButton("Descendre -500m")
        self.btn_monter.clicked.connect(lambda: self.changer_altitude(500))
        self.btn_descendre.clicked.connect(lambda: self.changer_altitude(-500))
        alt_layout.addWidget(self.btn_monter)
        alt_layout.addWidget(self.btn_descendre)
        alt_group.setLayout(alt_layout)
        instructions_layout.addWidget(alt_group)

        # CAP
        cap_group = QGroupBox("Cap")
        cap_layout = QVBoxLayout()
        cap_buttons_layout = QHBoxLayout()

        self.btn_cap_0 = QPushButton("0° N")
        self.btn_cap_90 = QPushButton("90° E")
        self.btn_cap_180 = QPushButton("180° S")
        self.btn_cap_270 = QPushButton("270° O")

        for btn, cap in [(self.btn_cap_0, 0), (self.btn_cap_90, 90),
                         (self.btn_cap_180, 180), (self.btn_cap_270, 270)]:
            btn.clicked.connect(lambda checked, c=cap: self.changer_cap(c))
            cap_buttons_layout.addWidget(btn)

        cap_layout.addLayout(cap_buttons_layout)

        cap_precis_layout = QHBoxLayout()
        label_cap = QLabel("Cap:")
        self.spin_cap = QSpinBox()
        self.spin_cap.setRange(0, 359)
        self.spin_cap.setValue(0)
        self.btn_appliquer_cap = QPushButton("Appliquer")
        self.btn_appliquer_cap.clicked.connect(self.appliquer_cap)

        cap_precis_layout.addWidget(label_cap)
        cap_precis_layout.addWidget(self.spin_cap)
        cap_precis_layout.addWidget(self.btn_appliquer_cap)
        cap_layout.addLayout(cap_precis_layout)

        cap_group.setLayout(cap_layout)
        instructions_layout.addWidget(cap_group)

        # VITESSE
        vitesse_group = QGroupBox("Vitesse")
        vitesse_layout = QHBoxLayout()
        self.btn_accelerer = QPushButton("+50 km/h")
        self.btn_ralentir = QPushButton("-50 km/h")
        self.btn_accelerer.clicked.connect(lambda: self.changer_vitesse(50))
        self.btn_ralentir.clicked.connect(lambda: self.changer_vitesse(-50))
        vitesse_layout.addWidget(self.btn_accelerer)
        vitesse_layout.addWidget(self.btn_ralentir)
        vitesse_group.setLayout(vitesse_layout)
        instructions_layout.addWidget(vitesse_group)

        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)

        # ACTIONS
        actions_group = QGroupBox("ACTIONS")
        actions_layout = QVBoxLayout()

        self.btn_atterrir = QPushButton("Préparer Atterrissage")
        self.btn_attente = QPushButton("Mettre en Attente")
        self.btn_urgence = QPushButton("Résoudre Urgence")

        self.btn_atterrir.clicked.connect(self.preparer_atterrissage)
        self.btn_attente.clicked.connect(self.mettre_attente)
        self.btn_urgence.clicked.connect(self.resoudre_urgence)

        for btn in [self.btn_atterrir, self.btn_attente, self.btn_urgence]:
            btn.setMinimumHeight(40)
            actions_layout.addWidget(btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        # Désactiver tous les contrôles au début
        self.desactiver_controles()

        panel.setLayout(layout)
        return panel

    # MÉTHODES DE CONTRÔLE DE LA SIMULATION
    def commencer_simulation(self):
        """Démarre la simulation"""
        self.simulation.demarrer_simulation()
        self.btn_commencer.setEnabled(False)
        self.btn_arreter.setEnabled(True)
        self.label_etat_simulation.setText("État: En cours")
        self.label_etat_simulation.setStyleSheet("color: green; font-weight: bold;")

        # Afficher le radar et masquer le message d'accueil
        self.radar.setVisible(True)
        self.label_accueil.setVisible(False)

        # Activer les contrôles
        self.activer_controles()

        # Ajouter quelques avions initiaux
        for _ in range(3):
            self.simulation.ajouter_avion_aleatoire()

    def arreter_simulation(self):
        """Arrête la simulation"""
        self.simulation.arreter_simulation()
        self.btn_commencer.setEnabled(True)
        self.btn_arreter.setEnabled(False)
        self.label_etat_simulation.setText("État: Arrêtée")
        self.label_etat_simulation.setStyleSheet("color: red;")

        # Désactiver les contrôles
        self.desactiver_controles()

    def reinitialiser_simulation(self):
        """Réinitialise la simulation"""
        from Projet.models.simu import Simulation
        self.simulation = Simulation()
        self.radar.simulation = self.simulation
        self.btn_commencer.setEnabled(True)
        self.btn_arreter.setEnabled(False)
        self.label_etat_simulation.setText("État: En attente")
        self.label_etat_simulation.setStyleSheet("color: black;")

        # Réafficher le message d'accueil
        self.radar.setVisible(False)
        self.label_accueil.setVisible(True)

        # Désactiver les contrôles
        self.desactiver_controles()

        # Mettre à jour l'affichage
        self.mettre_a_jour_simulation()

    def activer_controles(self):
        """Active tous les contrôles"""
        for widget in [self.btn_monter, self.btn_descendre, self.btn_cap_0,
                       self.btn_cap_90, self.btn_cap_180, self.btn_cap_270,
                       self.spin_cap, self.btn_appliquer_cap, self.btn_accelerer,
                       self.btn_ralentir, self.btn_atterrir, self.btn_attente,
                       self.btn_urgence]:
            widget.setEnabled(True)
        self.controles_actifs = True

    def desactiver_controles(self):
        """Désactive tous les contrôles"""
        for widget in [self.btn_monter, self.btn_descendre, self.btn_cap_0,
                       self.btn_cap_90, self.btn_cap_180, self.btn_cap_270,
                       self.spin_cap, self.btn_appliquer_cap, self.btn_accelerer,
                       self.btn_ralentir, self.btn_atterrir, self.btn_attente,
                       self.btn_urgence]:
            widget.setEnabled(False)
        self.controles_actifs = False

    # MÉTHODES DE MISE À JOUR
    def mettre_a_jour_simulation(self):
        """Met à jour la simulation et l'interface"""
        self.simulation.mettre_a_jour(0.1)

        self.label_score.setText(f"Score: {self.simulation.score}")
        self.label_avions.setText(f"Avions: {len(self.simulation.avions)}")
        self.label_niveau.setText(f"Niveau: {self.simulation.niveau}")
        self.label_atterrissages.setText(f"Atterrissages: {self.simulation.avions_atterris}")
        self.label_collisions.setText(f"Collisions évitées: {self.simulation.collisions_evitees}")

        self.liste_avions.clear()
        for avion in self.simulation.avions:
            self.liste_avions.addItem(avion.get_info())

        if self.simulation.avion_selectionne and self.controles_actifs:
            avion = self.simulation.avion_selectionne
            info = f"{avion.identifiant}\n\n"
            info += f"Altitude: {int(avion.position.altitude)}m\n"
            info += f"Vitesse: {int(avion.vitesse)} km/h\n"
            info += f"Cap: {int(avion.cap)}°\n"
            info += f"Carburant: {int(avion.carburant)}%\n"
            info += f"État: {avion.etat.value}\n"
            if avion.urgence != avion.urgence.AUCUNE:
                info += f"URGENCE: {avion.urgence.value}"
            if avion.en_attente:
                info += f"⏱️ En attente: {int(avion.temps_attente)}s"

            self.label_avion_selectionne.setText(info)
        elif not self.controles_actifs:
            self.label_avion_selectionne.setText("Aucun avion sélectionné\n\n"
                                                 "La simulation n'est pas démarrée")
        else:
            self.label_avion_selectionne.setText("Aucun avion sélectionné\n\n"
                                                 "Cliquez sur un avion dans la liste ou sur le radar pour le sélectionner")

    def selectionner_avion_liste(self, item):
        if not self.controles_actifs:
            return
        identifiant = item.text().split('\n')[0]
        self.simulation.selectionner_avion(identifiant)

    def changer_altitude(self, delta):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.donner_instruction_altitude(delta)

    def changer_cap(self, nouveau_cap):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.donner_instruction_cap(nouveau_cap)

    def appliquer_cap(self):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.donner_instruction_cap(self.spin_cap.value())

    def changer_vitesse(self, delta):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.donner_instruction_vitesse(delta)

    def preparer_atterrissage(self):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.demander_atterrissage()

    def mettre_attente(self):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.mettre_en_attente()

    def resoudre_urgence(self):
        if self.simulation.avion_selectionne and self.controles_actifs:
            self.simulation.resoudre_urgence()