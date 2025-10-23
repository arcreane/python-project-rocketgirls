import random
import string


class Plane:
    def __init__(self, call_sign, alt, speed, head, fuel, pos):
        self.call_sign = call_sign
        self.alt = alt
        self.speed = speed
        self.head = head
        self.fuel = fuel
        self.pos = pos

    def get_info(self):
        return f"{self.call_sign} | Alt: {self.alt}m | Vit: {self.speed}km/h | Cap: {self.head}° | Fuel: {self.fuel}%"


class PlaneGen:
    def __init__(self):
        self.coef = 1

    def gen_plane(self, airspace_size=(10000, 10000)):
        letters = ''.join(random.choices(string.ascii_uppercase, k=2))
        call_sign = letters + str(random.randint(100, 999))
        alt = random.randint(2000, 5000)
        speed = random.randint(400, 600)
        head = random.randint(0, 359)
        fuel = random.randint(20, 100)
        pos = self.gen_pos(airspace_size)
        return Plane(call_sign, alt, speed, head, fuel, pos)

    def gen_pos(self, airspace_size):
        width, height = airspace_size
        side = random.choice(["top", "bottom", "left", "right"])

        if side == "top":
            return (random.uniform(0, width), height)
        elif side == "bottom":
            return (random.uniform(0, width), 0)
        elif side == "left":
            return (0, random.uniform(0, height))
        else:
            return (width, random.uniform(0, height))

    def gen_multiple_plane(self, count, airspace_size=(10000, 10000)):
        count = int(count * self.coef)
        plane = []
        for i in range(count):
            plane.append(self.gen_plane(airspace_size))
        return plane

    def increase_coef(self):
        self.coef += 0.5

    def get_coef(self):
        return self.coef