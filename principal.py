import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from Projet.interface.fenetre import FenetrePrincipale
from Projet.models.simu import Simulation
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication(sys.argv)

    simulation = Simulation()

    fenetre = FenetrePrincipale(simulation)
    fenetre.show()

    sys.exit(app.exec())