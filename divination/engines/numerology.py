"""
数秘术引擎
Numerology Calculator (Pythagorean System)

输入：出生日期 + 姓名（拉丁字母）
输出：生命数/命运数/心愿数/人格数

算法核心：字母→数字映射 + 数字根归约（保留大师数11/22/33）
"""

# 毕达哥拉斯字母-数字映射
LETTER_MAP = {
    'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7, 'H': 8, 'I': 9,
    'J': 1, 'K': 2, 'L': 3, 'M': 4, 'N': 5, 'O': 6, 'P': 7, 'Q': 8, 'R': 9,
    'S': 1, 'T': 2, 'U': 3, 'V': 4, 'W': 5, 'X': 6, 'Y': 7, 'Z': 8,
}

VOWELS = set('AEIOU')
MASTER_NUMBERS = {11, 22, 33}

# 数字含义
MEANINGS = {
    1: "领导者 · 独立 · 开创 · 自信",
    2: "合作者 · 外交 · 敏感 · 平衡",
    3: "表达者 · 创造 · 乐观 · 社交",
    4: "建设者 · 稳定 · 纪律 · 实际",
    5: "自由者 · 变化 · 冒险 · 多才",
    6: "照顾者 · 责任 · 和谐 · 家庭",
    7: "探索者 · 分析 · 内省 · 智慧",
    8: "成就者 · 权力 · 物质 · 野心",
    9: "人道者 · 慈悲 · 理想 · 完成",
    11: "【大师数】灵感 · 直觉 · 启示 · 敏感",
    22: "【大师数】大建筑师 · 实现梦想 · 宏大视野",
    33: "【大师数】大教师 · 无私奉献 · 精神导师",
}


def digit_root(n: int, keep_master: bool = True) -> int:
    """数字根归约：反复求各位数字之和，直到为个位数（或大师数）"""
    while n > 9:
        if keep_master and n in MASTER_NUMBERS:
            return n
        n = sum(int(d) for d in str(n))
    return n


def life_path_number(year: int, month: int, day: int) -> int:
    """生命历程数（Life Path Number）：出生日期各位求和归约"""
    # 先分别归约年月日，再求和归约（标准方法）
    m = digit_root(month, keep_master=True)
    d = digit_root(day, keep_master=True)
    y = digit_root(year, keep_master=True)
    total = m + d + y
    return digit_root(total, keep_master=True)


def expression_number(full_name: str) -> int:
    """表达数/命运数（Expression Number）：全名所有字母求和归约"""
    total = sum(LETTER_MAP.get(c, 0) for c in full_name.upper() if c.isalpha())
    return digit_root(total)


def soul_urge_number(full_name: str) -> int:
    """心愿数（Soul Urge / Heart's Desire）：仅元音字母"""
    total = sum(LETTER_MAP.get(c, 0) for c in full_name.upper()
                if c.isalpha() and c in VOWELS)
    return digit_root(total)


def personality_number(full_name: str) -> int:
    """人格数（Personality Number）：仅辅音字母"""
    total = sum(LETTER_MAP.get(c, 0) for c in full_name.upper()
                if c.isalpha() and c not in VOWELS)
    return digit_root(total)


def birthday_number(day: int) -> int:
    """生日数（Birthday Number）：出生日归约"""
    return digit_root(day)


def calculate(name: str, year: int, month: int, day: int) -> dict:
    """完整数秘术计算"""
    return {
        "姓名": name,
        "出生日期": f"{year}-{month:02d}-{day:02d}",
        "生命历程数": life_path_number(year, month, day),
        "表达数": expression_number(name),
        "心愿数": soul_urge_number(name),
        "人格数": personality_number(name),
        "生日数": birthday_number(day),
    }


def display(result: dict):
    """格式化显示"""
    print("\n" + "═" * 50)
    print("  数秘术 · Numerology")
    print("═" * 50)
    print(f"\n  姓名：{result['姓名']}")
    print(f"  出生：{result['出生日期']}\n")

    items = [
        ("生命历程数", "Life Path", "核心人生主题"),
        ("表达数", "Expression", "天赋才能"),
        ("心愿数", "Soul Urge", "内心渴望"),
        ("人格数", "Personality", "外在形象"),
        ("生日数", "Birthday", "特殊才能"),
    ]

    for cn, en, desc in items:
        num = result[cn]
        meaning = MEANINGS.get(num, "")
        master = " ✦" if num in MASTER_NUMBERS else ""
        print(f"  {cn}（{en}）= {num}{master}")
        print(f"    └ {desc}：{meaning}")
    print()


def interactive():
    """交互式数秘术"""
    print("\n╔══════════════════════════════════════╗")
    print("║   数秘术 · Numerology               ║")
    print("║   Pythagorean Number System          ║")
    print("╚══════════════════════════════════════╝")
    print("\n  字母→数字归约，溯源至毕达哥拉斯学派。")
    print("  ⚠️ 本程序忠实复现计算规则，不代表认同其预测效力。\n")

    try:
        name = input("  姓名（拉丁字母，如 John Smith）：").strip()
        y = int(input("  出生年（如 1990）："))
        m = int(input("  出生月（1-12）："))
        d = int(input("  出生日（1-31）："))
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    result = calculate(name, y, m, d)
    display(result)


if __name__ == "__main__":
    interactive()
