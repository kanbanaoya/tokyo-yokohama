from models import Province, Unit
from engine import DISTANCE_MAP, find_path, get_move_speed

def draw_map(provinces, is_at_war, game_hour, total_ic, build_queue):
    mode = "【戦時】" if is_at_war else "【平和】"
    print(f"\n{'='*65}")
    print(f"  {game_hour//24}日目 {game_hour%24:02d}:00  |  状態: {mode}  |  総工業力: {total_ic} IC")
    
    # 生産状況の表示
    if build_queue:
        q = build_queue[0]
        prog_bar = "#" * int(q['progress'] / q['cost'] * 20)
        print(f"  [生産中] {q['type']} ({q['id']}): [{prog_bar:20}] {int(q['progress'])}/{q['cost']}")
    else:
        print("  [生産中] なし")
    print(f"{'='*65}")
    
    def get_p_info(name):
        p = provinces[name]
        owner_m = "T" if p.owner == "東京" else "K"
        u_count = len(p.units) if p.units else " "
        hub_m = "★" if p.is_hub else " "
        return f"[{owner_m}]{hub_m}{name}{u_count}"

    print(f"  {get_p_info('奥多摩')} -- {get_p_info('八王子')} -- {get_p_info('町田')} -- {get_p_info('新宿')}")
    print("                |            /          / ")
    print(f"  {get_p_info('箱根')}   -- {get_p_info('相模原')} -- {get_p_info('川崎')} -- {get_p_info('横浜')}")
    print("-" * 65)

def setup():
    p_data = {
        "新宿": ["巨大都市", "東京", 10, True, True], "町田": ["都市", "東京", 3, False, False],
        "八王子": ["平地", "東京", 5, True, False], "奥多摩": ["山岳", "東京", 1, False, False],
        "横浜": ["巨大都市", "神奈川", 8, True, True], "川崎": ["都市", "神奈川", 6, True, False],
        "相模原": ["平地", "神奈川", 4, False, False], "箱根": ["山岳", "神奈川", 1, False, False]
    }
    provinces = {n: Province(n, d[0], d[1], d[2], d[3], d[4]) for n, d in p_data.items()}
    units = {"K1": Unit("K1", "歩兵", "神奈川")}
    units["K1"].location = "横浜"; provinces["横浜"].units.append(units["K1"])
    return provinces, units

provinces, all_units = setup()
is_at_war = False
game_hour = 0
build_queue = [] # [{id, type, cost, progress}]

while True:
    total_ic = sum(p.ic for p in provinces.values() if p.owner == "神奈川")
    draw_map(provinces, is_at_war, game_hour, total_ic, build_queue)
    
    print("コマンド: move [ID] [目標], build [種別], war, wait [時], exit")
    cmd = input(">> ").split()
    
    if not cmd: continue
    if cmd[0] == "exit": break
    if cmd[0] == "war": is_at_war = True; print("！！！宣戦布告！！！"); continue
    if cmd[0] == "build":
        u_type = cmd[1]
        if u_type in Unit.SPECS:
            new_id = f"K{len(all_units) + len(build_queue) + 1}"
            build_queue.append({"id": new_id, "type": u_type, "cost": Unit.SPECS[u_type]["cost"], "progress": 0})
            print(f"--- {u_type} ({new_id}) の生産を開始しました ---")
        else:
            print("エラー: その部隊種別は存在しません(歩兵/戦車/山岳兵)")
        continue

    steps = int(cmd[1]) if cmd[0] == "wait" and len(cmd)>1 else (1 if cmd[0] != "move" else 0)
    if cmd[0] == "move" and len(cmd) >= 3:
        uid, goal = cmd[1], cmd[2]
        if uid in all_units:
            unit = all_units[uid]; path = find_path(unit.location, goal, unit.side, provinces, is_at_war)
            if path: unit.path = path; unit.destination = goal; print(f"ルート確定: {'->'.join(path)}")
            else: print("エラー: 到達不能です。")
        steps = 1

    for _ in range(steps):
        game_hour += 1
        # 生産処理
        if build_queue:
            build_queue[0]["progress"] += total_ic
            if build_queue[0]["progress"] >= build_queue[0]["cost"]:
                done = build_queue.pop(0)
                new_u = Unit(done["id"], done["type"], "神奈川")
                new_u.location = "横浜"; all_units[done["id"]] = new_u
                provinces["横浜"].units.append(new_u)
                print(f"!!! {new_u.u_type} ({new_u.uid}) が横浜に配備されました !!!")

        # 移動・戦闘処理
        for u in list(all_units.values()):
            if u.path:
                next_city = u.path[0]; target_p = provinces[next_city]; dist = DISTANCE_MAP[u.location][next_city]
                enemies = [e for e in target_p.units if e.side != u.side]
                if enemies and is_at_war:
                    enemy = enemies[0]; enemy.hp -= 15; u.hp -= 10
                    if enemy.hp <= 0:
                        print(f"** {enemy.uid} 撃破！ **")
                        target_p.units.remove(enemy); del all_units[enemy.uid]
                else:
                    speed = get_move_speed(u, target_p, game_hour)
                    u.progress += speed
                    if u.progress >= dist:
                        provinces[u.location].units.remove(u); u.location = next_city; target_p.units.append(u)
                        if is_at_war: target_p.owner = u.side
                        u.path.pop(0); u.progress = 0
                        print(f"!! {u.uid} が {u.location} に到着 !!")

        # 勝利判定
        if all(p.owner == "神奈川" for p in provinces.values() if p.initial_owner == "東京" and p.is_hub):
            print("\n★★★ 神奈川軍、勝利！ ★★★"); break
