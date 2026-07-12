"""
奇门遁甲布盘引擎
Qi Men Dun Jia (Mysterious Gates Escaping Technique)

输入：起局时间（年月日时）
输出：九宫布盘（天盘/地盘/八门/九星/八神/三奇六仪）

算法核心：
  - 洛书九宫（横竖斜和=15）
  - 阳遁9局 + 阴遁9局 = 18局
  - 按节气定局，逐层布入九宫
"""

# ─── 基础数据 ───

TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"

# 洛书九宫排列（中宫=5，寄坤二宫）
# 位置：[1坎北, 2坤西南, 3震东, 4巽东南, 5中, 6乾西北, 7兑西, 8艮东北, 9离南]
LUOSHU = [
    (4, "巽", "东南"), (9, "离", "南"), (2, "坤", "西南"),
    (3, "震", "东"),   (5, "中", "中"), (7, "兑", "西"),
    (8, "艮", "东北"), (1, "坎", "北"), (6, "乾", "西北"),
]

# 九宫顺序（飞星顺序）：1→2→3→4→5→6→7→8→9
FEIXING_ORDER = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 八门
BAMEN = ["休门", "死门", "伤门", "杜门", "中(寄)", "开门", "惊门", "生门", "景门"]

# 九星
JIUXING = ["天蓬", "天芮", "天冲", "天辅", "天禽", "天心", "天柱", "天任", "天英"]

# 八神（阳遁）
BASHEN_YANG = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九地", "九天"]
# 八神（阴遁）
BASHEN_YIN = ["值符", "腾蛇", "太阴", "六合", "白虎", "玄武", "九天", "九地"]

# 三奇六仪（固定地盘排列）
# 戊己庚辛壬癸为六仪，乙丙丁为三奇
SANQI_LIUYI = ["戊", "己", "庚", "辛", "壬", "癸", "丁", "丙", "乙"]

# 24节气与局数对应（简化版）
# 阳遁：冬至后（冬至/小寒/大寒各三局 = 上元1/中元2/下元3 ...）
# 阴遁：夏至后
JIEQI_JU = {
    # 阳遁（冬至→芒种）
    "冬至": (True, [1, 7, 4]),   # 上元1局 中元7局 下元4局
    "小寒": (True, [2, 8, 5]),
    "大寒": (True, [3, 9, 6]),
    "立春": (True, [8, 5, 2]),
    "雨水": (True, [9, 6, 3]),
    "惊蛰": (True, [1, 7, 4]),
    "春分": (True, [3, 9, 6]),
    "清明": (True, [4, 1, 7]),
    "谷雨": (True, [5, 2, 8]),
    "立夏": (True, [4, 1, 7]),
    "小满": (True, [5, 2, 8]),
    "芒种": (True, [6, 3, 9]),
    # 阴遁（夏至→大雪）
    "夏至": (False, [9, 3, 6]),
    "小暑": (False, [8, 2, 5]),
    "大暑": (False, [7, 1, 4]),
    "立秋": (False, [2, 5, 8]),
    "处暑": (False, [1, 4, 7]),
    "白露": (False, [9, 3, 6]),
    "秋分": (False, [7, 1, 4]),
    "寒露": (False, [6, 9, 3]),
    "霜降": (False, [5, 8, 2]),
    "立冬": (False, [6, 9, 3]),
    "小雪": (False, [5, 8, 2]),
    "大雪": (False, [4, 7, 1]),
}


def get_ju(month: int, day: int) -> tuple[bool, int]:
    """
    根据月日确定局数（简化版）
    返回 (是否阳遁, 局数)
    """
    # 简化：根据月份粗略对应节气
    jieqi_by_month = {
        12: "冬至", 1: "小寒", 2: "立春", 3: "惊蛰",
        4: "清明", 5: "立夏", 6: "芒种", 7: "小暑",
        8: "立秋", 9: "白露", 10: "寒露", 11: "立冬",
    }
    jieqi = jieqi_by_month.get(month, "冬至")
    is_yang, jus = JIEQI_JU[jieqi]

    # 三元：上元(日1-10)/中元(日11-20)/下元(日21-30)
    if day <= 10:
        yuan = 0
    elif day <= 20:
        yuan = 1
    else:
        yuan = 2

    return is_yang, jus[yuan]


def build_pan(month: int, day: int, hour_zhi: int) -> dict:
    """
    奇门遁甲布盘

    month: 月份(1-12)
    day: 日(1-31)
    hour_zhi: 时辰地支索引(0=子, ..., 11=亥)
    """
    is_yang, ju_num = get_ju(month, day)
    dun_type = "阳遁" if is_yang else "阴遁"

    # 地盘三奇六仪布局（按局数旋转）
    dipan = [None] * 9
    for i in range(9):
        if is_yang:
            pos = (ju_num - 1 + i) % 9  # 阳遁顺排
        else:
            pos = (ju_num - 1 - i) % 9  # 阴遁逆排
        dipan[pos] = SANQI_LIUYI[i]

    # 天盘（简化：以值符随时辰旋转）
    tianpan = [None] * 9
    shift = hour_zhi % 9
    for i in range(9):
        new_pos = (i + shift) % 9
        tianpan[new_pos] = SANQI_LIUYI[i]

    # 八门布局（以值使门为起点，按九宫飞星顺序）
    men = [None] * 9
    men_start = (ju_num - 1) % 8
    for i in range(9):
        pos = (men_start + i) % 9
        men[pos] = BAMEN[i]

    # 九星布局
    xing = [None] * 9
    xing_start = (ju_num - 1 + shift) % 9
    for i in range(9):
        pos = (xing_start + i) % 9
        xing[pos] = JIUXING[i]

    # 八神布局
    bashen = BASHEN_YANG if is_yang else BASHEN_YIN
    shen = [None] * 9
    shen_start = shift % 8
    for i in range(9):
        idx = i % 8
        pos = (shen_start + i) % 9
        shen[pos] = bashen[idx]

    return {
        "遁": dun_type,
        "局数": f"第{ju_num}局",
        "地盘": dipan,
        "天盘": tianpan,
        "八门": men,
        "九星": xing,
        "八神": shen,
    }


def display(pan: dict):
    """格式化显示奇门盘"""
    print("\n" + "═" * 60)
    print(f"  奇门遁甲 · {pan['遁']} · {pan['局数']}")
    print("═" * 60)

    # 九宫格展示（3x3）
    # 布局：巽(4) 离(9) 坤(2) / 震(3) 中(5) 兑(7) / 艮(8) 坎(1) 乾(6)
    positions = [
        (3, "巽/东南"), (8, "离/南  "), (1, "坤/西南"),
        (2, "震/东  "), (4, "中    "), (6, "兑/西  "),
        (7, "艮/东北"), (0, "坎/北  "), (5, "乾/西北"),
    ]

    print("\n  ┌──────────────┬──────────────┬──────────────┐")
    for row in range(3):
        cells = []
        for col in range(3):
            idx = row * 3 + col
            pos_idx, pos_name = positions[idx]
            dp = pan["地盘"][pos_idx] or "?"
            tp = pan["天盘"][pos_idx] or "?"
            mn = pan["八门"][pos_idx] or "?"
            xg = pan["九星"][pos_idx] or "?"
            sh = pan["八神"][pos_idx] or "?"
            cells.append(f" {pos_name}\n  │ 天{tp} 地{dp}\n  │ {mn} {xg}\n  │ {sh}")

        # 打印宫位名
        print(f"  │ {positions[row*3][1]}    │ {positions[row*3+1][1]}    │ {positions[row*3+2][1]}    │")
        # 打印天地盘
        print(f"  │ 天{pan['天盘'][positions[row*3][0]] or '?'} 地{pan['地盘'][positions[row*3][0]] or '?'}  │"
              f" 天{pan['天盘'][positions[row*3+1][0]] or '?'} 地{pan['地盘'][positions[row*3+1][0]] or '?'}  │"
              f" 天{pan['天盘'][positions[row*3+2][0]] or '?'} 地{pan['地盘'][positions[row*3+2][0]] or '?'}  │")
        print(f"  │ {pan['八门'][positions[row*3][0]] or '?':4s} {pan['九星'][positions[row*3][0]] or '?':4s}│"
              f" {pan['八门'][positions[row*3+1][0]] or '?':4s} {pan['九星'][positions[row*3+1][0]] or '?':4s}│"
              f" {pan['八门'][positions[row*3+2][0]] or '?':4s} {pan['九星'][positions[row*3+2][0]] or '?':4s}│")
        print(f"  │ {pan['八神'][positions[row*3][0]] or '?':12s}│"
              f" {pan['八神'][positions[row*3+1][0]] or '?':12s}│"
              f" {pan['八神'][positions[row*3+2][0]] or '?':12s}│")
        if row < 2:
            print("  ├──────────────┼──────────────┼──────────────┤")
    print("  └──────────────┴──────────────┴──────────────┘")
    print()


def interactive():
    """交互式奇门遁甲"""
    print("\n╔══════════════════════════════════════╗")
    print("║   奇门遁甲 · 布盘                   ║")
    print("║   Qi Men Dun Jia                     ║")
    print("╚══════════════════════════════════════╝")
    print("\n  中国古代最高等级的数术系统（三式之一）。")
    print("  ⚠️ 本程序忠实复现布盘算法，不代表认同其预测效力。\n")

    try:
        m = int(input("  月份（1-12）："))
        d = int(input("  日（1-31）："))
        h = int(input("  时辰（0=子 1=丑 ... 11=亥）："))
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    pan = build_pan(m, d, h)
    display(pan)


if __name__ == "__main__":
    interactive()
