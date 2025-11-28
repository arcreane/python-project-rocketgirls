class Position:
    def __init__(self, x=0, y=0, altitude=0):
        self.x = x
        self.y = y
        self.altitude = altitude

    def clone(self):
        return Position(self.x, self.y, self.altitude)

    def __str__(self):
        return f"Position(x={self.x:.0f}, y={self.y:.0f}, alt={self.altitude:.0f}m)"