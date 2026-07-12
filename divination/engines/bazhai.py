"""
风水八宅法引擎
Feng Shui Ba Zhai (Eight Mansions) Calculator

输入：出生年 + 性别 → 命卦；宅向
输出：八方吉凶判定

算法核心：
  - 命卦 = (出生年各位数字之和归约) → 东四命/西四命
  - 宅向 → 东四宅/西四宅
  - 八方：伏位/生气/延年/天医（四吉）+ 绝命/五鬼/六煞/祸害（四凶）
"""

# ─── 八卦与方位 ───

GUA_INFO = {
    "坎": {"方位": "北", "group": "东四", "wuxing": "水", "number": 1},
    "坤": {"方位": "西南", "group": "西四", "wuxing": "土", "number": 2},
    "震": {"方位": "东", "group": "东四", "wuxing": "木", "number": 3},
    "巽": {"方位": "东南", "group": "东四", "wuxing": "木", "number": 4},
    "乾": {"方位": "西北", "group": "西四", "wuxing": "金", "number": 6},
    "兑": {"方位": "西", "group": "西四", "wuxing": "金", "number": 7},
    "艮": {"方位": "东北", "group": "西四", "wuxing": "土", "number": 8},
    "离": {"方位": "南", "group": "东四", "wuxing": "火", "number": 9},
}

# 八星（四吉四凶）
EIGHT_STARS = {
    "伏位": ("吉", "★☆☆☆", "安定、平稳，无大起伏"),
    "生气": ("大吉", "★★★★", "生机勃勃、贵人运、事业发展"),
    "延年": ("大吉", "★★★☆", "长寿、婚姻、人际和谐"),
    "天医": ("吉", "★★☆☆", "健康、疾病恢复、贵人"),
    "绝命": ("大凶", "☆☆☆☆", "最凶方位，诸事不利"),
    "五鬼": ("大凶", "☆☆☆★", "口舌是非、火灾、盗贼"),
    "六煞": ("凶", "☆☆★★", "桃花劫、感情纠纷"),
    "祸害": ("凶", "☆★★★", "小人、口角、慢性病"),
}

# 命卦与八方吉凶对应表
# key=命卦, value={方位卦: 星名}
BAZHAI_TABLE = {
    "坎": {"坎": "伏位", "巽": "生气", "震": "延年", "离": "天医",
           "坤": "绝命", "兑": "五鬼", "乾": "六煞", "艮": "祸害"},
    "离": {"离": "伏位", "震": "生气", "巽": "延年", "坎": "天医",
           "乾": "绝命", "艮": "五鬼", "坤": "六煞", "兑": "祸害"},
    "震": {"震": "伏位", "离": "生气", "坎": "延年", "巽": "天医",
           "兑": "绝命", "坤": "五鬼", "艮": "六煞", "乾": "祸害"},
    "巽": {"巽": "伏位", "坎": "生气", "离": "延年", "震": "天医",
           "艮": "绝命", "乾": "五鬼", "兑": "六煞", "坤": "祸害"},
    "乾": {"乾": "伏位", "艮": "生气", "坤": "延年", "兑": "天医",
           "离": "绝命", "坎": "五鬼", "巽": "六煞", "震": "祸害"},
    "坤": {"坤": "伏位", "兑": "生气", "乾": "延年", "艮": "天医",
           "震": "绝命", "巽": "五鬼", "坎": "六煞", "离": "祸害"},
    "兑": {"兑": "伏位", "坤": "生气", "艮": "延年", "乾": "天医",
           "巽": "绝命", "震": "五鬼", "离": "六煞", "坎": "祸害"},
    "艮": {"艮": "伏位", "乾": "生气", "兑": "延年", "坤": "天医",
           "坎": "绝命", "离": "五鬼", "震": "六煞", "巽": "祸害"},
}


def calc_ming_gua(year: int, gender: str) -> str:
    """
    计算命卦
    男命：(100 - 出生年后两位) / 9 取余，余数对应卦
    女命：(出生年后两位 - 4) / 9 取余，余数对应卦
    余数5：男归坤，女归艮
    2000年后公式调整
    """
    last_two = year % 100

    if year < 2000:
        if gender == "男":
            remainder = (100 - last_two) % 9
        else:
            remainder = (last_two - 4) % 9
    else:
        if gender == "男":
            remainder = (100 - last_two - 1) % 9  # 2000后男命减1
        else:
            remainder = (last_two - 4 + 1) % 9    # 2000后女命加1

    if remainder == 0:
        remainder = 9

    # 数字→卦名映射
    num_to_gua = {1: "坎", 2: "坤", 3: "震", 4: "巽",
                  5: "坤" if gender == "男" else "艮",  # 5寄宫
                  6: "乾", 7: "兑", 8: "艮", 9: "离"}

    return num_to_gua.get(remainder, "坎")


def analyze(ming_gua: str) -> dict:
    """分析八方吉凶"""
    gua_group = GUA_INFO[ming_gua]["group"]
    directions = BAZHAI_TABLE[ming_gua]

    result = {"命卦": ming_gua, "所属": gua_group, "方位分析": []}

    for gua_name in ["坎", "坤", "震", "巽", "乾", "兑", "艮", "离"]:
        star = directions[gua_name]
        ji_xiong, rating, desc = EIGHT_STARS[star]
        info = GUA_INFO[gua_name]
        result["方位分析"].append({
            "方位": info["方位"],
            "卦": gua_name,
            "八星": star,
            "吉凶": ji_xiong,
            "评级": rating,
            "说明": desc,
        })

    return result


def display(result: dict):
    """格式化显示"""
    print("\n" + "═" * 56)
    print("  风水八宅法 · 方位吉凶")
    print("═" * 56)

    gua_info = GUA_INFO[result["命卦"]]
    print(f"\n  命卦：{result['命卦']}（{gua_info['wuxing']}）")
    print(f"  所属：{result['所属']}命")
    print(f"  本位：{gua_info['方位']}\n")

    print("  ┌────────┬──────┬──────┬──────┬──────────────────┐")
    print("  │ 方位   │ 卦   │ 八星 │ 吉凶 │ 说明             │")
    print("  ├────────┼──────┼──────┼──────┼──────────────────┤")
    for item in result["方位分析"]:
        icon = "🟢" if "吉" in item["吉凶"] and "凶" not in item["吉凶"] else "🔴"
        print(f"  │ {item['方位']:6s}│ {item['卦']:4s}│ {item['八星']:4s}│ {icon}{item['吉凶']:3s}│ {item['说明'][:16]}│")
    print("  └────────┴──────┴──────┴──────┴──────────────────┘")

    # 建议
    ji_fang = [i["方位"] for i in result["方位分析"] if "吉" in i["吉凶"] and "凶" not in i["吉凶"]]
    print(f"\n  四吉方：{'、'.join(ji_fang)}")

    print("\n  ────────────────────────────")
    print("  📊 八宅法为理气派风水，其方位吉凶判断")
    print("     无经过同行评审的科学验证。")
    print()


def interactive():
    """交互式风水八宅法"""
    print("\n╔══════════════════════════════════════╗")
    print("║   风水八宅法 · 方位吉凶             ║")
    print("║   Ba Zhai Feng Shui                  ║")
    print("╚══════════════════════════════════════╝")
    print("\n  理气派风水的基础方法。")
    print("  ⚠️ 本程序忠实复现推算规则，不代表认同其预测效力。\n")

    try:
        year = int(input("  出生年（如 1990）："))
        gender = input("  性别（男/女）：").strip()
        if gender not in ("男", "女"):
            gender = "男"
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    ming_gua = calc_ming_gua(year, gender)
    result = analyze(ming_gua)
    display(result)


if __name__ == "__main__":
    interactive()
