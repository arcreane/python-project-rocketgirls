from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QFrame)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont


class PageAccueil(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setAlignment(Qt.AlignCenter)
        layout_principal.setSpacing(30)

        # Titre principal
        titre = QLabel("SIMULATEUR DE CONTRÔLE AÉRIEN")
        titre.setFont(QFont("Arial", 28, QFont.Bold))
        titre.setAlignment(Qt.AlignCenter)
        titre.setStyleSheet("color: #2c3e50; margin: 20px; background: transparent;")
        layout_principal.addWidget(titre)

        # Cadre d'information
        cadre_info = QFrame()
        cadre_info.setFrameStyle(QFrame.Box)
        cadre_info.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                padding: 25px;
                margin: 20px;
            }
        """)
        layout_info = QVBoxLayout()

        # Instructions
        instructions = QLabel("VOTRE MISSION :")
        instructions.setFont(QFont("Arial", 18, QFont.Bold))
        instructions.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        layout_info.addWidget(instructions)

        texte_mission = QLabel(
            "Vous êtes contrôleur aérien !\n\n"
            "• Gérez l'espace aérien autour de votre aéroport\n"
            "• Donnez des instructions aux avions\n"
            "• Évitez les collisions et gérer les urgences\n"
            "• Faites atterrir les avions en sécurité\n"
        )
        texte_mission.setFont(QFont("Arial", 11))
        texte_mission.setStyleSheet("color: #2c3e50; line-height: 1.5;")
        texte_mission.setAlignment(Qt.AlignLeft)
        layout_info.addWidget(texte_mission)

        cadre_info.setLayout(layout_info)
        layout_principal.addWidget(cadre_info)

        # Contrôles principaux
        layout_boutons = QHBoxLayout()
        layout_boutons.setSpacing(20)

        # Bouton Commencer
        self.btn_commencer = QPushButton(" COMMENCER ")
        self.btn_commencer.setMinimumHeight(60)
        self.btn_commencer.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_commencer.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.btn_commencer.clicked.connect(self.lancer_simulation)

        # Bouton Quitter
        self.btn_quitter = QPushButton("QUITTER")
        self.btn_quitter.setMinimumHeight(60)
        self.btn_quitter.setFont(QFont("Arial", 14, QFont.Bold))
        self.btn_quitter.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border-radius: 8px;
                padding: 15px 30px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.btn_quitter.clicked.connect(self.quitter_application)

        layout_boutons.addWidget(self.btn_commencer)
        layout_boutons.addWidget(self.btn_quitter)
        layout_principal.addLayout(layout_boutons)

        self.setLayout(layout_principal)
        self.setStyleSheet("background-color: #ffffff;")

    def lancer_simulation(self):
        """Lance la simulation principale"""
        if self.parent:
            self.parent.afficher_simulateur()

    def quitter_application(self):
        """Quitte l'application"""
        if self.parent:
            self.parent.quitter()