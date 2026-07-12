"""
塔罗牌占卜引擎
Tarot Card Divination Engine

输入：选择牌阵 + 随机洗牌
输出：牌阵各位置的牌 + 正逆位 + 牌义

算法核心：78张牌无放回随机抽取，正/逆位各50%
"""

import random

# ─── 大阿卡纳（Major Arcana）22张 ───

MAJOR_ARCANA = [
    {"num": 0, "name": "愚者", "en": "The Fool",
     "upright": "新开始、自由、天真、冒险",
     "reversed": "鲁莽、冒失、不负责任"},
    {"num": 1, "name": "魔术师", "en": "The Magician",
     "upright": "创造力、意志力、技巧、自信",
     "reversed": "欺骗、操控、才能浪费"},
    {"num": 2, "name": "女祭司", "en": "The High Priestess",
     "upright": "直觉、潜意识、内在知识、神秘",
     "reversed": "秘密、脱离直觉、表面化"},
    {"num": 3, "name": "女皇", "en": "The Empress",
     "upright": "丰饶、母性、自然、美丽",
     "reversed": "依赖、空虚、过度溺爱"},
    {"num": 4, "name": "皇帝", "en": "The Emperor",
     "upright": "权威、结构、控制、父性",
     "reversed": "专制、僵化、缺乏纪律"},
    {"num": 5, "name": "教皇", "en": "The Hierophant",
     "upright": "传统、信仰、教育、指导",
     "reversed": "反叛、非传统、自由思想"},
    {"num": 6, "name": "恋人", "en": "The Lovers",
     "upright": "爱情、和谐、选择、价值观",
     "reversed": "不和谐、失衡、价值冲突"},
    {"num": 7, "name": "战车", "en": "The Chariot",
     "upright": "意志力、胜利、决心、控制",
     "reversed": "失控、攻击性、方向迷失"},
    {"num": 8, "name": "力量", "en": "Strength",
     "upright": "勇气、耐心、内在力量、同情",
     "reversed": "软弱、自我怀疑、缺乏自制"},
    {"num": 9, "name": "隐者", "en": "The Hermit",
     "upright": "内省、寻找、指引、独处",
     "reversed": "孤立、偏执、退缩"},
    {"num": 10, "name": "命运之轮", "en": "Wheel of Fortune",
     "upright": "转折、命运、机遇、循环",
     "reversed": "厄运、抗拒变化、失控"},
    {"num": 11, "name": "正义", "en": "Justice",
     "upright": "公正、真理、因果、法律",
     "reversed": "不公、逃避责任、欺骗"},
    {"num": 12, "name": "倒吊人", "en": "The Hanged Man",
     "upright": "牺牲、放手、新视角、等待",
     "reversed": "拖延、抵抗、无谓牺牲"},
    {"num": 13, "name": "死神", "en": "Death",
     "upright": "结束、转变、过渡、放下",
     "reversed": "抗拒改变、停滞、执着"},
    {"num": 14, "name": "节制", "en": "Temperance",
     "upright": "平衡、耐心、调和、适度",
     "reversed": "失衡、过度、不协调"},
    {"num": 15, "name": "恶魔", "en": "The Devil",
     "upright": "束缚、欲望、物质、阴影",
     "reversed": "释放、突破、恢复控制"},
    {"num": 16, "name": "塔", "en": "The Tower",
     "upright": "突变、崩塌、启示、解放",
     "reversed": "逃避灾难、延迟变革"},
    {"num": 17, "name": "星星", "en": "The Star",
     "upright": "希望、灵感、宁静、更新",
     "reversed": "绝望、失去信心、断联"},
    {"num": 18, "name": "月亮", "en": "The Moon",
     "upright": "幻觉、恐惧、潜意识、不确定",
     "reversed": "释放恐惧、真相大白"},
    {"num": 19, "name": "太阳", "en": "The Sun",
     "upright": "快乐、成功、活力、自信",
     "reversed": "暂时受挫、过度乐观"},
    {"num": 20, "name": "审判", "en": "Judgement",
     "upright": "觉醒、重生、召唤、赦免",
     "reversed": "自我怀疑、拒绝召唤"},
    {"num": 21, "name": "世界", "en": "The World",
     "upright": "完成、整合、成就、旅行",
     "reversed": "未完成、缺乏结束感"},
]

# ─── 小阿卡纳（Minor Arcana）56张（简化版，只列花色含义） ───

SUITS = {
    "权杖": {"element": "火", "domain": "行动/热情/创造",
             "cards": ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                       "侍从", "骑士", "王后", "国王"]},
    "圣杯": {"element": "水", "domain": "情感/关系/直觉",
             "cards": ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                       "侍从", "骑士", "王后", "国王"]},
    "宝剑": {"element": "风", "domain": "思想/冲突/真相",
             "cards": ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                       "侍从", "骑士", "王后", "国王"]},
    "钱币": {"element": "土", "domain": "物质/工作/健康",
             "cards": ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10",
                       "侍从", "骑士", "王后", "国王"]},
}

# ─── 牌阵定义 ───

SPREADS = {
    "single": {
        "name": "单牌占卜",
        "positions": ["核心信息"],
        "description": "最简单的占卜，抽一张牌回答一个问题",
    },
    "three": {
        "name": "三牌阵（时间之流）",
        "positions": ["过去", "现在", "未来"],
        "description": "展示事件的时间脉络",
    },
    "celtic": {
        "name": "凯尔特十字牌阵",
        "positions": [
            "① 现状（核心）", "② 挑战（阻碍）", "③ 潜意识基础",
            "④ 过去", "⑤ 目标/最佳结果", "⑥ 近未来",
            "⑦ 自我态度", "⑧ 外部环境", "⑨ 希望与恐惧",
            "⑩ 最终结果"
        ],
        "description": "最经典的复杂牌阵，全面分析",
    },
}


def build_deck() -> list[dict]:
    """构建完整78张牌组"""
    deck = []

    # 大阿卡纳
    for card in MAJOR_ARCANA:
        deck.append({
            "type": "大阿卡纳",
            "name": card["name"],
            "en": card["en"],
            "upright": card["upright"],
            "reversed": card["reversed"],
        })

    # 小阿卡纳
    for suit, info in SUITS.items():
        for card_name in info["cards"]:
            deck.append({
                "type": "小阿卡纳",
                "name": f"{suit}{card_name}",
                "en": f"{card_name} of {suit}",
                "upright": f"{info['domain']}（{info['element']}）的正面能量",
                "reversed": f"{info['domain']}（{info['element']}）的挑战面",
            })

    return deck


def draw(spread: str = "three") -> dict:
    """抽牌"""
    spread_info = SPREADS.get(spread, SPREADS["three"])
    n = len(spread_info["positions"])

    deck = build_deck()
    random.shuffle(deck)

    drawn = []
    for i in range(n):
        card = deck[i]
        is_reversed = random.choice([True, False])
        drawn.append({
            "position": spread_info["positions"][i],
            "card": card,
            "reversed": is_reversed,
        })

    return {
        "spread": spread_info["name"],
        "description": spread_info["description"],
        "cards": drawn,
    }


def display(result: dict):
    """格式化显示塔罗占卜结果"""
    print("\n" + "═" * 56)
    print(f"  塔罗牌 · {result['spread']}")
    print("═" * 56)
    print(f"  {result['description']}\n")

    for item in result["cards"]:
        card = item["card"]
        rev = "【逆位】" if item["reversed"] else "【正位】"
        meaning = card["reversed"] if item["reversed"] else card["upright"]

        print(f"  ┌─ {item['position']} ─────────────────────")
        print(f"  │  🃏 {card['name']} ({card['en']}) {rev}")
        print(f"  │  {card['type']}")
        print(f"  │  含义：{meaning}")
        print(f"  └───────────────────────────────────")
    print()


def interactive():
    """交互式塔罗占卜"""
    print("\n╔══════════════════════════════════════╗")
    print("║   塔罗牌 · Tarot Divination         ║")
    print("║   Rider-Waite-Smith System           ║")
    print("╚══════════════════════════════════════╝")
    print("\n  1781年Court de Gébelin伪造埃及起源说，")
    print("  实际1420年代诞生于意大利，最初是纸牌游戏。")
    print("  ⚠️ 本程序忠实复现抽牌机制，解读仅供参考。\n")

    print("  牌阵选择：")
    for key, spread in SPREADS.items():
        print(f"    {key:8s} - {spread['name']}（{len(spread['positions'])}张）")

    try:
        choice = input("\n  请选择牌阵：").strip()
    except EOFError:
        return

    if choice not in SPREADS:
        choice = "three"

    result = draw(choice)
    display(result)


if __name__ == "__main__":
    interactive()
