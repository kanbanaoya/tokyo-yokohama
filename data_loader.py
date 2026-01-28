import csv

def load_provinces(file_path):
    p_data = {}
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            p_data[row['name']] = [
                row['terrain'], row['owner'], int(row['ic']),
                row['is_hub'] == '1', row['is_mega'] == '1'
            ]
    return p_data

def load_distances(file_path):
    dist_map = {}
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            f_city, t_city, d = row['from'], row['to'], int(row['distance'])
            if f_city not in dist_map: dist_map[f_city] = {}
            if t_city not in dist_map: dist_map[t_city] = {}
            dist_map[f_city][t_city] = d
            dist_map[t_city][f_city] = d
    return dist_map