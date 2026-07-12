"""
沙占 / Geomancy 引擎
Arabian Geomancy (علم الرمل) / Sikidy (Madagascar)

输入：4次随机打点（或自动生成）
输出：完整 geomantic tableau（母图→女图→侄图→见证→法官）

算法核心：
  - 2⁴ = 16种基本图形
  - 异或运算（XOR / 奇偶合成）递推派生
  - 自带校验机制
"""

import random

# ─── 16种基本图形 ───

FIGURES = {
    (1, 1, 1, 1): {"name": "Via", "ar": "طريق", "cn": "路", "element": "水",
                    "meaning": "道路、旅行、变化、流动"},
    (0, 0, 0, 0): {"name": "Populus", "ar": "جماعة", "cn": "众", "element": "水",
                    "meaning": "人群、聚集、被动、等待"},
    (1, 0, 1, 0): {"name": "Acquisitio", "ar": "اكتساب", "cn": "得", "element": "火",
                    "meaning": "获得、收获、成功、增长"},
    (0, 1, 0, 1): {"name": "Amissio", "ar": "خسارة", "cn": "失", "element": "火",
                    "meaning": "失去、损失、放下、释放"},
    (1, 1, 0, 0): {"name": "Fortuna Major", "ar": "السعد الأكبر", "cn": "大吉", "element": "土",
                    "meaning": "大吉、保护、成功、力量"},
    (0, 0, 1, 1): {"name": "Fortuna Minor", "ar": "السعد الأصغر", "cn": "小吉", "element": "火",
                    "meaning": "小吉、速度、变化中的成功"},
    (1, 0, 0, 1): {"name": "Conjunctio", "ar": "اجتماع", "cn": "合", "element": "风",
                    "meaning": "联合、结合、交叉路口"},
    (0, 1, 1, 0): {"name": "Carcer", "ar": "سجن", "cn": "困", "element": "土",
                    "meaning": "监禁、限制、束缚、稳定"},
    (1, 1, 1, 0): {"name": "Laetitia", "ar": "فرح", "cn": "喜", "element": "火",
                    "meaning": "快乐、上升、希望、乐观"},
    (0, 1, 1, 1): {"name": "Tristitia", "ar": "حزن", "cn": "悲", "element": "土",
                    "meaning": "悲伤、下降、根基、深沉"},
    (1, 0, 0, 0): {"name": "Caput Draconis", "ar": "رأس التنين", "cn": "龙首", "element": "土",
                    "meaning": "开始、入口、上升的北月交点"},
    (0, 0, 0, 1): {"name": "Cauda Draconis", "ar": "ذنب التنين", "cn": "龙尾", "element": "火",
                    "meaning": "结束、出口、下降的南月交点"},
    (1, 1, 0, 1): {"name": "Rubeus", "ar": "أحمر", "cn": "赤", "element": "风",
                    "meaning": "红色、激情、危险、愤怒"},
    (1, 0, 1, 1): {"name": "Albus", "ar": "أبيض", "cn": "白", "element": "水",
                    "meaning": "白色、纯净、智慧、和平"},
    (0, 1, 0, 0): {"name": "Puella", "ar": "بنت", "cn": "女", "element": "水",
                    "meaning": "少女、美丽、和谐、被动"},
    (0, 0, 1, 0): {"name": "Puer", "ar": "ولد", "cn": "男", "element": "风",
                    "meaning": "少年、勇气、冲动、行动"},
}


def xor_figures(f1: tuple, f2: tuple) -> tuple:
    """异或运算合成两个图形（每行奇偶判定）"""
    return tuple((a + b) % 2 for a, b in zip(f1, f2))


def generate_mother(manual: bool = False) -> list[tuple]:
    """
    生成4个母图（Mother Figures）
    manual=True: 手动打点
    manual=False: 随机生成
    """
    mothers = []
    for i in range(4):
        if manual:
            print(f"\n  第{i+1}个母图（输入4行，每行输入若干点数或奇/偶）：")
            lines = []
            for j in range(4):
                try:
                    dots = int(input(f"    第{j+1}行点数："))
                except (ValueError, EOFError):
                    dots = random.randint(1, 20)
                lines.append(dots % 2)  # 奇=1, 偶=0
            mothers.append(tuple(lines))
        else:
            mothers.append(tuple(random.randint(0, 1) for _ in range(4)))
    return mothers


def build_tableau(mothers: list[tuple]) -> dict:
    """
    构建完整 geomantic tableau
    4母图 → 4女图 → 4侄图 → 2见证 → 1法官
    共15个图形
    """
    m1, m2, m3, m4 = mothers

    # 女图 = 母图各行横向重组
    d1 = (m1[0], m2[0], m3[0], m4[0])
    d2 = (m1[1], m2[1], m3[1], m4[1])
    d3 = (m1[2], m2[2], m3[2], m4[2])
    d4 = (m1[3], m2[3], m3[3], m4[3])
    daughters = [d1, d2, d3, d4]

    # 侄图 = 相邻两图异或
    all_eight = mothers + daughters
    nephews = [
        xor_figures(all_eight[0], all_eight[1]),
        xor_figures(all_eight[2], all_eight[3]),
        xor_figures(all_eight[4], all_eight[5]),
        xor_figures(all_eight[6], all_eight[7]),
    ]

    # 见证 = 相邻侄图异或
    witnesses = [
        xor_figures(nephews[0], nephews[1]),
        xor_figures(nephews[2], nephews[3]),
    ]

    # 法官 = 两见证异或
    judge = xor_figures(witnesses[0], witnesses[1])

    # 校验：法官的点数总和必须为偶数（自校验机制）
    judge_sum = sum(judge)
    valid = judge_sum % 2 == 0

    return {
        "母图": mothers,
        "女图": daughters,
        "侄图": nephews,
        "见证": witnesses,
        "法官": judge,
        "校验通过": valid,
    }


def fig_to_str(fig: tuple) -> str:
    """图形转可视化字符串"""
    return "  ".join("●" if x == 1 else "● ●" for x in fig)


def get_fig_info(fig: tuple) -> dict:
    """获取图形信息"""
    return FIGURES.get(fig, {"name": "?", "cn": "?", "meaning": "未知"})


def display(tableau: dict):
    """格式化显示占卜盘"""
    print("\n" + "═" * 56)
    print("  沙占 · Geomancy · علم الرمل")
    print("═" * 56)

    sections = [
        ("母图 (Mothers)", "母图"),
        ("女图 (Daughters)", "女图"),
        ("侄图 (Nieces)", "侄图"),
        ("见证 (Witnesses)", "见证"),
    ]

    for label, key in sections:
        print(f"\n  ── {label} ──")
        for i, fig in enumerate(tableau[key]):
            info = get_fig_info(fig)
            print(f"    {i+1}. {info.get('cn', '?')} ({info['name']})")
            for row in fig:
                dots = "  ●" if row == 1 else "  ● ●"
                print(f"      {dots}")
            print(f"       → {info.get('meaning', '')}")

    # 法官
    judge_info = get_fig_info(tableau["法官"])
    print(f"\n  ══ 法官 (Judge) ══")
    print(f"    {judge_info.get('cn', '?')} ({judge_info['name']})")
    for row in tableau["法官"]:
        dots = "  ●" if row == 1 else "  ● ●"
        print(f"      {dots}")
    print(f"    → {judge_info.get('meaning', '')}")

    check = "✅ 通过" if tableau["校验通过"] else "❌ 失败"
    print(f"\n  自校验：{check}")
    print()


def interactive():
    """交互式沙占"""
    print("\n╔══════════════════════════════════════╗")
    print("║   沙占 · Geomancy · 土占             ║")
    print("║   Arabian / Malagasy Sikidy          ║")
    print("╚══════════════════════════════════════╝")
    print("\n  2⁴=16种基本图形，异或运算递推。")
    print("  ⚠️ 本程序忠实复现推演算法，不代表认同其预测效力。\n")

    print("  模式：1=自动随机  2=手动打点")
    try:
        mode = input("  请选择（1/2）：").strip()
    except EOFError:
        return

    manual = mode == "2"
    mothers = generate_mother(manual)
    tableau = build_tableau(mothers)
    display(tableau)


if __name__ == "__main__":
    interactive()
