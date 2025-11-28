import sys
import os

# Ajouter le dossier parent au path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Projet.interface.fenetre import FenetrePrincipale
from Projet.models.simu import Simulation
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Créer la simulation
    simulation = Simulation()

    # Créer et afficher la fenêtre principale
    fenetre = FenetrePrincipale(simulation)
    fenetre.show()

    sys.exit(app.exec())