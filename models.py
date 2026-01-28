class Province:
    def __init__(self, name, terrain, owner, ic, food, metal, oil, manpower, is_hub, x, y):
        # 土地の基本情報
        self.name = name
        self.terrain = terrain
        self.owner = owner  # 現在の領有勢力
        self.initial_owner = owner  # 初期の領有勢力（判定用）
        
        # 毎時の資源産出量
        self.ic = ic            # 工業力（資金に影響）
        self.food = food        # 食料
        self.metal = metal      # 金属
        self.oil = oil          # 石油
        self.manpower = manpower # 人的資源（毎時の加算量）
        
        # 戦略的属性と座標
        self.is_hub = is_hub    # 主要拠点かどうか
        self.x = x              # 地図上のX座標
        self.y = y              # 地図上のY座標
        
        # この土地に駐留している部隊のリスト
        self.units = []

    def __repr__(self):
        return f"<Province {self.name} ({self.owner})>"
class Unit:
    # 15兵科の全スペック: [攻撃, 防御, 射程, 速度, 金属, 石油, 食料, 資金, 人的, タイプ]
    SPECS = {
        "歩兵":     [20, 40, 0,  4,  10,   0, 100,  50, 1000, "陸"],
        "軽装甲":   [35, 25, 0, 14, 150,  80,  20, 120,  300, "陸"],
        "重装甲":   [65, 70, 0,  8, 400, 150,  30, 300,  500, "陸"],
        "対戦車":   [50, 20, 1,  5, 120,  30,  20, 150,  400, "陸"],
        "対空":     [30, 30, 2,  6, 180,  40,  20, 200,  400, "陸"],
        "哨戒機":   [15, 10, 8, 30, 100, 250,  10, 400,  100, "空"],
        "戦術爆撃": [55, 15, 8, 25, 250, 300,  10, 500,  200, "空"],
        "戦闘爆撃": [60, 20, 6, 22, 300, 350,  10, 600,  200, "空"],
        "潜水艦":   [70, 10, 2, 10, 300, 200,  50, 800,  150, "海"],
        "駆逐艦":   [30, 30, 3, 18, 400, 250,  60, 700,  300, "海"],
        "巡洋艦":   [50, 50, 4, 15, 700, 400,  80, 1200, 600, "海"],
        "戦艦":    [100, 90, 6, 10, 1500, 800, 150, 2500, 1200, "海"],
        "空母":     [20, 60, 5, 12, 1200, 1000, 200, 3000, 1500, "海"],
        "ミサイル": [150, 1, 15, 50, 200, 500,   0, 1000,   50, "空"],
        "輸送船":   [5,  5, 0,  8,  50,  50,  20, 100,  100, "海"]
    }

    def __init__(self, uid, u_type, side, serial_number):
        s = self.SPECS[u_type]
        self.uid = uid           # 識別ID（例: 神奈川-重装甲-1）
        self.u_type = u_type     # 兵科種別
        self.side = side         # 所属勢力
        self.name = f"{side} {u_type} 第{serial_number}師団"
        
        # 戦闘能力値
        self.hp = 100
        self.attack = s[0]
        self.defense = s[1]
        self.range = s[2]        # 遠隔攻撃の射程
        self.speed = s[3]        # 1時間あたりの移動km
        
        # 移動・状態管理
        self.location = ""       # 現在のプロビンス名
        self.path = []           # 移動予定のルート
        self.progress = 0        # 現在の道中の進捗（km）
        self.wait_minutes = 0    # 上陸・乗船ペナルティによる停止時間（分）

    def __repr__(self):
        return f"<{self.name} at {self.location}>"
