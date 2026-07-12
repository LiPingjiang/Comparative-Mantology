"""
生肖相合引擎
Chinese Zodiac Compatibility Calculator

输入：两个生肖（或出生年）
输出：六合/六冲/三合/相刑/相害/相破判定

算法核心：十二地支之间的固定关系查表
"""

SHENGXIAO = ["鼠", "牛", "虎", "兔", "龙", "蛇", "马", "羊", "猴", "鸡", "狗", "猪"]
DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 六合（最佳搭配）
LIUHE = {
    frozenset({0, 1}): "子丑合土",   # 鼠-牛
    frozenset({2, 11}): "寅亥合木",  # 虎-猪
    frozenset({3, 10}): "卯戌合火",  # 兔-狗
    frozenset({4, 9}): "辰酉合金",   # 龙-鸡
    frozenset({5, 8}): "巳申合水",   # 蛇-猴
    frozenset({6, 7}): "午未合",     # 马-羊
}

# 六冲（最不利）
LIUCHONG = {
    frozenset({0, 6}): "子午冲",   # 鼠-马
    frozenset({1, 7}): "丑未冲",   # 牛-羊
    frozenset({2, 8}): "寅申冲",   # 虎-猴
    frozenset({3, 9}): "卯酉冲",   # 兔-鸡
    frozenset({4, 10}): "辰戌冲",  # 龙-狗
    frozenset({5, 11}): "巳亥冲",  # 蛇-猪
}

# 三合局
SANHE = [
    ({8, 0, 4}, "申子辰合水局"),   # 猴鼠龙
    ({2, 6, 10}, "寅午戌合火局"),  # 虎马狗
    ({5, 9, 1}, "巳酉丑合金局"),   # 蛇鸡牛
    ({11, 3, 7}, "亥卯未合木局"),  # 猪兔羊
]

# 相刑
XIANGXING = {
    frozenset({2, 5}): "寅刑巳（恃势之刑）",    # 虎-蛇
    frozenset({5, 8}): "巳刑申（恃势之刑）",    # 蛇-猴
    frozenset({8, 2}): "申刑寅（恃势之刑）",    # 猴-虎
    frozenset({1, 10}): "丑刑戌（无恩之刑）",   # 牛-狗
    frozenset({10, 7}): "戌刑未（无恩之刑）",   # 狗-羊
    frozenset({7, 1}): "未刑丑（无恩之刑）",    # 羊-牛
    frozenset({0, 3}): "子刑卯（无礼之刑）",    # 鼠-兔
    frozenset({3, 0}): "卯刑子（无礼之刑）",    # 兔-鼠
}

# 相害
XIANGHAI = {
    frozenset({0, 7}): "子未害",   # 鼠-羊
    frozenset({1, 6}): "丑午害",   # 牛-马
    frozenset({2, 5}): "寅巳害",   # 虎-蛇
    frozenset({3, 4}): "卯辰害",   # 兔-龙
    frozenset({8, 11}): "申亥害",  # 猴-猪
    frozenset({9, 10}): "酉戌害",  # 鸡-狗
}


def year_to_zodiac(year: int) -> int:
    """公历年份→生肖索引"""
    return (year - 4) % 12


def analyze(z1: int, z2: int) -> dict:
    """分析两个生肖的关系"""
    pair = frozenset({z1, z2})
    results = {
        "生肖1": SHENGXIAO[z1],
        "生肖2": SHENGXIAO[z2],
        "地支1": DIZHI[z1],
        "地支2": DIZHI[z2],
        "关系": [],
    }

    # 同属相
    if z1 == z2:
        results["关系"].append(("自刑/同类", "⚪", "同属相，互为镜像"))

    # 六合
    if pair in LIUHE:
        results["关系"].append(("六合", "🟢", LIUHE[pair]))

    # 六冲
    if pair in LIUCHONG:
        results["关系"].append(("六冲", "🔴", LIUCHONG[pair]))

    # 三合
    for group, desc in SANHE:
        if z1 in group and z2 in group:
            results["关系"].append(("三合", "🟢", desc))

    # 相刑
    if pair in XIANGXING:
        results["关系"].append(("相刑", "🟡", XIANGXING[pair]))

    # 相害
    if pair in XIANGHAI:
        results["关系"].append(("相害", "🟠", XIANGHAI[pair]))

    if not results["关系"]:
        results["关系"].append(("普通", "⚪", "无特殊关系"))

    return results


def display(result: dict):
    """格式化显示"""
    print("\n" + "═" * 50)
    print("  生肖相合 · 十二属相")
    print("═" * 50)
    print(f"\n  {result['生肖1']}（{result['地支1']}）  ↔  {result['生肖2']}（{result['地支2']}）\n")

    for rel_type, icon, desc in result["关系"]:
        print(f"  {icon} {rel_type}：{desc}")

    print("\n  ────────────────────────────")
    print("  📊 科学评价：属相决定性格/婚配的说法")
    print("     无任何同行评审研究支持。")
    print('     "龙年效应"等仅证明迷信对社会行为的影响力。')
    print()


def interactive():
    """交互式生肖相合"""
    print("\n╔══════════════════════════════════════╗")
    print("║   生肖相合 · 十二属相配对           ║")
    print("║   Chinese Zodiac Compatibility       ║")
    print("╚══════════════════════════════════════╝\n")

    print("  生肖列表：")
    for i, sx in enumerate(SHENGXIAO):
        print(f"    {i:2d}. {sx}（{DIZHI[i]}）", end="")
        if (i + 1) % 4 == 0:
            print()
    print()

    try:
        mode = input("  输入方式：1=选生肖编号  2=输入出生年：").strip()
        if mode == "2":
            y1 = int(input("  第一人出生年："))
            y2 = int(input("  第二人出生年："))
            z1 = year_to_zodiac(y1)
            z2 = year_to_zodiac(y2)
            print(f"  → {y1}年属{SHENGXIAO[z1]}，{y2}年属{SHENGXIAO[z2]}")
        else:
            z1 = int(input("  第一个生肖编号（0-11）："))
            z2 = int(input("  第二个生肖编号（0-11）："))
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    result = analyze(z1, z2)
    display(result)


if __name__ == "__main__":
    interactive()
