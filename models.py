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
    def __init__(self, uid, u_type, side):
        # 部隊ごとのスペック設定
        specs = {
            "歩兵": {"speed": 4, "atk": 20, "def": 40},
            "戦車": {"speed": 12, "atk": 50, "def": 20},
            "山岳兵": {"speed": 5, "atk": 25, "def": 30}
        }
        self.uid = uid
        self.u_type = u_type
        self.side = side
        self.hp = 100
        self.max_hp = 100
        self.speed = specs[u_type]["speed"]
        self.attack = specs[u_type]["atk"]
        self.defense = specs[u_type]["def"]
        self.location = ""
        self.destination = None # 最終目的地
        self.path = []         # 経由するルート
        self.progress = 0      # 現在の区間の進捗(km)
