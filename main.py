import engine
from models import Province, Unit
from data_loader import load_provinces, load_distances

# 資源管理 [食料, 金属, 石油, お金, 人的資源]
stockpiles = {
    "神奈川": {"food": 5000, "metal": 2000, "oil": 1000, "money": 10000, "manpower": 200000},
    "東京":   {"food": 5000, "metal": 2000, "oil": 1000, "money": 10000, "manpower": 300000}
}
# 毎分の収支を保持（高速化のため）
income_cache = {side: {k: 0.0 for k in ["food", "metal", "oil", "money", "manpower"]} for side in stockpiles}
UNIT_COUNTERS = {}
build_queues = {side: [] for side in stockpiles}
game_minutes = 0

def update_income_cache(side, provinces):
    """土地所有権が変わった時のみ呼び出し、1分あたりの収支を再計算する"""
    for k in ["food", "metal", "oil", "manpower"]:
        total_hourly = sum(getattr(p, k) for p in provinces.values() if p.owner == side)
        income_cache[side][k] = total_hourly / 60
    # 資金はICの10倍として計算
    income_cache[side]["money"] = sum(p.ic * 10 for p in provinces.values() if p.owner == side) / 60

def get_next_unit_info(side, u_type):
    if side not in UNIT_COUNTERS: UNIT_COUNTERS[side] = {k: 0 for k in Unit.SPECS.keys()}
    UNIT_COUNTERS[side][u_type] += 1
    return f"{side}-{u_type}-{UNIT_COUNTERS[side][u_type]}", UNIT_COUNTERS[side][u_type]
def draw_status(provinces, stocks, all_units, game_min, is_at_war):
    side = "神奈川"
    s, inc = stocks[side], income_cache[side]
    day, hr, mn = game_min // 1440, (game_min % 1440) // 60, game_min % 60
    print("\n" + "="*95)
    print(f" 【第{day}日 {hr:02d}:{mn:02d}】 状態: {'戦時' if is_at_war else '平和'}")
    print(f" 【資源】 食料:{int(s['food'])}(+{inc['food']*60:.0f}/h) | 金属:{int(s['metal'])}(+{inc['metal']*60:.0f}/h) | 石油:{int(s['oil'])}(+{inc['oil']*60:.0f}/h)")
    print(f" 【国力】 人的:{int(s['manpower'])}名(+{inc['manpower']*60:.0f}/h) | 資金:{int(s['money'])}(+{inc['money']*60:.0f}/h)")
    print("-" * 95)
    active_units = [u for u in all_units.values() if u.side == side and (u.path or u.wait_minutes > 0)]
    for u in active_units[:10]: # 表示制限
        st = f"待機({u.wait_minutes}m)" if u.wait_minutes > 0 else f"移動中({u.progress:.1f}km)"
        print(f"{u.uid:<15} | {u.location:<10} | HP:{u.hp:>3} | {st}")
    if len(active_units) > 10: print(f"...他 {len(active_units)-10} 部隊が展開中")
    print("="*95)

def setup():
    p_data = load_provinces('provinces.csv')
    provinces = {n: Province(n, *d) for n, d in p_data.items()}
    print("--- 座標から隣接ネットワークを構築中 (半径30) ---")
    engine.DISTANCE_MAP = engine.initialize_adjacencies(provinces, threshold=30)
    for side in stockpiles: update_income_cache(side, provinces)
    return provinces, {}
provinces, all_units = setup()
is_at_war = False

while True:
    draw_status(provinces, stockpiles, all_units, game_minutes, is_at_war)
    inp = input("move [ID] [目標] / strike [ID] [目標] / build [兵科] / war / wait [分] >> ").split()
    if not inp: continue
    cmd = inp[0]

    if cmd == "war": is_at_war = True; continue
    
    if cmd == "strike" and len(inp) >= 3:
        uid, target_name = inp[1], inp[2]
        if uid in all_units and target_name in provinces:
            u, tp = all_units[uid], provinces[target_name]
            dist = engine.get_distance(provinces[u.location], tp)
            if dist <= u.range * 10: # 座標スケール調整
                enemies = [e for e in tp.units if e.side != u.side]
                if enemies and is_at_war:
                    target = enemies[0]; target.hp -= u.attack / 2
                    print(f"!! {u.name} の攻撃着弾: {target.name} HP {target.hp} !!")
                    if target.hp <= 0: tp.units.remove(target); del all_units[target.uid]
            else: print("!! 射程外です !!")
        continue

    if cmd == "build" and len(inp) > 1:
        u_type, side = inp[1], "神奈川"
        if u_type in Unit.SPECS:
            cost = Unit.SPECS[u_type] # [4]金,[5]油,[7]資,[8]人的
            if all(stockpiles[side][k] >= cost[i] for i, k in zip([4,5,7,8], ["metal","oil","money","manpower"])):
                for i, k in zip([4,5,7,8], ["metal","oil","money","manpower"]): stockpiles[side][k] -= cost[i]
                uid, sn = get_next_unit_info(side, u_type)
                build_queues[side].append({"id": uid, "type": u_type, "progress": 0, "side": side, "sn": sn})
            else: print("!! リソース不足 !!")
        continue
    steps = int(inp[1]) if cmd == "wait" and len(inp) > 1 else (1 if cmd != "move" else 0)
    if cmd == "move" and len(inp) >= 3:
        uid, goal = inp[1], inp[2]
        if uid in all_units:
            u = all_units[uid]; path = engine.find_path(u.location, goal, u.side, provinces, is_at_war)
            if path: u.path, u.destination = path, goal
        steps = 1

    for _ in range(steps):
        game_minutes += 1
        for side in stockpiles:
            # 1. キャッシュを利用した超高速資源加算
            for k in stockpiles[side]: stockpiles[side][k] += income_cache[side][k]
            # 2. 生産進行
            if build_queues[side]:
                q = build_queues[side][0]; q["progress"] += 5
                if q["progress"] >= 100:
                    d = build_queues[side].pop(0)
                    new_u = Unit(d["id"], d["type"], d["side"], d["sn"])
                    hubs = [p for p in provinces.values() if p.owner == d["side"] and p.is_hub]
                    loc = hubs[0].name if hubs else "横浜"
                    new_u.location = loc; all_units[d["id"]] = new_u; provinces[loc].units.append(new_u)

        # 3. ユニット移動とペナルティ消化
        for u in list(all_units.values()):
            if u.wait_minutes > 0: u.wait_minutes -= 1; continue
            if u.path:
                nxt = u.path[0]; tp = provinces[nxt]; cur_p = provinces[u.location]
                if u.progress == 0: engine.check_transition_penalty(u, cur_p, tp)
                if u.wait_minutes > 0: continue
                
                u.progress += engine.get_move_speed_per_min(u, tp)
                if u.progress >= engine.DISTANCE_MAP[u.location][nxt]:
                    cur_p.units.remove(u); u.location = nxt; tp.units.append(u)
                    if is_at_war and tp.terrain != "海" and tp.owner != u.side:
                        old_owner = tp.owner; tp.owner = u.side
                        update_income_cache(u.side, provinces)
                        if old_owner in income_cache: update_income_cache(old_owner, provinces)
                    u.path.pop(0); u.progress = 0