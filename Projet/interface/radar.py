from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QFont, QPolygonF
import math


class RadarWidget(QWidget):
    def __init__(self, simulation):
        super().__init__()
        self.simulation = simulation
        self.setMinimumSize(600, 600)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(50)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond
        painter.fillRect(self.rect(), QColor(0, 0, 50))

        centre_x = self.width() // 2
        centre_y = self.height() // 2
        rayon = min(centre_x, centre_y) - 40

        # Cercles concentriques
        painter.setPen(QPen(QColor(100, 100, 200), 1))
        for i in range(1, 6):
            r = rayon * i // 5
            painter.drawEllipse(centre_x - r, centre_y - r, 2 * r, 2 * r)

        # Lignes de référence principales (axes)
        painter.setPen(QPen(QColor(100, 100, 200), 2))
        painter.drawLine(centre_x, centre_y - rayon, centre_x, centre_y + rayon)
        painter.drawLine(centre_x - rayon, centre_y, centre_x + rayon, centre_y)

        # Lignes de référence secondaires (diagonales)
        painter.setPen(QPen(QColor(80, 80, 160), 1))
        diag_offset = int(rayon * 0.707)
        painter.drawLine(centre_x - diag_offset, centre_y - diag_offset,
                         centre_x + diag_offset, centre_y + diag_offset)
        painter.drawLine(centre_x - diag_offset, centre_y + diag_offset,
                         centre_x + diag_offset, centre_y - diag_offset)

        # Ajouter les marqueurs d'angles
        self.dessiner_marqueurs_angles(painter, centre_x, centre_y, rayon)

        # Centre (aéroport)
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawEllipse(centre_x - 10, centre_y - 10, 20, 20)

        # Dessiner les avions
        for avion in self.simulation.avions:
            self.dessiner_avion(painter, avion, centre_x, centre_y, rayon)

    def dessiner_marqueurs_angles(self, painter, centre_x, centre_y, rayon):
        """Dessine les marqueurs d'angles principaux et intermédiaires"""

        # Angles principaux et intermédiaires
        angles = [
            (0, "0°", QFont.Bold),
            (45, "45°", QFont.Normal),
            (90, "90°", QFont.Bold),
            (135, "135°", QFont.Normal),
            (180, "180°", QFont.Bold),
            (225, "225°", QFont.Normal),
            (270, "270°", QFont.Bold),
            (315, "315°", QFont.Normal)
        ]

        # Décalage pour positionner le texte à l'extérieur du radar
        text_offset = 25

        for angle, label, font_weight in angles:
            # Convertir l'angle pour le système de coordonnées (0° en haut, sens horaire)
            angle_rad = math.radians(angle - 90)

            # Position pour le texte (à l'extérieur du cercle)
            text_x = centre_x + (rayon + text_offset) * math.cos(angle_rad)
            text_y = centre_y + (rayon + text_offset) * math.sin(angle_rad)

            # Dessiner le texte
            if font_weight == QFont.Bold:
                painter.setFont(QFont("Arial", 12, QFont.Bold))
                painter.setPen(QPen(QColor(255, 255, 255), 2))
                mark_length = 15
            else:
                painter.setFont(QFont("Arial", 10, QFont.Normal))
                painter.setPen(QPen(QColor(200, 200, 200), 1))
                mark_length = 10

            # Centrer le texte
            text_width = len(label) * 6
            painter.drawText(int(text_x - text_width / 2), int(text_y + 5), label)

            # Dessiner une marque sur le cercle
            x1 = centre_x + rayon * math.cos(angle_rad)
            y1 = centre_y + rayon * math.sin(angle_rad)
            x2 = centre_x + (rayon - mark_length) * math.cos(angle_rad)
            y2 = centre_y + (rayon - mark_length) * math.sin(angle_rad)

            if font_weight == QFont.Bold:
                painter.setPen(QPen(QColor(150, 150, 255), 2))
            else:
                painter.setPen(QPen(QColor(120, 120, 200), 1))

            painter.drawLine(int(x1), int(y1), int(x2), int(y2))

    def dessiner_avion(self, painter, avion, centre_x, centre_y, rayon_max):
        echelle = rayon_max / 30000
        x = centre_x + avion.position.x * echelle
        y = centre_y + avion.position.y * echelle

        # Taille du triangle (plus grand pour être bien visible)
        taille = max(8, 12 - avion.position.altitude / 2000)

        # Couleur de l'avion selon son état
        couleur = QColor(avion.get_couleur())

        painter.setBrush(QBrush(couleur))
        painter.setPen(QPen(Qt.white, 1))

        # Calculer l'angle de rotation (cap de l'avion)
        angle_rad = math.radians(avion.cap)

        # Créer un triangle pointant dans la direction du cap
        # Point avant (nez de l'avion)
        nose_x = x + math.sin(angle_rad) * taille * 1.5
        nose_y = y - math.cos(angle_rad) * taille * 1.5

        # Point arrière gauche
        left_x = x + math.sin(angle_rad - 2.5) *taille * 0.7
        left_y = y - math.cos(angle_rad - 2.5) * taille * 0.7

        # Point arrière droit
        right_x = x + math.sin(angle_rad + 2.5) * taille * 0.7
        right_y = y - math.cos(angle_rad + 2.5) * taille * 0.7

        # Créer le triangle
        triangle = QPolygonF([
            QPointF(nose_x, nose_y),  # Nez
            QPointF(left_x, left_y),  # Arrière gauche
            QPointF(right_x, right_y)  # Arrière droit
        ])

        painter.drawPolygon(triangle)

        # Cercle de sélection si l'avion est sélectionné
        if avion == self.simulation.avion_selectionne:
            painter.setPen(QPen(Qt.yellow, 2))
            painter.drawEllipse(int(x - taille * 2), int(y - taille * 2),
                                int(taille * 4), int(taille * 4))

        # Afficher l'identifiant de l'avion
        if avion.position.altitude < 5000:
            painter.setPen(QPen(Qt.white))
            painter.setFont(QFont("Arial", 8))
            painter.drawText(int(x + taille * 2), int(y - taille * 2), avion.identifiant)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            centre_x = self.width() // 2
            centre_y = self.height() // 2
            rayon_max = min(centre_x, centre_y) - 40
            echelle = rayon_max / 30000

            click_x = (event.pos().x() - centre_x) / echelle
            click_y = (event.pos().y() - centre_y) / echelle

            avion_proche = None
            distance_min = 2000

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