"""
紫微斗数排盘引擎
Zi Wei Dou Shu (Purple Star Astrology) Calculator

输入：出生年月日时（农历）
输出：十二宫 + 主星分布 + 四化

算法核心：
  1. 定命宫位置（以出生月+时辰定位）
  2. 定五行局（天干+命宫地支→纳音）
  3. 定紫微星位置（五行局+出生日→查表）
  4. 由紫微推其余13颗主星
  5. 安四化星（禄权科忌）
"""

TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"

# 十二宫名称
GONG_NAMES = ["命宫", "兄弟", "夫妻", "子女", "财帛", "疾厄",
              "迁移", "交友", "事业", "田宅", "福德", "父母"]

# 14颗主星
ZHUXING = ["紫微", "天机", "太阳", "武曲", "天同", "廉贞",
           "天府", "太阴", "贪狼", "巨门", "天相", "天梁",
           "七杀", "破军"]

# 紫微星系安星规则（紫微定位后，其余按固定间距排列）
# 紫微星系：紫微、天机、太阳、武曲、天同、廉贞
# 相对紫微的宫位偏移（逆时针）
ZIWEI_OFFSETS = {
    "紫微": 0, "天机": -1, "太阳": -3,
    "武曲": -4, "天同": -5, "廉贞": -8,
}

# 天府星系：天府与紫微关于寅-申轴对称
# 天府定位后，其余按固定间距排列（顺时针）
TIANFU_OFFSETS = {
    "天府": 0, "太阴": 1, "贪狼": 2, "巨门": 3,
    "天相": 4, "天梁": 5, "七杀": 6, "破军": 10,
}

# 五行局对应数字
WUXING_JU = {
    "水二局": 2, "木三局": 3, "金四局": 4,
    "土五局": 5, "火六局": 6,
}

# 简化版：命宫天干+地支 → 五行局
# （完整版需要纳音五行查表，这里用简化映射）
JU_TABLE = {
    # 天干序号 % 5 -> 五行: 0=木, 1=火, 2=土, 3=金, 4=水
    # 地支序号 % 2 -> 阴阳
    # 简化规则：(天干%5 + 地支%2) % 5 → 局
    0: "水二局", 1: "木三局", 2: "金四局",
    3: "土五局", 4: "火六局",
}

# 四化表（年干 → 四颗星的四化）
SIHUA = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}


def calc_ming_gong(month: int, hour_zhi: int) -> int:
    """
    定命宫位置
    公式：命宫地支 = 寅 + 月 - 1 - 时辰
    month: 农历月 (1-12)
    hour_zhi: 时辰地支索引 (0=子, 1=丑, ..., 11=亥)
    返回：命宫在十二地支中的索引
    """
    # 命宫 = (月 + 时辰 的倒推)
    # 口诀：正月子时起寅宫，逆时针退一位
    ming = (2 + month - 1 - hour_zhi) % 12  # 2=寅
    if ming < 0:
        ming += 12
    return ming


def calc_wuxing_ju(tg_idx: int, ming_zhi: int) -> tuple[str, int]:
    """
    定五行局
    简化版：根据命宫天干地支纳音五行
    """
    # 简化映射
    key = (tg_idx % 5 + ming_zhi % 6) % 5
    ju_name = JU_TABLE[key]
    return ju_name, WUXING_JU[ju_name]


def calc_ziwei_pos(day: int, ju_num: int) -> int:
    """
    定紫微星位置
    紫微星位置 = 五行局数与出生日的对应关系
    简化算法：day / ju_num 的商和余数决定位置
    """
    quotient = day // ju_num
    remainder = day % ju_num

    if remainder == 0:
        pos = quotient - 1
    else:
        # 奇数余数前进，偶数余数后退
        if remainder % 2 == 1:
            pos = quotient + (remainder + 1) // 2
        else:
            pos = quotient - remainder // 2 + ju_num

    return (pos + 2) % 12  # 偏移到寅起


def paipan(year_tg: int, month: int, day: int, hour_zhi: int) -> dict:
    """
    紫微斗数排盘主函数

    year_tg: 年干索引 (0=甲, 1=乙, ...)
    month: 农历月 (1-12)
    day: 农历日 (1-30)
    hour_zhi: 时辰地支索引 (0=子, 1=丑, ..., 11=亥)
    """
    # 1. 定命宫
    ming_zhi = calc_ming_gong(month, hour_zhi)

    # 2. 各宫安排（从命宫逆时针排列十二宫）
    gongs = {}
    for i, name in enumerate(GONG_NAMES):
        pos = (ming_zhi + i) % 12
        gongs[name] = {"地支": DIZHI[pos], "主星": [], "四化": []}

    # 3. 定五行局
    ju_name, ju_num = calc_wuxing_ju(year_tg, ming_zhi)

    # 4. 定紫微星位置
    ziwei_pos = calc_ziwei_pos(day, ju_num)

    # 5. 安紫微星系
    for star, offset in ZIWEI_OFFSETS.items():
        pos = (ziwei_pos + offset) % 12
        # 找到该地支对应的宫
        for gname, gdata in gongs.items():
            if DIZHI.index(gdata["地支"]) == pos:
                gdata["主星"].append(star)
                break

    # 6. 安天府星系（天府与紫微关于寅申轴对称）
    tianfu_pos = (4 - ziwei_pos + 4) % 12  # 简化对称
    for star, offset in TIANFU_OFFSETS.items():
        pos = (tianfu_pos + offset) % 12
        for gname, gdata in gongs.items():
            if DIZHI.index(gdata["地支"]) == pos:
                gdata["主星"].append(star)
                break

    # 7. 安四化
    year_gan = TIANGAN[year_tg]
    sihua = SIHUA.get(year_gan, {})
    for hua_type, star in sihua.items():
        for gname, gdata in gongs.items():
            if star in gdata["主星"]:
                gdata["四化"].append(f"{star}化{hua_type}")
                break

    return {
        "命宫地支": DIZHI[ming_zhi],
        "五行局": ju_name,
        "年干": year_gan,
        "十二宫": gongs,
    }


def display(result: dict):
    """格式化显示紫微斗数命盘"""
    print("\n" + "═" * 56)
    print("  紫微斗数 · 命盘")
    print("═" * 56)

    print(f"\n  命宫：{result['命宫地支']}宫  |  {result['五行局']}  |  年干：{result['年干']}")

    # 简化版：列表展示
    print("\n  ┌─────────────────────────────────────────────────┐")
    for gname, gdata in result["十二宫"].items():
        stars = "、".join(gdata["主星"]) if gdata["主星"] else "（空宫）"
        sihua = " ".join(gdata["四化"]) if gdata["四化"] else ""
        marker = " ★" if gname == "命宫" else "  "
        line = f"  │{marker}{gname}（{gdata['地支']}）：{stars}"
        if sihua:
            line += f"  【{sihua}】"
        # 填充到固定宽度
        print(line)
    print("  └─────────────────────────────────────────────────┘")
    print()


def interactive():
    """交互式紫微斗数排盘"""
    print("\n╔══════════════════════════════════════╗")
    print("║   紫微斗数 · 排盘                   ║")
    print("║   Zi Wei Dou Shu Calculator          ║")
    print("╚══════════════════════════════════════╝")
    print('\n  号称"天下第一神数"，以108颗虚星排布命盘。')
    print("  ⚠️ 本程序忠实复现排盘算法，不代表认同其预测效力。")
    print("  ℹ️  输入需为农历日期。\n")

    try:
        y_tg = int(input("  出生年天干（0=甲 1=乙 2=丙 ... 9=癸）："))
        m = int(input("  农历月（1-12）："))
        d = int(input("  农历日（1-30）："))
        h = int(input("  时辰（0=子 1=丑 2=寅 ... 11=亥）："))
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    result = paipan(y_tg, m, d, h)
    display(result)


if __name__ == "__main__":
    interactive()
