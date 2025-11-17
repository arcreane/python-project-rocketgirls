from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont
import math


class RadarWidget(QWidget):
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.setMinimumSize(600, 600)

        # Timer pour les mises à jour
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)  # 20 FPS

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond
        painter.fillRect(self.rect(), QColor(0, 0, 50))

        # Dimensions
        centre_x = self.width() // 2
        centre_y = self.height() // 2
        rayon = min(centre_x, centre_y) - 20

        # Cercles concentriques
        painter.setPen(QPen(QColor(100, 100, 200), 1))
        for i in range(1, 6):
            r = rayon * i // 5
            painter.drawEllipse(centre_x - r, centre_y - r, 2 * r, 2 * r)

        # Lignes cardinales
        painter.drawLine(centre_x, 20, centre_x, self.height() - 20)
        painter.drawLine(20, centre_y, self.width() - 20, centre_y)

        # Aire d'atterrissage (centre)
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawEllipse(centre_x - 10, centre_y - 10, 20, 20)

        # Affichage des avions
        for avion in self.simulation.avions:
            self.dessiner_avion(painter, avion, centre_x, centre_y, rayon)

    def dessiner_avion(self, painter, avion, centre_x, centre_y, rayon_max):
        """Dessine un avion sur le radar"""
        # Conversion coordonnées simulation -> radar
        echelle = rayon_max / 30000  # 30km de portée
        x = centre_x + avion.position.x * echelle
        y = centre_y + avion.position.y * echelle

        # Taille en fonction de l'altitude
        taille = max(3, 8 - avion.position.altitude / 2000)

        # Couleur selon l'état
        couleur = QColor(avion.get_couleur())

        # Dessin de l'avion
        painter.setBrush(QBrush(couleur))
        painter.setPen(QPen(Qt.white, 1))

        # Triangle orienté selon le cap
        angle_rad = math.radians(avion.cap)
        dx = math.sin(angle_rad) * taille
        dy = -math.cos(angle_rad) * taille

        points = [
            (x + dx, y + dy),
            (x - dy, y + dx),
            (x - dx, y - dy),
            (x + dy, y - dx)
        ]

        painter.drawPolygon(*[self.point_to_qpoint(p) for p in points])

        # Sélection
        if avion == self.simulation.avion_selectionne:
            painter.setPen(QPen(Qt.yellow, 2))
            painter.drawEllipse(int(x - taille * 2), int(y - taille * 2),
                                int(taille * 4), int(taille * 4))

        # Affichage de l'identifiant
        if avion.position.altitude < 5000:  # Seulement si basse altitude
            painter.setPen(QPen(Qt.white))
            painter.drawText(int(x + taille * 2), int(y - taille * 2), avion.identifiant)

    def point_to_qpoint(self, point):
        """Convertit un tuple (x,y) en QPoint"""
        from PySide6.QtCore import QPoint
        return QPoint(int(point[0]), int(point[1]))

    def mousePressEvent(self, event):
        """Gère la sélection d'avion par clic"""
        if event.button() == Qt.LeftButton:
            # Conversion coordonnées clic -> simulation
            centre_x = self.width() // 2
            centre_y = self.height() // 2
            rayon_max = min(centre_x, centre_y) - 20
            echelle = rayon_max / 30000

            click_x = (event.pos().x() - centre_x) / echelle
            click_y = (event.pos().y() - centre_y) / echelle

            # Recherche de l'avion le plus proche
            avion_proche = None
            distance_min = 2000  # 2km de tolérance

            for avion in self.simulation.avions:
                dx = avion.position.x - click_x
                dy = avion.position.y - click_y
                distance = math.sqrt(dx * dx + dy * dy)

                if distance < distance_min:
                    distance_min = distance
                    avion_proche = avion

            if avion_proche:
                self.simulation.selectionner_avion(avion_proche.identifiant)
                self.update()
