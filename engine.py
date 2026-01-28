import heapq

# main.pyから上書きされるため、初期値は空
DISTANCE_MAP = {}

def find_path(start, goal, side, provinces, is_at_war):
    queue = [(0, start, [])]
    visited = set()
    while queue:
        (cost, current, path) = heapq.heappop(queue)
        if current in visited: continue
        visited.add(current)
        path = path + [current]
        if current == goal: return path[1:]
        
        for neighbor, dist in DISTANCE_MAP.get(current, {}).items():
            if not is_at_war and provinces[neighbor].owner != side: continue
            heapq.heappush(queue, (cost + dist, neighbor, path))
    return None

def get_move_speed(unit, target_p, hour):
    speed = unit.speed
    if target_p.is_mega and (7 <= hour % 24 <= 9 or 17 <= hour % 24 <= 19): speed *= 0.5
    if target_p.terrain == "山岳" and unit.u_type != "山岳": speed *= 0.6
    return speed