from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QPen, QBrush, QColor, QPolygonF
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
        painter.setPen(QPen(QColor(100, 100, 200), 1))
        painter.drawLine(centre_x, 20, centre_x, self.height() - 20)
        painter.drawLine(20, centre_y, self.width() - 20, centre_y)

        # Étiquettes des directions
        painter.setPen(QPen(Qt.white))
        painter.drawText(centre_x - 10, 30, "N")
        painter.drawText(centre_x - 10, self.height() - 10, "S")
        painter.drawText(10, centre_y + 5, "O")
        painter.drawText(self.width() - 20, centre_y + 5, "E")

        # Aire d'atterrissage (centre)
        painter.setBrush(QBrush(QColor(0, 255, 0, 100)))
        painter.setPen(QPen(QColor(0, 255, 0), 2))
        painter.drawEllipse(centre_x - 10, centre_y - 10, 20, 20)

        # Affichage des avions
        for avion in self.simulation.avions:
            self.dessiner_avion(painter, avion, centre_x, centre_y, rayon)

        # Affichage des informations de portée
        painter.setPen(QPen(Qt.white))
        painter.drawText(10, 20, f"Portée: 30km")
        painter.drawText(10, 40, f"Avions: {len(self.simulation.avions)}")

    def dessiner_avion(self, painter, avion, centre_x, centre_y, rayon_max):
        """Dessine un avion sur le radar"""
        # Conversion coordonnées simulation -> radar
        echelle = rayon_max / 30000  # 30km de portée
        x = centre_x + avion.position.x * echelle
        y = centre_y + avion.position.y * echelle

        # Vérifier si l'avion est dans la portée du radar
        distance_centre = math.sqrt((x - centre_x) ** 2 + (y - centre_y) ** 2)
        if distance_centre > rayon_max:
            return  # Ne pas dessiner les avions hors portée

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

        # Points du triangle orienté
        points = [
            QPointF(x + dx, y + dy),  # Pointe avant (direction du cap)
            QPointF(x - dy, y + dx),  # Coin arrière droit
            QPointF(x - dx, y - dy),  # Pointe arrière
            QPointF(x + dy, y - dx)  # Coin arrière gauche
        ]

        # Créer et dessiner le polygone
        polygon = QPolygonF(points)
        painter.drawPolygon(polygon)

        # Sélection - mettre en évidence l'avion sélectionné
        if avion == self.simulation.avion_selectionne:
            painter.setPen(QPen(Qt.yellow, 2))
            painter.setBrush(QBrush(Qt.NoBrush))
            painter.drawEllipse(int(x - taille * 2), int(y - taille * 2),
                                int(taille * 4), int(taille * 4))

            # Dessiner une ligne vers le centre pour l'avion sélectionné
            painter.setPen(QPen(Qt.yellow, 1, Qt.DashLine))
            painter.drawLine(int(x), int(y), centre_x, centre_y)

        # Affichage de l'identifiant et informations
        if avion.position.altitude < 5000:  # Seulement si basse altitude
            painter.setPen(QPen(Qt.white))
            # Identifiant
            painter.drawText(int(x + taille * 2), int(y - taille * 2), avion.identifiant)

            # Altitude
            alt_text = f"{int(avion.position.altitude)}ft"
            painter.drawText(int(x + taille * 2), int(y + taille * 4), alt_text)

        # Dessiner la trajectoire récente
        self.dessiner_trajectoire(painter, avion, centre_x, centre_y, rayon_max)

    def dessiner_trajectoire(self, painter, avion, centre_x, centre_y, rayon_max):
        """Dessine la trajectoire récente de l'avion"""
        if not hasattr(avion, 'historique_positions') or len(avion.historique_positions) < 2:
            return

        echelle = rayon_max / 30000
        points_trajectoire = []

        # Prendre les 10 dernières positions
        for position in avion.historique_positions[-10:]:
            x = centre_x + position.x * echelle
            y = centre_y + position.y * echelle
            points_trajectoire.append(QPointF(x, y))

        # Dessiner la trajectoire
        painter.setPen(QPen(QColor(255, 255, 255, 150), 1, Qt.DashLine))
        for i in range(len(points_trajectoire) - 1):
            painter.drawLine(points_trajectoire[i], points_trajectoire[i + 1])

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

    def ajouter_historique_position(self, avion):
        """Ajoute la position actuelle à l'historique de l'avion"""
        if not hasattr(avion, 'historique_positions'):
            avion.historique_positions = []

        # Ajouter la position actuelle
        avion.historique_positions.append(avion.position.clone())

        # Garder seulement les 20 dernières positions
        if len(avion.historique_positions) > 20:
            avion.historique_positions.pop(0)