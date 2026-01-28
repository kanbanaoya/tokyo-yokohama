import heapq

# 都市間の距離（km）を定義
DISTANCE_MAP = {
    "横浜": {"川崎": 12, "相模原": 25},
    "川崎": {"横浜": 12, "相模原": 20, "町田": 15},
    "相模原": {"横浜": 25, "川崎": 20, "箱根": 40, "町田": 10, "八王子": 15},
    "箱根": {"相模原": 40},
    "新宿": {"町田": 30, "八王子": 35},
    "町田": {"新宿": 30, "八王子": 15, "川崎": 15, "相模原": 10},
    "八王子": {"新宿": 35, "町田": 15, "奥多摩": 45, "相模原": 15},
    "奥多摩": {"八王子": 45}
}

# 自動経路探索関数
def find_path(start, goal, side, provinces, is_at_war):
    queue = [(0, start, [])]
    visited = set()
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        if current in visited: continue
        visited.add(current)
        path = path + [current]
        if current == goal: return path[1:] # 最初の現在地を除いた経路を返す

        for neighbor, dist in DISTANCE_MAP[current].items():
            # 平和時は敵地を通れない
            if not is_at_war and provinces[neighbor].owner != side: continue
            heapq.heappush(queue, (cost + dist, neighbor, path))
    return None

class Unit:
    def __init__(self, uid, u_type, side):
        specs = {
            "歩兵": {"speed": 4, "atk": 20, "def": 40},
            "戦車": {"speed": 12, "atk": 50, "def": 20}
        }
        self.uid, self.u_type, self.side = uid, u_type, side
        self.hp = 100
        self.speed = specs[u_type]["speed"]
        self.attack = specs[u_type]["atk"]
        self.defense = specs[u_type]["def"]
        self.location = ""
        self.path = [] # 自動進軍ルート
        self.progress = 0

# (シミュレーション部分の更新：Unit.pathがあれば自動で次の目的地をセットする)
