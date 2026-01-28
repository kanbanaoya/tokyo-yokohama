class Province:
    def __init__(self, name, terrain, owner, ic=1, is_hub=False, is_mega=False):
        self.name = name
        self.terrain = terrain
        self.owner = owner
        self.initial_owner = owner
        self.ic = ic
        self.is_hub = is_hub
        self.is_mega = is_mega
        self.units = []

class Unit:
    SPECS = {
        "普通科": {"speed": 4, "atk": 20, "def": 40, "cost": 150},
        "機甲": {"speed": 12, "atk": 50, "def": 20, "cost": 400},
        "山岳": {"speed": 5, "atk": 25, "def": 30, "cost": 200}
    }

    def __init__(self, uid, u_type, side, serial_number):
        s = self.SPECS[u_type]
        self.uid = uid
        self.u_type = u_type
        self.side = side
        self.serial_number = serial_number
        self.name = f"{side} {u_type} 第{serial_number}師団"
        self.hp = 100
        self.max_hp = 100
        self.attack = s["atk"]
        self.defense = s["def"]
        self.speed = s["speed"]
        self.location = ""
        self.destination = None
        self.path = []
        self.progress = 0