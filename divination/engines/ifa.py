"""
Ifá 占卜引擎
Ifá Divination System (Yorùbá / West Africa)

输入：模拟抓取 Ikin 或抛 Ọ̀pẹ̀lẹ̀ 链
输出：256个 Odù 之一 + 对应的诗歌/格言

算法核心：2⁸ = 256 个 Odù，8位二进制编码
  - 每次操作产生单线(|)或双线(||)
  - 4次操作生成一个半 Odù，两半组成完整 Odù
  - 前16个主 Odù（Olódù）地位最高
"""

import random

# ─── 16 个主 Odù（Olódù / Méjì）───
# 每个 Odù 由4位二进制组成：| = 1 (ikin剩1), || = 0 (ikin剩2)

OLODU = [
    {"binary": (1, 1, 1, 1), "name": "Ogbè", "yoruba": "Ògbè Méjì",
     "meaning": "光明、清晰、新开始", "proverb": "Ìmọ̀lẹ̀ ni baba ọ̀rọ̀ — 光明是万事之父"},
    {"binary": (0, 0, 0, 0), "name": "Òyèkú", "yoruba": "Òyèkú Méjì",
     "meaning": "黑暗、死亡、转化", "proverb": "Ikú ò sí nínú aye — 世间无物永存"},
    {"binary": (1, 0, 1, 0), "name": "Ìwòrì", "yoruba": "Ìwòrì Méjì",
     "meaning": "对立面的统一、选择", "proverb": "Ohun méjì ṣàjọ ni ń jẹ́ ìwà — 两面共存方为真性"},
    {"binary": (0, 1, 0, 1), "name": "Odí", "yoruba": "Odí Méjì",
     "meaning": "保护、女性力量、生育", "proverb": "Obìnrin ló bí ọmọ — 是女人孕育了生命"},
    {"binary": (1, 1, 0, 0), "name": "Ìrosùn", "yoruba": "Ìrosùn Méjì",
     "meaning": "祖先的记忆、传承", "proverb": "Ẹni tí kò mọ ibi tó ti wá — 不知来处者不知去处"},
    {"binary": (0, 0, 1, 1), "name": "Ọ̀wọ́nrín", "yoruba": "Ọ̀wọ́nrín Méjì",
     "meaning": "混乱与秩序、出其不意", "proverb": "Ohun tí a ò retí ni ó máa ń ṣẹlẹ̀ — 意想不到之事终会发生"},
    {"binary": (1, 0, 0, 1), "name": "Ọ̀bàrà", "yoruba": "Ọ̀bàrà Méjì",
     "meaning": "领导力、王权、权威", "proverb": "Ọba aláṣẹ kì í jẹ́ kí ilé rú — 真正的领袖不让家园混乱"},
    {"binary": (0, 1, 1, 0), "name": "Ọ̀kànràn", "yoruba": "Ọ̀kànràn Méjì",
     "meaning": "逆转、反转、强大的力量", "proverb": "Àtúnṣe bá ilé tí kò dára — 修复需先认识破损"},
    {"binary": (1, 1, 1, 0), "name": "Ògúndá", "yoruba": "Ògúndá Méjì",
     "meaning": "冲突、开路、Ògún的力量", "proverb": "Ìjà kì í gun ẹ̀ṣin — 争斗不可骑马远行"},
    {"binary": (0, 1, 1, 1), "name": "Ọ̀sá", "yoruba": "Ọ̀sá Méjì",
     "meaning": "流动、变化、适应", "proverb": "Omi kì í san kí ó dé ibikan — 水不会只流向一处"},
    {"binary": (1, 0, 0, 0), "name": "Ìká", "yoruba": "Ìká Méjì",
     "meaning": "谨慎、隐藏的危险", "proverb": "Ẹni tí ó fagilé kì í yẹ̀ — 举刀者须先三思"},
    {"binary": (0, 0, 0, 1), "name": "Oturukpọ̀n", "yoruba": "Oturukpọ̀n Méjì",
     "meaning": "和平、解决冲突", "proverb": "Àlàáfíà ló jù gbogbo — 和平胜过一切"},
    {"binary": (1, 1, 0, 1), "name": "Otúrá", "yoruba": "Otúrá Méjì",
     "meaning": "精神成长、智慧", "proverb": "Ẹ̀kọ́ ló ń mú ni dàgbà — 学习使人成长"},
    {"binary": (1, 0, 1, 1), "name": "Ìrẹtẹ̀", "yoruba": "Ìrẹtẹ̀ Méjì",
     "meaning": "坚定、决心、力量", "proverb": "Iṣẹ́ aṣeju ní ń pani — 过劳者自损"},
    {"binary": (0, 1, 0, 0), "name": "Ọ̀ṣẹ́", "yoruba": "Ọ̀ṣẹ́ Méjì",
     "meaning": "繁荣、丰饶、Ọ̀ṣun的祝福", "proverb": "Ọ̀ṣun ní í fún ni lówó — 是Ọ̀ṣun赐予财富"},
    {"binary": (0, 0, 1, 0), "name": "Òfún", "yoruba": "Òfún Méjì",
     "meaning": "完成、神圣的白色、真理", "proverb": "Funfun ló jẹ́ àṣà Ọlọ́run — 白色是上天的印记"},
]


def cast_half_odu(method: str = "opele") -> tuple:
    """
    生成半个 Odù（4位二进制）

    method:
      "opele" - 抛 Ọ̀pẹ̀lẹ̀ 链（每次凸/凹各50%）
      "ikin"  - 抓取 Ikin 棕榈果（剩1=单线, 剩2=双线，概率不完全均匀）
    """
    if method == "ikin":
        # Ikin 法：从16颗棕榈果中抓取，剩1或2有效
        # 简化：剩1(单线=1)约60%, 剩2(双线=0)约40%（非精确均匀）
        return tuple(1 if random.random() < 0.6 else 0 for _ in range(4))
    else:
        # Ọ̀pẹ̀lẹ̀ 链法：每枚果壳凸/凹各50%
        return tuple(random.randint(0, 1) for _ in range(4))


def cast_odu(method: str = "opele") -> dict:
    """生成完整 Odù"""
    right = cast_half_odu(method)  # 右半（先掷）
    left = cast_half_odu(method)   # 左半（后掷）

    # 查找主 Odù
    right_info = None
    left_info = None
    for odu in OLODU:
        if odu["binary"] == right:
            right_info = odu
        if odu["binary"] == left:
            left_info = odu

    # Méjì（双）= 左右相同
    is_meji = right == left

    # 组合名称
    if is_meji and right_info:
        full_name = right_info["yoruba"]
    elif right_info and left_info:
        full_name = f"{right_info['name']}-{left_info['name']}"
    else:
        full_name = "组合 Odù"

    # 256中的序号
    odu_num = 0
    for i, bit in enumerate(right + left):
        odu_num |= (bit << (7 - i))

    return {
        "右半": right,
        "左半": left,
        "右半名": right_info["name"] if right_info else "?",
        "左半名": left_info["name"] if left_info else "?",
        "完整名": full_name,
        "是否Méjì": is_meji,
        "二进制序号": odu_num,
        "方法": "Ikin 棕榈果法" if method == "ikin" else "Ọ̀pẹ̀lẹ̀ 链法",
        "右半信息": right_info,
        "左半信息": left_info,
    }


def draw_half(half: tuple, label: str):
    """绘制半个 Odù"""
    print(f"    {label}：")
    for bit in half:
        mark = "  |" if bit == 1 else "  | |"
        print(f"      {mark}")


def display(result: dict):
    """格式化显示"""
    print("\n" + "═" * 56)
    print(f"  Ifá 占卜 · {result['方法']}")
    print("═" * 56)

    print(f"\n  Odù：{result['完整名']}")
    if result["是否Méjì"]:
        print(f"  ✦ Méjì（双）— 主 Odù，地位崇高")
    print(f"  二进制序号：{result['二进制序号']} / 256\n")

    draw_half(result["右半"], f"右半 ({result['右半名']})")
    draw_half(result["左半"], f"左半 ({result['左半名']})")

    # 显示含义
    for half_key, info_key in [("右半名", "右半信息"), ("左半名", "左半信息")]:
        info = result[info_key]
        if info:
            print(f"\n  ── {info['yoruba']} ──")
            print(f"    含义：{info['meaning']}")
            print(f"    格言：{info['proverb']}")

    print(f"\n  ────────────────────────────")
    print(f"  📊 Ifá 是 2⁸=256 的完备二进制编码系统，")
    print(f"     与中国易经（2⁶=64）和阿拉伯沙占（2⁴=16）")
    print(f"     构成跨文明的二进制占卜家族。")
    print()


def interactive():
    """交互式 Ifá 占卜"""
    print("\n╔══════════════════════════════════════╗")
    print("║   Ifá 占卜 · 约鲁巴传统             ║")
    print("║   Ifá Divination (UNESCO ICH)        ║")
    print("╚══════════════════════════════════════╝")
    print("\n  2⁸=256个Odù，西非约鲁巴民族的知识体系。")
    print("  2005年列入UNESCO人类非物质文化遗产代表作。")
    print("  ⚠️ 本程序忠实复现编码机制，不代表认同其预测效力。\n")

    print("  方法：1=Ọ̀pẹ̀lẹ̀ 链法（均匀概率）")
    print("        2=Ikin 棕榈果法（非均匀概率）")

    try:
        choice = input("\n  请选择（1/2）：").strip()
    except EOFError:
        return

    method = "ikin" if choice == "2" else "opele"
    result = cast_odu(method)
    display(result)


if __name__ == "__main__":
    interactive()
