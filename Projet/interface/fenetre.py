from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QListWidget, QGroupBox,
                               QSpinBox, QSlider, QFrame, QScrollArea)
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

        # Panel gauche - Statistiques et liste avions
        panel_gauche = self.creer_panel_gauche()
        layout_principal.addWidget(panel_gauche, 1)

        # Panel central - Radar
        panel_central = self.creer_panel_central()
        layout_principal.addWidget(panel_central, 2)

        # Panel droit - Contrôles
        panel_droit = self.creer_panel_droit()
        layout_principal.addWidget(panel_droit, 1)

        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

    def creer_panel_gauche(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()

        # Titre
        titre = QLabel("ATC SIMULATOR")
        titre.setFont(QFont("Arial", 16, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        layout.addWidget(titre)

        # Statistiques
        stats_group = QGroupBox("STATISTIQUES")
        stats_layout = QVBoxLayout()

        self.label_score = QLabel("Score: 0")
        self.label_avions = QLabel("Avions: 0")
        self.label_niveau = QLabel("Niveau: 1")
        self.label_atterrissages = QLabel("Atterrissages: 0")
        self.label_collisions = QLabel("Collisions évitées: 0")

        for label in [self.label_score, self.label_avions, self.label_niveau,
                      self.label_atterrissages, self.label_collisions]:
            label.setFont(QFont("Arial", 10))
            stats_layout.addWidget(label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Liste des avions
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

        self.radar = RadarWidget(self.simulation)
        layout.addWidget(self.radar)

        panel.setLayout(layout)
        return panel

    def creer_panel_droit(self):
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        layout = QVBoxLayout()

        # Avion sélectionné
        selection_group = QGroupBox("AVION SÉLECTIONNÉ")
        selection_layout = QVBoxLayout()

        self.label_avion_selectionne = QLabel("Aucun avion sélectionné")
        self.label_avion_selectionne.setWordWrap(True)
        self.label_avion_selectionne.setFont(QFont("Arial", 10))
        selection_layout.addWidget(self.label_avion_selectionne)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Instructions
        instructions_group = QGroupBox("INSTRUCTIONS")
        instructions_layout = QVBoxLayout()

        # Contrôle d'altitude
        alt_group = QGroupBox("Altitude")
        alt_layout = QHBoxLayout()
        btn_monter = QPushButton("Monter +500m")
        btn_descendre = QPushButton("Descendre -500m")
        btn_monter.clicked.connect(lambda: self.changer_altitude(500))
        btn_descendre.clicked.connect(lambda: self.changer_altitude(-500))
        alt_layout.addWidget(btn_monter)
        alt_layout.addWidget(btn_descendre)
        alt_group.setLayout(alt_layout)
        instructions_layout.addWidget(alt_group)

        # Contrôle de cap
        cap_group = QGroupBox("Cap")
        cap_layout = QVBoxLayout()
        cap_buttons_layout = QHBoxLayout()

        btn_cap_0 = QPushButton("0° N")
        btn_cap_90 = QPushButton("90° E")
        btn_cap_180 = QPushButton("180° S")
        btn_cap_270 = QPushButton("270° O")

        for btn, cap in [(btn_cap_0, 0), (btn_cap_90, 90), (btn_cap_180, 180), (btn_cap_270, 270)]:
            btn.clicked.connect(lambda checked, c=cap: self.changer_cap(c))
            cap_buttons_layout.addWidget(btn)

        cap_layout.addLayout(cap_buttons_layout)

        # Sélecteur de cap précis
        cap_precis_layout = QHBoxLayout()
        label_cap = QLabel("Cap:")
        self.spin_cap = QSpinBox()
        self.spin_cap.setRange(0, 359)
        self.spin_cap.setValue(0)
        btn_appliquer_cap = QPushButton("Appliquer")
        btn_appliquer_cap.clicked.connect(self.appliquer_cap)

        cap_precis_layout.addWidget(label_cap)
        cap_precis_layout.addWidget(self.spin_cap)
        cap_precis_layout.addWidget(btn_appliquer_cap)
        cap_layout.addLayout(cap_precis_layout)

        cap_group.setLayout(cap_layout)
        instructions_layout.addWidget(cap_group)

        # Contrôle de vitesse
        vitesse_group = QGroupBox("Vitesse")
        vitesse_layout = QHBoxLayout()
        btn_accelerer = QPushButton("+50 km/h")
        btn_ralentir = QPushButton("-50 km/h")
        btn_accelerer.clicked.connect(lambda: self.changer_vitesse(50))
        btn_ralentir.clicked.connect(lambda: self.changer_vitesse(-50))
        vitesse_layout.addWidget(btn_accelerer)
        vitesse_layout.addWidget(btn_ralentir)
        vitesse_group.setLayout(vitesse_layout)
        instructions_layout.addWidget(vitesse_group)

        instructions_group.setLayout(instructions_layout)
        layout.addWidget(instructions_group)

        # Actions
        actions_group = QGroupBox("ACTIONS")
        actions_layout = QVBoxLayout()

        btn_atterrir = QPushButton("Préparer Atterrissage")
        btn_attente = QPushButton("Mettre en Attente")
        btn_urgence = QPushButton("Résoudre Urgence")

        btn_atterrir.clicked.connect(self.preparer_atterrissage)
        btn_attente.clicked.connect(self.mettre_attente)
        btn_urgence.clicked.connect(self.resoudre_urgence)

        for btn in [btn_atterrir, btn_attente, btn_urgence]:
            btn.setMinimumHeight(40)
            actions_layout.addWidget(btn)

        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)

        panel.setLayout(layout)
        return panel

    def mettre_a_jour_simulation(self):
        """Met à jour la simulation et l'interface"""
        self.simulation.mettre_a_jour(0.1)  # 0.1 seconde

        # Mise à jour des statistiques
        self.label_score.setText(f"Score: {self.simulation.score}")
        self.label_avions.setText(f"Avions: {len(self.simulation.avions)}")
        self.label_niveau.setText(f"Niveau: {self.simulation.niveau}")
        self.label_atterrissages.setText(f"Atterrissages: {self.simulation.avions_atterris}")
        self.label_collisions.setText(f"Collisions évitées: {self.simulation.collisions_evitees}")

        # Mise à jour de la liste des avions
        self.liste_avions.clear()
        for avion in self.simulation.avions:
            self.liste_avions.addItem(avion.get_info())

        # Mise à jour de l'avion sélectionné
        if self.simulation.avion_selectionne:
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
        else:
            self.label_avion_selectionne.setText(
                "Aucun avion sélectionné\n\nCliquez sur un avion dans la liste ou sur le radar pour le sélectionner")

    def selectionner_avion_liste(self, item):
        """Sélectionne un avion depuis la liste"""
        identifiant = item.text().split('\n')[0]
        self.simulation.selectionner_avion(identifiant)

    def changer_altitude(self, delta):
        if self.simulation.avion_selectionne:
            self.simulation.donner_instruction_altitude(delta)

    def changer_cap(self, nouveau_cap):
        if self.simulation.avion_selectionne:
            self.simulation.donner_instruction_cap(nouveau_cap)

    def appliquer_cap(self):
        if self.simulation.avion_selectionne:
            self.simulation.donner_instruction_cap(self.spin_cap.value())

    def changer_vitesse(self, delta):
        if self.simulation.avion_selectionne:
            self.simulation.donner_instruction_vitesse(delta)

    def preparer_atterrissage(self):
        if self.simulation.avion_selectionne:
            self.simulation.demander_atterrissage()

    def mettre_attente(self):
        if self.simulation.avion_selectionne:
            self.simulation.mettre_en_attente()

    def resoudre_urgence(self):
        if self.simulation.avion_selectionne:
            self.simulation.resoudre_urgence()