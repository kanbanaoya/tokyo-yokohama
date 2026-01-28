import engine
from models import Province, Unit
from data_loader import load_provinces, load_distances

# 管理データ
UNIT_COUNTERS = {}
build_queues = {"神奈川": [], "東京": []}

def get_next_unit_info(side, u_type):
    if side not in UNIT_COUNTERS: UNIT_COUNTERS[side] = {"普通科": 0, "機甲": 0, "山岳": 0}
    UNIT_COUNTERS[side][u_type] += 1
    sn = UNIT_COUNTERS[side][u_type]
    return f"{side}-{u_type}-{sn}", sn

def draw_map(provinces, is_at_war, game_hour, all_units, build_queues):
    k_ic = sum(p.ic for p in provinces.values() if p.owner == "神奈川")
    print(f"\n{'='*85}\n  {game_hour//24}日目 {game_hour%24:02d}:00 | 神奈川 IC: {k_ic} | 状態: {'戦時' if is_at_war else '平和'}")
    if build_queues["神奈川"]:
        q = build_queues["神奈川"][0]
        prog = int(q['progress'] / q['cost'] * 20)
        print(f"  [生産] {q['name']}: [{'#'*prog:20}] {int(q['progress'])}/{q['cost']}")
    print(f"{'='*85}\n  部隊リスト:")
    for u in [u for u in all_units.values() if u.side == "神奈川"]:
        status = f"{u.path[0]}へ移動中" if u.path else "待機中"
        print(f"  - {u.name:<25} | HP: {u.hp:>3}/100 | 位置: {u.location:<10} | {status}")
    print("-" * 85)

def setup():
    p_data = load_provinces('provinces.csv')
    engine.DISTANCE_MAP = load_distances('distances.csv')
    provinces = {n: Province(n, *d) for n, d in p_data.items()}
    units = {}
    initial_deploy = [["神奈川", "機甲", "横浜"], ["東京", "普通科", "新宿"]]
    for side, u_type, loc in initial_deploy:
        uid, sn = get_next_unit_info(side, u_type)
        new_u = Unit(uid, u_type, side, sn)
        new_u.location = loc
        units[uid] = new_u
        provinces[loc].units.append(new_u)
    return provinces, units

provinces, all_units = setup()
is_at_war, game_hour = False, 0

while True:
    draw_map(provinces, is_at_war, game_hour, all_units, build_queues)
    cmd = input("move [ID] [目標] / build [種別] / war / wait [時] / exit >> ").split()
    if not cmd: continue
    if cmd[0] == "exit": break
    if cmd[0] == "war": is_at_war = True; continue
    if cmd[0] == "build" and len(cmd) > 1:
        u_type = cmd[1]
        if u_type in Unit.SPECS:
            uid, sn = get_next_unit_info("神奈川", u_type)
            name = f"神奈川 {u_type} 第{sn}師団"
            build_queues["神奈川"].append({"id": uid, "type": u_type, "cost": Unit.SPECS[u_type]["cost"], "progress": 0, "name": name})
        continue

    steps = int(cmd[1]) if cmd[0] == "wait" and len(cmd) > 1 else (1 if cmd[0] != "move" else 0)
    if cmd[0] == "move" and len(cmd) >= 3:
        uid, goal = cmd[1], cmd[2]
        if uid in all_units:
            u = all_units[uid]
            path = engine.find_path(u.location, goal, u.side, provinces, is_at_war)
            if path: u.path, u.destination = path, goal
        steps = 1

    for _ in range(steps):
        game_hour += 1
        # 生産進行
        for side in ["神奈川", "東京"]:
            ic = sum(p.ic for p in provinces.values() if p.owner == side)
            if build_queues[side]:
                q = build_queues[side][0]
                q["progress"] += ic
                if q["progress"] >= q["cost"]:
                    done = build_queues[side].pop(0)
                    new_u = Unit(done["id"], done["type"], side, int(done["id"].split("-")[-1]))
                    hubs = [p for p in provinces.values() if p.owner == side and p.is_hub]
                    if hubs:
                        loc = hubs[0].name
                        new_u.location = loc; all_units[done["id"]] = new_u; provinces[loc].units.append(new_u)
        
        # 移動・戦闘
        for u in list(all_units.values()):
            if u.path:
                nxt = u.path[0]; target_p = provinces[nxt]; dist = engine.DISTANCE_MAP[u.location][nxt]
                enemies = [e for e in target_p.units if e.side != u.side]
                if enemies and is_at_war:
                    enemy = enemies[0]; enemy.hp -= 15; u.hp -= 10
                    if enemy.hp <= 0: target_p.units.remove(enemy); del all_units[enemy.uid]
                else:
                    u.progress += engine.get_move_speed(u, target_p, game_hour)
                    if u.progress >= dist:
                        provinces[u.location].units.remove(u); u.location = nxt; target_p.units.append(u)
                        if is_at_war: target_p.owner = u.side
                        u.path.pop(0); u.progress = 0

        # 勝利判定
        t_hubs = [p for p in provinces.values() if p.initial_owner == "東京" and p.is_hub]
        if all(p.owner == "神奈川" for p in t_hubs):
            print("\n★★★ 神奈川軍、勝利！ ★★★"); break