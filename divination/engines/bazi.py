"""
八字命理 · 四柱推命排盘引擎
BaZi (Four Pillars of Destiny) Calculator

输入：出生年月日时（公历）
输出：四柱八字（年柱·月柱·日柱·时柱）+ 十神 + 五行统计 + 大运

算法核心：
  1. 公历→农历/干支历转换
  2. 年柱：以立春为界（非正月初一）
  3. 月柱：以节气定月，五虎遁起月干
  4. 日柱：查万年历或用蔡勒公式变体
  5. 时柱：五鼠遁起时干
"""

from datetime import datetime, date

# ─── 天干地支基础数据 ───

TIANGAN = "甲乙丙丁戊己庚辛壬癸"
DIZHI = "子丑寅卯辰巳午未申酉戌亥"
WUXING_GAN = {"甲": "木", "乙": "木", "丙": "火", "丁": "火",
              "戊": "土", "己": "土", "庚": "金", "辛": "金",
              "壬": "水", "癸": "水"}
WUXING_ZHI = {"子": "水", "丑": "土", "寅": "木", "卯": "木",
              "辰": "土", "巳": "火", "午": "火", "未": "土",
              "申": "金", "酉": "金", "戌": "土", "亥": "水"}
SHENGXIAO = "鼠牛虎兔龙蛇马羊猴鸡狗猪"

# 地支藏干
CANGGAN = {
    "子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"],
    "卯": ["乙"], "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"],
    "午": ["丁", "己"], "未": ["己", "丁", "乙"], "申": ["庚", "壬", "戊"],
    "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"],
}

# 十神关系（以日干为我）
SHISHEN_TABLE = {
    ("同", "阳"): "比肩", ("同", "阴"): "劫财",
    ("生", "阳"): "食神", ("生", "阴"): "伤官",
    ("克", "阳"): "偏财", ("克", "阴"): "正财",
    ("被克", "阳"): "七杀", ("被克", "阴"): "正官",
    ("被生", "阳"): "偏印", ("被生", "阴"): "正印",
}

WUXING_SHENG = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_KE = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

# ─── 节气数据（简化版：1900-2100年立春近似日期） ───
# 每年24节气的精确时刻需要天文算法，这里用简化方案

# 2000年各节气太阳黄经对应的近似日序（从1月1日起算）
# 节气序号0=小寒, 1=大寒, 2=立春, ..., 23=大寒(次年)
# 月柱以"节"（非"气"）为界：立春/惊蛰/清明/立夏/芒种/小暑/立秋/白露/寒露/立冬/大雪/小寒
JIE_MONTHS = [
    (2, 4),   # 寅月：立春 ~2月4日
    (3, 6),   # 卯月：惊蛰 ~3月6日
    (4, 5),   # 辰月：清明 ~4月5日
    (5, 6),   # 巳月：立夏 ~5月6日
    (6, 6),   # 午月：芒种 ~6月6日
    (7, 7),   # 未月：小暑 ~7月7日
    (8, 8),   # 申月：立秋 ~8月8日
    (9, 8),   # 酉月：白露 ~9月8日
    (10, 8),  # 戌月：寒露 ~10月8日
    (11, 7),  # 亥月：立冬 ~11月7日
    (12, 7),  # 子月：大雪 ~12月7日
    (1, 6),   # 丑月：小寒 ~1月6日（次年）
]


def _ganzhi(tg_idx: int, dz_idx: int) -> str:
    """组合天干地支"""
    return TIANGAN[tg_idx % 10] + DIZHI[dz_idx % 12]


def year_pillar(year: int, month: int, day: int) -> tuple[int, int]:
    """
    年柱：以立春为分界
    立春前属上一年
    返回 (天干索引, 地支索引)
    """
    # 简化：立春约在2月4日
    if month < 2 or (month == 2 and day < 4):
        year -= 1
    tg = (year - 4) % 10
    dz = (year - 4) % 12
    return tg, dz


def month_pillar(year_tg: int, month: int, day: int) -> tuple[int, int]:
    """
    月柱：以节气定月，五虎遁起月干
    五虎遁口诀：甲己之年丙作首，乙庚之岁戊为头，
                丙辛之岁庚寅上，丁壬壬寅顺水流，
                戊癸之年甲寅始
    返回 (天干索引, 地支索引)
    """
    # 确定月份地支（寅月=0, 卯月=1, ..., 丑月=11）
    month_idx = None
    for i, (m, d) in enumerate(JIE_MONTHS):
        if i < 11:
            next_m, next_d = JIE_MONTHS[i + 1]
        else:
            next_m, next_d = JIE_MONTHS[0]

        if m == month and day >= d:
            month_idx = i
        elif m == month and day < d:
            month_idx = (i - 1) % 12

    if month_idx is None:
        # 按月份粗略对应
        for i, (m, d) in enumerate(JIE_MONTHS):
            if m == month:
                month_idx = i if day >= d else (i - 1) % 12
                break
        if month_idx is None:
            month_idx = (month - 2) % 12  # fallback

    dz = (month_idx + 2) % 12  # 寅=2

    # 五虎遁：年干决定正月(寅月)天干
    start_gan = [2, 4, 6, 8, 0, 2, 4, 6, 8, 0]  # 甲→丙, 乙→戊, ...
    tg = (start_gan[year_tg] + month_idx) % 10

    return tg, dz


def day_pillar(year: int, month: int, day: int) -> tuple[int, int]:
    """
    日柱：基于已知参考日推算
    参考日：1900年1月1日 = 甲戌日 (tg=0, dz=10)
    即 1900-01-01 干支序数 = 10 (甲戌在六十甲子中序号10)
    """
    ref = date(1900, 1, 1)
    target = date(year, month, day)
    delta = (target - ref).days
    # 1900-01-01 = 甲子日后第10天 = 甲戌
    # 甲戌: 天干=甲(0), 地支=戌(10)
    gz_order = (delta + 10) % 60  # 六十甲子序号
    tg = gz_order % 10
    dz = gz_order % 12
    return tg, dz


def hour_pillar(day_tg: int, hour: int) -> tuple[int, int]:
    """
    时柱：五鼠遁起时干
    五鼠遁口诀：甲己还加甲，乙庚丙作初，
                丙辛从戊起，丁壬庚子居，戊癸壬子头
    hour: 0-23 的小时数
    """
    # 时辰地支（子时=23:00-01:00, 丑时=01:00-03:00, ...）
    shichen = [(23, 1), (1, 3), (3, 5), (5, 7), (7, 9), (9, 11),
               (11, 13), (13, 15), (15, 17), (17, 19), (19, 21), (21, 23)]
    dz = 0
    for i, (start, end) in enumerate(shichen):
        if start > end:  # 子时跨日
            if hour >= start or hour < end:
                dz = i
                break
        else:
            if start <= hour < end:
                dz = i
                break

    # 五鼠遁：日干决定子时天干
    start_gan = [0, 2, 4, 6, 8, 0, 2, 4, 6, 8]  # 甲→甲, 乙→丙, ...
    tg = (start_gan[day_tg] + dz) % 10

    return tg, dz


def get_shishen(ri_gan: str, other_gan: str) -> str:
    """计算十神关系"""
    wx_ri = WUXING_GAN[ri_gan]
    wx_other = WUXING_GAN[other_gan]

    ri_idx = TIANGAN.index(ri_gan)
    other_idx = TIANGAN.index(other_gan)
    same_polarity = (ri_idx % 2) == (other_idx % 2)
    yin_yang = "阳" if same_polarity else "阴"

    if wx_ri == wx_other:
        relation = "同"
    elif WUXING_SHENG[wx_ri] == wx_other:
        relation = "生"
    elif WUXING_KE[wx_ri] == wx_other:
        relation = "克"
    elif WUXING_SHENG[wx_other] == wx_ri:
        relation = "被生"
    else:
        relation = "被克"

    return SHISHEN_TABLE[(relation, yin_yang)]


def wuxing_count(pillars: list[tuple[int, int]]) -> dict[str, int]:
    """统计八字中的五行分布"""
    count = {"金": 0, "木": 0, "水": 0, "火": 0, "土": 0}
    for tg, dz in pillars:
        count[WUXING_GAN[TIANGAN[tg % 10]]] += 1
        count[WUXING_ZHI[DIZHI[dz % 12]]] += 1
    return count


def paipan(year: int, month: int, day: int, hour: int) -> dict:
    """
    八字排盘主函数
    返回完整命盘信息
    """
    y_tg, y_dz = year_pillar(year, month, day)
    m_tg, m_dz = month_pillar(y_tg, month, day)
    d_tg, d_dz = day_pillar(year, month, day)
    h_tg, h_dz = hour_pillar(d_tg, hour)

    pillars = [(y_tg, y_dz), (m_tg, m_dz), (d_tg, d_dz), (h_tg, h_dz)]
    ri_gan = TIANGAN[d_tg % 10]  # 日干=命主

    # 各柱十神
    shishen = []
    for i, (tg, dz) in enumerate(pillars):
        gan = TIANGAN[tg % 10]
        if i == 2:  # 日柱天干是"我"
            shishen.append("日元")
        else:
            shishen.append(get_shishen(ri_gan, gan))

    # 五行统计
    wx = wuxing_count(pillars)

    # 生肖
    sx = SHENGXIAO[y_dz % 12]

    result = {
        "年柱": _ganzhi(y_tg, y_dz),
        "月柱": _ganzhi(m_tg, m_dz),
        "日柱": _ganzhi(d_tg, d_dz),
        "时柱": _ganzhi(h_tg, h_dz),
        "日元": ri_gan,
        "十神": {"年": shishen[0], "月": shishen[1], "日": shishen[2], "时": shishen[3]},
        "五行": wx,
        "生肖": sx,
        "纳音五行": _nayin(y_tg, y_dz),
    }
    return result


def _nayin(tg: int, dz: int) -> str:
    """纳音五行（六十甲子纳音表）"""
    nayin_table = [
        "海中金", "炉中火", "大林木", "路旁土", "剑锋金", "山头火",
        "涧下水", "城头土", "白蜡金", "杨柳木", "泉中水", "屋上土",
        "霹雳火", "松柏木", "长流水", "沙中金", "山下火", "平地木",
        "壁上土", "金箔金", "覆灯火", "天河水", "大驿土", "钗钏金",
        "桑柘木", "大溪水", "沙中土", "天上火", "石榴木", "大海水",
    ]
    gz_order = (tg % 10) * 6 + (dz % 12) // 2  # 简化映射
    # 正确的六十甲子序号
    gz_idx = 0
    for i in range(60):
        if i % 10 == tg % 10 and i % 12 == dz % 12:
            gz_idx = i
            break
    return nayin_table[gz_idx // 2 % 30]


def display(result: dict):
    """格式化显示八字命盘"""
    print("\n" + "═" * 50)
    print("  八字命理 · 四柱排盘")
    print("═" * 50)

    print(f"\n  生肖：{result['生肖']}  |  纳音：{result['纳音五行']}")
    print(f"  日元（命主）：{result['日元']}（{WUXING_GAN[result['日元']]}）\n")

    # 四柱展示
    labels = ["年柱", "月柱", "日柱", "时柱"]
    gods = ["年", "月", "日", "时"]
    print("  ┌────────┬────────┬────────┬────────┐")
    print(f"  │  {labels[0]}  │  {labels[1]}  │  {labels[2]}  │  {labels[3]}  │")
    print("  ├────────┼────────┼────────┼────────┤")
    row1 = ""
    for l in labels:
        gz = result[l]
        row1 += f"│  {gz[0]} {gz[1]}  "
    print(f"  {row1}│")
    print("  ├────────┼────────┼────────┼────────┤")
    row2 = ""
    for g in gods:
        ss = result["十神"][g]
        padding = "  " if len(ss) == 2 else " "
        row2 += f"│ {ss}{padding}"
    print(f"  {row2}│")
    print("  └────────┴────────┴────────┴────────┘")

    # 五行统计
    print("\n  五行分布：", end="")
    symbols = {"金": "🪙", "木": "🌳", "水": "💧", "火": "🔥", "土": "⛰️ "}
    for wx, cnt in result["五行"].items():
        print(f" {symbols.get(wx, '')}{wx}:{cnt}", end="")
    print()

    # 缺失五行
    missing = [wx for wx, cnt in result["五行"].items() if cnt == 0]
    if missing:
        print(f"  ⚠️  五行缺：{'、'.join(missing)}")

    print()


def interactive():
    """交互式八字排盘"""
    print("\n╔══════════════════════════════════════╗")
    print("║   八字命理 · 四柱推命排盘           ║")
    print("║   BaZi / Four Pillars of Destiny    ║")
    print("╚══════════════════════════════════════╝")
    print("\n  唐李虚中创三柱法，宋徐子平增时柱成四柱。")
    print("  ⚠️ 本程序忠实复现排盘算法，不代表认同其预测效力。\n")

    try:
        y = int(input("  出生年（公历，如 1990）："))
        m = int(input("  出生月（1-12）："))
        d = int(input("  出生日（1-31）："))
        h = int(input("  出生时（0-23，如 14 表示下午2点）："))
    except (ValueError, EOFError):
        print("  输入无效。")
        return

    result = paipan(y, m, d, h)
    display(result)


if __name__ == "__main__":
    interactive()
