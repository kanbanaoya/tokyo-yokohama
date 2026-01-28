import heapq

# 都市間の距離データ
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

def find_path(start, goal, side, provinces, is_at_war):
    """ダイクストラ法による最短経路探索"""
    queue = [(0, start, [])]
    visited = set()
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        if current in visited: continue
        visited.add(current)
        path = path + [current]
        if current == goal: return path[1:] # 現在地を除いたリストを返す
        
        for neighbor, dist in DISTANCE_MAP.get(current, {}).items():
            # 平和時は敵地を通れない
            if not is_at_war and provinces[neighbor].owner != side: continue
            heapq.heappush(queue, (cost + dist, neighbor, path))
    return None

def get_move_speed(unit, target_province, hour):
    """地形や時間帯による実際の移動速度を計算"""
    speed = unit.speed
    # 通勤ラッシュ補正
    if target_province.is_mega and (7 <= hour % 24 <= 9 or 17 <= hour % 24 <= 19):
        speed *= 0.5
    # 山岳補正（山岳兵以外は夜にさらに遅くなる等、将来の拡張用）
    if target_province.terrain == "山岳" and unit.u_type != "山岳兵":
        speed *= 0.6
    return speed
