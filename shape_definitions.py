import numpy as np
from itertools import combinations, permutations

# --- ベクトル・幾何学計算のためのヘルパー関数群 ---
def magnitude(v):
    return np.linalg.norm(v)

def normalize(v):
    norm = magnitude(v)
    return v / norm if norm != 0 else v

def angle_between(v1, v2):
    v1_u, v2_u = normalize(v1), normalize(v2)
    return np.degrees(np.arccos(np.clip(np.dot(v1_u, v2_u), -1.0, 1.0)))

def get_line_center(line):
    return (line['start'] + line['end']) / 2

# --- 各図形の「幾何学的な指紋」を定義する辞書 ---
SHAPE_DEFINITIONS = {
    # --- 01-群: 柱など ---
    "dedicated_pole": {"name": "専用柱 (01-01)", "entity_counts": {"CIRCLE": 2}, "anchor_type": "CIRCLE", "search_radius_ratio": 1.5, "check_function": "check_dedicated_pole"},
    "kanden_pole": {"name": "関電柱 (01-02)", "entity_counts": {"CIRCLE": 1, "LINE": 2}, "anchor_type": "CIRCLE", "search_radius_ratio": 1.5, "check_function": "check_kanden_pole"},
    "lighting_pole": {"name": "照明柱 (01-04)", "entity_counts": {"CIRCLE": 1, "LINE": 3, "ARC": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 1.1, "check_function": "check_lighting_pole"},
    "lighting_type3": {"name": "照明 (01-05)", "entity_counts": {"CIRCLE": 2, "LINE": 2}, "anchor_type": "CIRCLE", "search_radius_ratio": 2.0, "check_function": "check_lighting_type3"},
    "lighting_type2": {"name": "照明 (01-06)", "entity_counts": {"CIRCLE": 2, "LINE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 5.0, "check_function": "check_lighting_type2"},
    
    # --- 02-群: 車両用灯器 ---
    "traffic_light_h3": {"name": "車両灯器 横型3位式 (02-01)", "entity_counts": {"ARC": 3, "CIRCLE": 1, "LINE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 10.0, "check_function": "check_traffic_light_h3"},
    "traffic_light_h3_double": {"name": "車両灯器 両面横型3位式 (02-02)", "entity_counts": {"ARC": 6, "CIRCLE": 1, "LINE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 10.0, "check_function": "check_traffic_light_h3_double"},
    "light_box_only_h3": {"name": "灯箱のみ 横型3位式 (02-10)", "entity_counts": {"ARC": 3}, "anchor_type": "ARC", "search_radius_ratio": 3.0, "check_function": "check_light_box_only_h3"},
    "traffic_light_v3": {"name": "車両灯器 縦型3位式 (02-13)", "entity_counts": {"ARC": 3, "CIRCLE": 1, "LINE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 10.0, "check_function": "check_traffic_light_v3"},
    "advance_light": {"name": "予告灯用 (02-14)", "entity_counts": {"ARC": 2, "CIRCLE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 8.0, "check_function": "check_advance_light"},
    "arrow_light_straight": {"name": "矢印灯器(直進) (02-18)", "entity_counts": {"ARC": 4}, "anchor_type": "ARC", "search_radius_ratio": 3.0, "check_function": "check_arrow_light_straight"},
    
    # --- 03-群: 歩行者用灯器 ---
    "pedestrian_light_clasp": {"name": "2位式(抱込型)歩行者用灯器 (03-01)", "entity_counts": {"CIRCLE": 1, "LINE": 8}, "anchor_type": "CIRCLE", "search_radius_ratio": 4.0, "check_function": "check_pedestrian_light_clasp"},
    
    # --- 04-群: 設備 ---
    "controller": {"name": "制御機 (04-01)", "entity_counts": {"LINE": 5, "CIRCLE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 2.0, "check_function": "check_controller"},
    "accessory_device": {"name": "付加装置 (04-02)", "entity_counts": {"LINE": 5, "CIRCLE": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 2.0, "check_function": "check_accessory_device"},
    
    # --- 05-群: 感知器 ---
    "sensor_arm": {"name": "感知器アーム (05-02)", "entity_counts": {"LINE": 1, "CIRCLE": 1, "ARC": 1}, "anchor_type": "CIRCLE", "search_radius_ratio": 15.0, "check_function": "check_sensor_arm"},
    
    # --- 06-群: 形態 ---
    "handhole": {"name": "ハンドホール (06-01)", "entity_counts": {"LINE": 4}, "anchor_type": "LINE", "search_radius_ratio": 2.0, "check_function": "check_handhole"},
}

# --- 判定ロジックの共通部分 ---
def find_collinear_arcs(arcs, num, is_horizontal=True):
    """同一直線上に等間隔に並ぶ、同じ半径の円弧のグループを見つける"""
    if len(arcs) < num: return None
    radii = [a['radius'] for a in arcs if a['radius'] > 0]
    if not radii: return None
    base_r = np.median(radii)
    similar_arcs = [a for a in arcs if abs(a['radius'] - base_r) < base_r * 0.1]
    if len(similar_arcs) < num: return None
    
    sort_key = 0 if is_horizontal else 1 # 水平ならx, 垂直ならyでソート
    for group in combinations(similar_arcs, num):
        centers = sorted([arc['center'] for arc in group], key=lambda p: p[sort_key])
        vectors = [centers[i+1] - centers[i] for i in range(num - 1)]
        magnitudes = [magnitude(v) for v in vectors]
        if any(m < 1e-6 for m in magnitudes): continue
        
        # 等間隔かチェック
        dist_ratio_ok = all(0.9 < (magnitudes[i] / magnitudes[0]) < 1.1 for i in range(1, len(magnitudes)))
        if not dist_ratio_ok: continue

        # 同一直線上にあるかチェック
        angle_ok = all(angle_between(vectors[i], vectors[0]) < 5 or angle_between(vectors[i], vectors[0]) > 175 for i in range(1, len(vectors)))
        if not angle_ok: continue
        
        return group # 条件に合うグループが見つかればそれを返す
    return None

# --- 各図形の定義に対応するチェック関数 ---
def check_dedicated_pole(anchor, neighbors):
    other_circles = [e for e in neighbors if e['entity'] == 'CIRCLE']
    if len(other_circles) != 1: return False
    return magnitude(anchor['center'] - other_circles[0]['center']) < 0.1

def check_kanden_pole(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(lines) != 2: return False
    v_line = next((l for l in lines if abs((l['end']-l['start'])[0]) < 0.1 * magnitude(l['end']-l['start'])), None)
    h_line = next((l for l in lines if abs((l['end']-l['start'])[1]) < 0.1 * magnitude(l['end']-l['start'])), None)
    if not v_line or not h_line: return False
    dist1 = min(magnitude(v_line['start'] - h_line['start']), magnitude(v_line['start'] - h_line['end']))
    dist2 = min(magnitude(v_line['end'] - h_line['start']), magnitude(v_line['end'] - h_line['end']))
    return min(dist1, dist2) < (magnitude(h_line['end'] - h_line['start']) * 0.1)

def check_lighting_pole(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']; arcs = [e for e in neighbors if e['entity'] == 'ARC']
    if len(lines) != 3 or len(arcs) != 1: return False
    for comp in lines + arcs:
        c = comp.get('center', get_line_center(comp))
        if magnitude(c - anchor['center']) > anchor['radius']: return False
    return True

def check_lighting_type3(anchor, neighbors):
    other_circles = [e for e in neighbors if e['entity'] == 'CIRCLE']; lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(other_circles) != 1 or len(lines) != 2: return False
    return magnitude(anchor['center'] - other_circles[0]['center']) < 0.1

def check_lighting_type2(anchor, neighbors):
    other_circles = [e for e in neighbors if e['entity'] == 'CIRCLE']; lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(other_circles) != 1 or len(lines) != 1: return False
    c1, c2, l = anchor, other_circles[0], lines[0]
    err1 = magnitude(l['start']-c1['center'])<c1['radius']*0.1 and magnitude(l['end']-c2['center'])<c2['radius']*0.1
    err2 = magnitude(l['start']-c2['center'])<c2['radius']*0.1 and magnitude(l['end']-c1['center'])<c1['radius']*0.1
    return err1 or err2

def check_traffic_light_h3(anchor, neighbors):
    arcs = [e for e in neighbors if e['entity'] == 'ARC']
    return find_collinear_arcs(arcs, 3, is_horizontal=True) is not None

# ★★★★★★★★★★★★★★★★★★★★ 新しいチェック関数を追加 ★★★★★★★★★★★★★★★★★★★★
def check_traffic_light_h3_double(anchor, neighbors):
    """両面横型3位式: 3つずつの円弧のグループが2つある"""
    arcs = [e for e in neighbors if e['entity'] == 'ARC']
    if len(arcs) < 6: return False
    
    group1 = find_collinear_arcs(arcs, 3, is_horizontal=True)
    if group1 is None: return False
    
    remaining_arcs = [arc for arc in arcs if arc not in group1]
    group2 = find_collinear_arcs(remaining_arcs, 3, is_horizontal=True)
    
    return group2 is not None

def check_light_box_only_h3(anchor, neighbors):
    """灯箱のみ: アンカー含め、3つの円弧が同一直線上にある"""
    all_arcs = [anchor] + [e for e in neighbors if e['entity'] == 'ARC']
    return find_collinear_arcs(all_arcs, 3, is_horizontal=True) is not None

def check_traffic_light_v3(anchor, neighbors):
    """縦型3位式: 3つの円弧が垂直に並んでいる"""
    arcs = [e for e in neighbors if e['entity'] == 'ARC']
    return find_collinear_arcs(arcs, 3, is_horizontal=False) is not None

def check_advance_light(anchor, neighbors):
    """予告灯: 2つの円弧が水平に並んでいる"""
    arcs = [e for e in neighbors if e['entity'] == 'ARC']
    return find_collinear_arcs(arcs, 2, is_horizontal=True) is not None
    
def check_arrow_light_straight(anchor, neighbors):
    arcs = [e for e in neighbors if e['entity'] == 'ARC']
    if len(arcs) < 3: return False
    all_arcs = [anchor] + arcs
    all_arcs.sort(key=lambda a: a['radius'], reverse=True)
    hood_arcs, arrow_arc = all_arcs[:3], all_arcs[3]
    if len(hood_arcs) != 3: return False
    base_r = np.median([a['radius'] for a in hood_arcs])
    if not all(abs(a['radius'] - base_r) < base_r * 0.1 for a in hood_arcs): return False
    hood_centroid = np.mean([a['center'] for a in hood_arcs], axis=0)
    return magnitude(arrow_arc['center'] - hood_centroid) < base_r
    
def check_pedestrian_light_clasp(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(lines) != 8: return False
    h_lines = [l for l in lines if abs((l['end']-l['start'])[1])<abs((l['end']-l['start'])[0])*0.1]
    v_lines = [l for l in lines if abs((l['end']-l['start'])[0])<abs((l['end']-l['start'])[1])*0.1]
    return len(h_lines) >= 4 and len(v_lines) >= 4

def check_controller(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']
    return len(lines) == 5

def check_accessory_device(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(lines) != 5: return False
    line_lens = [magnitude(l['end']-l['start']) for l in lines]
    longest = max(line_lens)
    return abs(longest - (anchor['radius'] * 2)) < anchor['radius'] * 0.2

def check_sensor_arm(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']; arcs = [e for e in neighbors if e['entity'] == 'ARC']
    return len(lines) == 1 and len(arcs) == 1

def check_handhole(anchor, neighbors):
    lines = [e for e in neighbors if e['entity'] == 'LINE']
    if len(lines) != 3: return False
    all_lines = [anchor] + lines
    h_lines = [l for l in all_lines if abs((l['end']-l['start'])[1]) < abs((l['end']-l['start'])[0])*0.15]
    v_lines = [l for l in all_lines if abs((l['end']-l['start'])[0]) < abs((l['end']-l['start'])[1])*0.15]
    return len(h_lines) == 2 and len(v_lines) == 2
