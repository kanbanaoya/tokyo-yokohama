import csv

def load_provinces(file_path):
    """
    Excelで作成した11列のプロビンスデータを読み込みます。
    形式: name, terrain, owner, ic, food, metal, oil, manpower, is_hub, x, y
    """
    data = {}
    # utf-8-sig を使うことで、Excel特有のBOM（文字化けの原因）を自動で除去します
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        header = next(reader)  # 1行目のヘッダーをスキップ
        
        for row in reader:
            if not row or len(row) < 11:
                continue
            
            name = row[0]
            # 各列を適切な型に変換して格納
            try:
                attr = (
                    row[1],           # terrain (str)
                    row[2],           # owner (str)
                    float(row[3]),    # ic (float)
                    float(row[4]),    # food (float)
                    float(row[5]),    # metal (float)
                    float(row[6]),    # oil (float)
                    float(row[7]),    # manpower (float)
                    int(row[8]) == 1, # is_hub (bool)
                    int(row[9]),      # x (int)
                    int(row[10])      # y (int)
                )
                data[name] = attr
            except ValueError as e:
                print(f"警告: {name} のデータ形式が不正です。スキップします。({e})")
                
    return data

def load_distances(file_path):
    """
    【補足】現在は座標からの自動接続がメインですが、
    アクアラインのような「距離は遠いが繋げたい特殊な道」を読み込む際に使用します。
    """
    manual_edges = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                if len(row) >= 2:
                    manual_edges.append((row[0], row[1]))
    except FileNotFoundError:
        return []
    return manual_edges