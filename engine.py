import math
import collections
import heapq

DISTANCE_MAP = {} # 接続関係と距離を保持

def get_distance(p1, p2):
    """三平方の定理で2点間の正確な距離を算出"""
    return math.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2)

def initialize_adjacencies(provinces, threshold=30):
    """
    全プロビンスをスキャンし、一定距離(threshold)内なら接続とみなす。
    これにより distances.csv の手動入力が不要になります。
    """
    adj_map = {}
    p_list = list(provinces.values())
    
    for i in range(len(p_list)):
        p1 = p_list[i]
        adj_map[p1.name] = {}
        for j in range(len(p_list)):
            if i == j: continue
            p2 = p_list[j]
            
            dist = get_distance(p1, p2)
            # 半径 threshold 以内なら隣接都市として登録
            if dist <= threshold:
                adj_map[p1.name][p2.name] = dist
                
    return adj_map

def get_move_speed_per_min(unit, target_p):
    """分単位の速度計算。海を渡る陸上ユニットは輸送船扱いで減速します。"""
    speed_per_min = unit.speed / 60
    # 人的資源(manpower)を多く要する陸上部隊が海に入る場合
    if target_p.terrain == "海" and unit.u_type in ["歩兵", "重装甲", "対戦車"]:
        speed_per_min *= 0.3 # 輸送船化による鈍足化
    return speed_per_min
def check_transition_penalty(u, current_p, next_p):
    """陸から海、海から陸への移動時に180分(3時間)のペナルティを課す"""
    if current_p.terrain != next_p.terrain:
        if current_p.terrain == "海" or next_p.terrain == "海":
            u.wait_minutes = 180 # 3時間の準備停滞
            print(f"[{u.name}] 渡河・上陸準備のため180分停滞します")

def find_path(start, goal, side, provinces, is_at_war):
    """ダイクストラ法による最短経路探索。敵地を避けるロジックを含む。"""
    if start == goal: return []
    
    queue = [(0, start, [])]
    seen = set()
    
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        if current in seen: continue
        
        seen.add(current)
        path = path + [current]
        
        if current == goal:
            return path[1:] # 開始地点を除いた経路を返す
            
        for nxt, dist in DISTANCE_MAP.get(current, {}).items():
            if nxt in seen: continue
            
            # 戦時下かつ陸地の場合、自勢力または中立以外の敵地は通過不可
            target_p = provinces[nxt]
            if is_at_war and target_p.terrain != "海" and target_p.owner != side:
                if target_p.owner != "なし": continue # 敵の領土は迂回
                
            heapq.heappush(queue, (cost + dist, nxt, path))
            
    return None # 経路なし

