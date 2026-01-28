from models import Province, Unit
from engine import DISTANCE_MAP, find_path, get_move_speed

# --- マップ描画関数 ---
def draw_map(provinces, is_at_war, game_hour):
    mode = "【戦時】" if is_at_war else "【平和】"
    print(f"\n{'='*65}")
    print(f"  {game_hour//24}日目 {game_hour%24:02d}:00  |  状態: {mode}  (T:東京 / K:神奈川)")
    print(f"{'='*65}")
    
    # マップのレイアウト
    # 奥多摩 -- 八王子 -- 町田 -- 新宿
    #              |        /      /
    # 箱根   -- 相模原 -- 川崎 -- 横浜
    
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

# --- 初期化 ---
def setup():
    p_data = {
        "新宿": ["巨大都市", "東京", 10, True, True], "町田": ["都市", "東京", 3, False, False],
        "八王子": ["平地", "東京", 5, True, False], "奥多摩": ["山岳", "東京", 1, False, False],
        "横浜": ["巨大都市", "神奈川", 8, True, True], "川崎": ["都市", "神奈川", 6, True, False],
        "相模原": ["平地", "神奈川", 4, False, False], "箱根": ["山岳", "神奈川", 1, False, False]
    }
    provinces = {n: Province(n, d[0], d[1], d[2], d[3], d[4]) for n, d in p_data.items()}
    units = {
        "K1": Unit("K1", "戦車", "神奈川"),
        "T1": Unit("T1", "歩兵", "東京")
    }
    units["K1"].location = "横浜"; provinces["横浜"].units.append(units["K1"])
    units["T1"].location = "新宿"; provinces["新宿"].units.append(units["T1"])
    return provinces, units

provinces, all_units = setup()
is_at_war = False
game_hour = 0

# --- メインループ ---
while True:
    draw_map(provinces, is_at_war, game_hour)
    print("コマンド: move [ID] [目標], war, wait [時], exit")
    user_input = input(">> ").split()
    
    if not user_input: continue
    cmd = user_input[0]
    if cmd == "exit": break
    if cmd == "war": is_at_war = True; print("！！！宣戦布告！！！"); continue

    steps = 1
    if cmd == "wait":
        steps = int(user_input[1]) if len(user_input) > 1 else 1
    elif cmd == "move" and len(user_input) >= 3:
        uid, goal = user_input[1], user_input[2]
        if uid in all_units:
            unit = all_units[uid]
            path = find_path(unit.location, goal, unit.side, provinces, is_at_war)
            if path:
                unit.path = path
                unit.destination = goal
                print(f"--- {unit.uid}、{goal}へ移動開始 (経路: {'->'.join(path)}) ---")
            else:
                print("エラー: 到達不可能な場所、または平和時の敵地です。")

    # シミュレーション実行
    for _ in range(steps):
        game_hour += 1
        for u in list(all_units.values()):
            if u.path:
                next_city = u.path[0]
                target_p = provinces[next_city]
                dist = DISTANCE_MAP[u.location][next_city]
                
                enemies = [e for e in target_p.units if e.side != u.side]
                if enemies and is_at_war:
                    enemy = enemies[0]
                    enemy.hp -= 15; u.hp -= 10
                    if game_hour % 3 == 0: print(f"【戦闘】{u.uid}(HP:{u.hp}) vs {enemy.uid}(HP:{enemy.hp})")
                    if enemy.hp <= 0:
                        print(f"** {enemy.uid} 撃破！ **")
                        target_p.units.remove(enemy); del all_units[enemy.uid]
                else:
                    speed = get_move_speed(u, target_p, game_hour)
                    u.progress += speed
                    if u.progress >= dist:
                        provinces[u.location].units.remove(u)
                        u.location = next_city
                        target_p.units.append(u)
                        if is_at_war: target_p.owner = u.side
                        u.path.pop(0)
                        u.progress = 0
                        print(f"!! {u.uid} が {u.location} に到着 !!")

        # 勝利判定
        tokyo_hubs = [p for p in provinces.values() if p.initial_owner == "東京" and p.is_hub]
        if
