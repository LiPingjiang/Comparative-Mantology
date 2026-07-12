"""
阴阳道方违引擎
Onmyōdō Kata-tagae (方違え) Calculator

输入：日期 + 目的地方位
输出：方位神位置 + 是否犯禁 + 方违え建议

算法核心：
  - 方位神（天一神/太白神/金神等）按日期循环移动
  - 特定方位神所在方向为禁忌方向
  - 方违え（kata-tagae）：先往别处住一晚，改变出发方位以避禁
"""

DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 八方位
DIRECTIONS = {
    "北": 0, "东北": 1, "东": 2, "东南": 3,
    "南": 4, "西南": 5, "西": 6, "西北": 7,
}
DIR_NAMES = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]

# ─── 方位神 ───

# 天一神（Nakagami）：最重要的方位神
# 按六日一循环移动八方位
# 天一神在的方向为凶方
TENICHI_CYCLE = [
    "北", "东北", "东", "东南", "南", "西南",  # 6天一循环
]

# 太白神（金星之神）
# 按十日一循环
TAIHAKU_CYCLE = [
    "西", "北", "东", "南",   # 四方循环
]

# 金神（Konjin）：最凶的方位神
# 按年支决定方位（简化版）
KONJIN_BY_YEAR = {
    0: "南",     # 子年
    1: "东",     # 丑年
    2: "南",     # 寅年
    3: "西",     # 卯年
    4: "北",     # 辰年
    5: "东",     # 巳年
    6: "南",     # 午年
    7: "西",     # 未年
    8: "北",     # 申年
    9: "东",     # 酉年
    10: "南",    # 戌年
    11: "西",    # 亥年
}

# 六曜（ろくよう）：按日期机械计算
ROKUYO = ["先勝", "友引", "先負", "仏滅", "大安", "赤口"]
ROKUYO_MEANINGS = {
    "大安": ("大吉", "万事皆宜，诸事大吉"),
    "友引": ("半吉", "上午吉、正午凶、下午吉。忌葬礼（怕拉走友人）"),
    "先勝": ("上午吉", "先出手为胜，上午吉下午凶"),
    "先負": ("下午吉", "先出手不利，上午凶下午吉"),
    "赤口": ("凶", "仅正午前后一时吉，其余皆凶"),
    "仏滅": ("大凶", "万事皆凶之日"),
}


def calc_day_offset(year: int, month: int, day: int) -> int:
    """计算从参考日起的天数偏移"""
    from datetime import date
    ref = date(2000, 1, 1)
    target = date(year, month, day)
    return (target - ref).days


def get_tenichi(day_offset: int) -> str:
    """天一神当日方位"""
    return TENICHI_CYCLE[day_offset % len(TENICHI_CYCLE)]


def get_taihaku(day_offset: int) -> str:
    """太白神当日方位"""
    return TAIHAKU_CYCLE[day_offset % len(TAIHAKU_CYCLE)]


def get_konjin(year: int) -> str:
    """金神当年方位"""
    year_zhi = (year - 4) % 12
    return KONJIN_BY_YEAR.get(year_zhi, "南")


def get_rokuyo(month: int, day: int) -> str:
    """
    六曜计算
    公式：（旧历月 + 旧历日）% 6
    简化版使用新历近似
    """
    return ROKUYO[(month + day) % 6]


def analyze(year: int, month: int, day: int, direction: str) -> dict:
    """
    分析某日某方向是否犯禁
    """
    day_offset = calc_day_offset(year, month, day)

    tenichi = get_tenichi(day_offset)
    taihaku = get_taihaku(day_offset)
    konjin = get_konjin(year)
    rokuyo = get_rokuyo(month, day)

    # 判断禁忌
    taboos = []
    if direction == tenichi:
        taboos.append(("天一神", "此方位有天一神坐镇，大凶"))
    if direction == taihaku:
        taboos.append(("太白神", "此方位有太白神（金星），不宜出行"))
    if direction == konjin:
        taboos.append(("金神", "此方位为金神所在，最凶方位"))

    # 方违え建议
    katatagae = None
    if taboos:
        # 找一个安全方位作为中转
        unsafe = {tenichi, taihaku, konjin}
        safe_dirs = [d for d in DIR_NAMES if d not in unsafe]
        if safe_dirs:
            katatagae = safe_dirs[0]

    return {
        "日期": f"{year}年{month}月{day}日",
        "目标方位": direction,
        "天一神": tenichi,
        "太白神": taihaku,
        "金神": f"{konjin}（{DIZHI[(year-4)%12]}年）",
        "六曜": rokuyo,
        "六曜解": ROKUYO_MEANINGS.get(rokuyo, ("?", "?")),
        "禁忌": taboos,
        "方违え": katatagae,
    }


def display(result: dict):
    """格式化显示"""
    print("\n" + "═" * 56)
    print("  陰陽道 · 方違え判定")
    print("═" * 56)

    print(f"\n  日期：{result['日期']}")
    print(f"  目标方位：{result['目标方位']}\n")

    print("  ── 方位神 ──")
    print(f"    天一神（中神）：{result['天一神']}")
    print(f"    太白神（金星）：{result['太白神']}")
    print(f"    金神（最凶）：{result['金神']}")

    print(f"\n  ── 六曜 ──")
    rokuyo_ji, rokuyo_desc = result["六曜解"]
    print(f"    今日六曜：{result['六曜']}（{rokuyo_ji}）")
    print(f"    {rokuyo_desc}")

    print(f"\n  ── 判定 ──")
    if result["禁忌"]:
        print(f"  ⚠️  此方位犯禁！")
        for god, desc in result["禁忌"]:
            print(f"    🔴 {god}：{desc}")
        if result["方违え"]:
            print(f"\n  💡 方違え建议：")
            print(f"    先往 {result['方违え']} 方向住一晚，")
            print(f"    次日再从该处出发前往目的地，")
            print(f"    即可改变出发方位以避凶。")
    else:
        print(f"  🟢 此方位今日无禁忌，可安心出行。")

    print(f"\n  ────────────────────────────")
    print(f"  📊 陰陽道方位禁忌为平安朝贵族习俗，")
    print(f"     1870年明治维新后陰陽寮被废。")
    print()


def interactive():
    """交互式阴阳道"""
    print("\n╔══════════════════════════════════════╗")
    print("║   陰陽道 · 方違え                   ║")
    print("║   Onmyōdō Kata-tagae                ║")
    print("╚══════════════════════════════════════╝")
    print("\n  平安時代の方位禁忌判定。安倍晴明の陰陽寮。")
    print("  ⚠️ 本程序忠实复现推算规则，不代表认同其预测效力。\n")

    try:
        y = int(input("  年（如 2025）："))
        m = int(input("  月（1-12）："))
        d = int(input("  日（1-31）："))
        print(f"\n  方位：{', '.join(DIR_NAMES)}")
        direction = input("  目标方位：").strip()
        if direction not in DIR_NAMES:
            print("  无效方位，默认北。")
            direction = "北"
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    result = analyze(y, m, d, direction)
    display(result)


if __name__ == "__main__":
    interactive()
