import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QFrame)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPainter, QPen, QColor, QBrush, QPolygonF
from PySide6.QtCore import QPointF
import random
import string
import math


class Plane:
    def __init__(self, call_sign, alt, speed, head, fuel, pos):
        self.call_sign = call_sign
        self.alt = alt
        self.speed = speed
        self.head = head
        self.fuel = fuel
        self.pos = pos
        self.selected = False


class PlaneGen:
    def __init__(self):
        self.coef = 1

    def gen_plane(self):
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        call_sign = letters + str(random.randint(100, 999))
        alt = random.randint(2000, 5000)
        speed = random.randint(400, 600)
        head = random.randint(0, 359)
        fuel = random.randint(20, 100)
        pos = (random.randint(50, 750), random.randint(50, 350))
        return Plane(call_sign, alt, speed, head, fuel, pos)

    def gen_multiple_plane(self, count):
        count = int(count * self.coef)
        planes = []
        for i in range(count):
            planes.append(self.gen_plane())
        return planes


class RadarWidget(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.planes = []
        self.main_window = main_window
        self.setMinimumSize(800, 400)

    def mousePressEvent(self, event):
        click_pos = (event.position().x(), event.position().y())

        for plane in self.planes:
            x, y = plane.pos
            distance = ((click_pos[0] - x) ** 2 + (click_pos[1] - y) ** 2) ** 0.5

            if distance < 20:
                for p in self.planes:
                    p.selected = False
                plane.selected = True
                self.main_window.show_plane_info(plane)
                self.update()
                break

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Fond bleu clair
        painter.fillRect(self.rect(), QColor(173, 216, 230))

        # Dessiner la boussole (sans lettres)
        self.draw_compass(painter)

        # Dessiner les avions
        for plane in self.planes:
            self.draw_plane(painter, plane)

    def draw_compass(self, painter):
        center_x = self.width() // 2
        center_y = self.height() // 2
        max_radius = min(center_x, center_y) - 30

        # Cercles concentriques
        painter.setPen(QPen(QColor(100, 100, 150), 2))
        for i in range(1, 6):
            radius = max_radius * i // 5
            painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # Lignes cardinales (sans texte)
        painter.setPen(QPen(QColor(0, 0, 0), 2))
        painter.drawLine(center_x, 0, center_x, self.height())
        painter.drawLine(0, center_y, self.width(), center_y)

    def draw_plane(self, painter, plane):
        x, y = plane.pos

        # Violet pétant
        if plane.selected:
            color = QColor(255, 0, 255)  # Violet pétant si sélectionné
            size = 14
        else:
            color = QColor(255, 0, 255)  # Violet pétant normal
            size = 12

        painter.setPen(QPen(color, 2))
        painter.setBrush(QBrush(color))

        # Convertir le cap en radians (0° = Nord, 90° = Est, etc.)
        heading_rad = math.radians(plane.head - 90)  # -90 pour que 0° pointe vers le haut

        # Points du triangle orienté selon le cap
        tip_x = x + size * math.cos(heading_rad)
        tip_y = y + size * math.sin(heading_rad)

        left_x = x + size * 0.6 * math.cos(heading_rad + 2.5)  # +140° environ
        left_y = y + size * 0.6 * math.sin(heading_rad + 2.5)

        right_x = x + size * 0.6 * math.cos(heading_rad - 2.5)  # -140° environ
        right_y = y + size * 0.6 * math.sin(heading_rad - 2.5)

        triangle = QPolygonF([
            QPointF(tip_x, tip_y),  # Pointe de la flèche
            QPointF(left_x, left_y),  # Coin gauche
            QPointF(right_x, right_y)  # Coin droit
        ])

        painter.drawPolygon(triangle)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.plane_gen = PlaneGen()
        self.planes = []

        self.setWindowTitle("Radar Tour de Contrôle")
        self.setGeometry(100, 100, 1200, 600)

        self.setup_ui()
        self.setup_timer()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Cadre gauche - Radar
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)

        self.radar = RadarWidget(self)
        left_layout.addWidget(self.radar)

        # Cadre droit - Informations
        right_frame = QFrame()
        right_frame.setFixedWidth(300)
        right_layout = QVBoxLayout(right_frame)

        title_label = QLabel("INFORMATIONS AVION")
        title_label.setStyleSheet("color: blue; font-size: 16px; font-weight: bold; padding: 10px;")

        self.info_label = QLabel("Cliquez sur une flèche violette")
        self.info_label.setStyleSheet(
            "color: blue; font-size: 14px; padding: 15px; background-color: #e6f3ff; border: 2px solid #0066cc; border-radius: 10px;")
        self.info_label.setMinimumHeight(150)
        self.info_label.setWordWrap(True)

        right_layout.addWidget(title_label)
        right_layout.addWidget(self.info_label)
        right_layout.addStretch()

        layout.addWidget(left_frame)
        layout.addWidget(right_frame)

    def setup_timer(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_planes)
        self.timer.start(2000)

    def update_planes(self):
        new_planes = self.plane_gen.gen_multiple_plane(1)
        self.planes.extend(new_planes)

        self.radar.planes = self.planes
        self.radar.update()

    def show_plane_info(self, plane):
        info_text = f"Nom: {plane.call_sign}\nAltitude: {plane.alt}m\nVitesse: {plane.speed}km/h\nCap: {plane.head}°\nCarburant: {plane.fuel}%"
        self.info_label.setText(info_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
