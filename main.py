from models import Province, Unit
from engine import DISTANCE_MAP, find_path, get_move_speed

# --- 初期化 ---
def setup():
    p_data = {
        "新宿": ["巨大都市", "東京", 10, True, True], "町田": ["都市", "東京", 3, False, False],
        "八王子": ["平地", "東京", 5, True, False], "奥多摩": ["山岳", "東京", 1, False, False],
        "横浜": ["巨大都市", "神奈川", 8, True, True], "川崎": ["都市", "神奈川", 6, True, False],
        "相模原": ["平地", "神奈川", 4, False, False], "箱根": ["山岳", "神奈川", 1, False, False]
    }
    provinces = {n: Province(n, d[0], d[1], d[2], d[3], d[4]) for n, d in p_data.items()}
    units = {"K1": Unit("K1", "戦車", "神奈川")}
    units["K1"].location = "横浜"
    provinces["横浜"].units.append(units["K1"])
    return provinces, units

provinces, all_units = setup()
is_at_war = False
game_hour = 0

# --- メインループ ---
while True:
    print(f"\n--- {game_hour//24}日目 {game_hour%24}:00 ---")
    cmd = input("move [ID] [目的地] / war / wait [時] / exit >> ").split()
    
    if not cmd: continue
    if cmd[0] == "exit": break
    if cmd[0] == "war": is_at_war = True; print("！！！宣戦布告！！！"); continue

    steps = 1
    if cmd[0] == "wait": steps = int(cmd[1]) if len(cmd]>1 else 1
    elif cmd[0] == "move":
        uid, goal = cmd[1], cmd[2]
        if uid in all_units:
            unit = all_units[uid]
            path = find_path(unit.location, goal, unit.side, provinces, is_at_war)
            if path:
                unit.path = path
                unit.destination = goal
                print(f"ルート確定: {' -> '.join([unit.location] + path)}")
            else:
                print("到達不可能な場所、または平和時の敵地です。")

    # シミュレーション実行
    for _ in range(steps):
        game_hour += 1
        for u in list(all_units.values()):
            if u.path:
                next_city = u.path[0]
                target_p = provinces[next_city]
                dist = DISTANCE_MAP[u.location][next_city]
                
                # 敵がいるかチェック
                enemies = [e for e in target_p.units if e.side != u.side]
                if enemies and is_at_war:
                    # 戦闘（簡易版：V3.3準拠）
                    enemy = enemies[0]
                    enemy.hp -= 10; u.hp -= 5
                    if game_hour % 6 == 0: print(f"戦闘中: {u.uid} vs {enemy.uid}")
                    if enemy.hp <= 0: target_p.units.remove(enemy); del all_units[enemy.uid]
                else:
                    # 移動
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
