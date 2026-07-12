"""
易经占卦引擎
I Ching (Book of Changes) Divination Engine

支持两种起卦法：
  1. 大衍筮法（蓍草法）—— 概率分布：老阴1/16, 少阳5/16, 少阴7/16, 老阳3/16
  2. 三枚硬币法 —— 概率分布：老阴1/8, 少阳3/8, 少阴3/8, 老阳1/8

算法核心：
  - 每种方法生成6爻 → 2⁶ = 64卦之一
  - 动爻（老阳/老阴）变化生成变卦
  - 输出本卦 + 变卦 + 卦辞 + 爻辞
"""

import random

# ─── 八卦基础 ───

BAGUA = {
    (1, 1, 1): {"name": "乾", "symbol": "☰", "nature": "天", "wuxing": "金"},
    (0, 0, 0): {"name": "坤", "symbol": "☷", "nature": "地", "wuxing": "土"},
    (1, 0, 0): {"name": "震", "symbol": "☳", "nature": "雷", "wuxing": "木"},
    (0, 1, 0): {"name": "坎", "symbol": "☵", "nature": "水", "wuxing": "水"},
    (0, 0, 1): {"name": "艮", "symbol": "☶", "nature": "山", "wuxing": "土"},
    (0, 1, 1): {"name": "巽", "symbol": "☴", "nature": "风", "wuxing": "木"},
    (1, 0, 1): {"name": "离", "symbol": "☲", "nature": "火", "wuxing": "火"},
    (1, 1, 0): {"name": "兑", "symbol": "☱", "nature": "泽", "wuxing": "金"},
}

# 爻的四种状态
YAO_TYPES = {
    6: {"name": "老阴", "symbol": "- X -", "value": 0, "changes": True},
    7: {"name": "少阳", "symbol": "─────", "value": 1, "changes": False},
    8: {"name": "少阴", "symbol": "── ──", "value": 0, "changes": False},
    9: {"name": "老阳", "symbol": "━ O ━", "value": 1, "changes": True},
}

# 六十四卦（上卦, 下卦）→ 卦名和卦辞
# 格式：(上卦三爻, 下卦三爻) → (卦名, 卦辞简要)
HEXAGRAMS = {}

# 卦名表（按先天八卦序：乾兑离震巽坎艮坤）
GUA_NAMES = [
    # 上乾
    ["乾为天", "泽天夬", "火天大有", "雷天大壮", "风天小畜", "水天需", "山天大畜", "地天泰"],
    # 上兑
    ["天泽履", "兑为泽", "火泽睽", "雷泽归妹", "风泽中孚", "水泽节", "山泽损", "地泽临"],
    # 上离
    ["天火同人", "泽火革", "离为火", "雷火丰", "风火家人", "水火既济", "山火贲", "地火明夷"],
    # 上震
    ["天雷无妄", "泽雷随", "火雷噬嗑", "震为雷", "风雷益", "水雷屯", "山雷颐", "地雷复"],
    # 上巽
    ["天风姤", "泽风大过", "火风鼎", "雷风恒", "巽为风", "水风井", "山风蛊", "地风升"],
    # 上坎
    ["天水讼", "泽水困", "火水未济", "雷水解", "风水涣", "坎为水", "山水蒙", "地水师"],
    # 上艮
    ["天山遁", "泽山咸", "火山旅", "雷山小过", "风山渐", "水山蹇", "艮为山", "地山谦"],
    # 上坤
    ["天地否", "泽地萃", "火地晋", "雷地豫", "风地观", "水地比", "山地剥", "坤为地"],
]

# 八卦到索引的映射（按先天序）
BAGUA_ORDER = {
    (1, 1, 1): 0,  # 乾
    (1, 1, 0): 1,  # 兑
    (1, 0, 1): 2,  # 离
    (1, 0, 0): 3,  # 震
    (0, 1, 1): 4,  # 巽
    (0, 1, 0): 5,  # 坎
    (0, 0, 1): 6,  # 艮
    (0, 0, 0): 7,  # 坤
}

# 卦辞简表（64卦序号 → 卦辞摘要）
GUA_CI = {
    "乾为天": "元亨利贞。",
    "坤为地": "元亨，利牝马之贞。",
    "水雷屯": "元亨利贞，勿用有攸往，利建侯。",
    "山水蒙": "亨。匪我求童蒙，童蒙求我。",
    "水天需": "有孚，光亨，贞吉。利涉大川。",
    "天水讼": "有孚，窒惕，中吉，终凶。利见大人，不利涉大川。",
    "地水师": "贞，丈人吉，无咎。",
    "水地比": "吉。原筮元永贞，无咎。不宁方来，后夫凶。",
    "风天小畜": "亨。密云不雨，自我西郊。",
    "天泽履": "履虎尾，不咥人，亨。",
    "地天泰": "小往大来，吉亨。",
    "天地否": "否之匪人，不利君子贞，大往小来。",
    "天火同人": "同人于野，亨。利涉大川，利君子贞。",
    "火天大有": "元亨。",
    "地山谦": "亨，君子有终。",
    "雷地豫": "利建侯行师。",
    "泽雷随": "元亨利贞，无咎。",
    "山风蛊": "元亨，利涉大川。先甲三日，后甲三日。",
    "地泽临": "元亨利贞。至于八月有凶。",
    "风地观": "盥而不荐，有孚颙若。",
    "火雷噬嗑": "亨。利用狱。",
    "山火贲": "亨。小利有攸往。",
    "山地剥": "不利有攸往。",
    "地雷复": "亨。出入无疾，朋来无咎。反复其道，七日来复，利有攸往。",
    "天雷无妄": "元亨利贞。其匪正有眚，不利有攸往。",
    "山天大畜": "利贞，不家食吉，利涉大川。",
    "山雷颐": "贞吉。观颐，自求口实。",
    "泽风大过": "栋桡，利有攸往，亨。",
    "坎为水": "习坎，有孚，维心亨，行有尚。",
    "离为火": "利贞，亨。畜牝牛，吉。",
    "泽山咸": "亨，利贞，取女吉。",
    "雷风恒": "亨，无咎，利贞，利有攸往。",
    "天山遁": "亨，小利贞。",
    "雷天大壮": "利贞。",
    "火地晋": "康侯用锡马蕃庶，昼日三接。",
    "地火明夷": "利艰贞。",
    "风火家人": "利女贞。",
    "火泽睽": "小事吉。",
    "水山蹇": "利西南，不利东北。利见大人，贞吉。",
    "雷水解": "利西南，无所往，其来复吉。有攸往，夙吉。",
    "山泽损": "有孚，元吉，无咎，可贞，利有攸往。",
    "风雷益": "利有攸往，利涉大川。",
    "泽天夬": "扬于王庭，孚号有厉，告自邑，不利即戎，利有攸往。",
    "天风姤": "女壮，勿用取女。",
    "泽地萃": "亨。王假有庙，利见大人，亨，利贞。",
    "地风升": "元亨，用见大人，勿恤，南征吉。",
    "泽水困": "亨，贞，大人吉，无咎，有言不信。",
    "水风井": "改邑不改井，无丧无得，往来井井。",
    "泽火革": "己日乃孚，元亨利贞，悔亡。",
    "火风鼎": "元吉，亨。",
    "震为雷": "亨。震来虩虩，笑言哑哑。",
    "艮为山": "艮其背，不获其身，行其庭，不见其人，无咎。",
    "风山渐": "女归吉，利贞。",
    "雷泽归妹": "征凶，无攸利。",
    "雷火丰": "亨，王假之，勿忧，宜日中。",
    "火山旅": "小亨，旅贞吉。",
    "巽为风": "小亨，利有攸往，利见大人。",
    "兑为泽": "亨，利贞。",
    "风水涣": "亨。王假有庙，利涉大川，利贞。",
    "水泽节": "亨。苦节不可贞。",
    "风泽中孚": "豚鱼吉，利涉大川，利贞。",
    "雷山小过": "亨，利贞，可小事，不可大事。飞鸟遗之音，不宜上宜下，大吉。",
    "水火既济": "亨，小利贞，初吉终乱。",
    "火水未济": "亨，小狐汔济，濡其尾，无攸利。",
}


def yarrow_stalk_yao() -> int:
    """
    大衍筮法模拟（一爻）
    50根蓍草去1，49根分二、挂一、揲四、归奇，三变得一爻。
    概率分布：老阴(6)=1/16, 少阳(7)=5/16, 少阴(8)=7/16, 老阳(9)=3/16
    """
    total = 49
    result_sum = 0

    for bian in range(3):  # 三变
        # 分二：随机分为左右两堆
        left = random.randint(1, total - 1)
        right = total - left

        # 挂一：从右手取一根夹于左手小指间
        right -= 1
        gua = 1

        # 揲四：左手每次取4根
        left_remainder = left % 4 or 4
        right_remainder = right % 4 or 4

        # 归奇：把余数和挂一合并
        removed = left_remainder + right_remainder + gua

        total = total - removed

    # 三变后剩余数 / 4 = 爻值
    yao = total // 4
    # 6=老阴, 7=少阳, 8=少阴, 9=老阳
    return yao


def three_coins_yao() -> int:
    """
    三枚硬币法模拟（一爻）
    字=2, 背=3，三枚之和：
    6(三字)=老阴, 7(两字一背)=少阳, 8(一字两背)=少阴, 9(三背)=老阳
    概率分布：老阴=1/8, 少阳=3/8, 少阴=3/8, 老阳=1/8
    """
    coins = [random.choice([2, 3]) for _ in range(3)]
    return sum(coins)


def cast_hexagram(method: str = "coins") -> list[int]:
    """
    起卦：生成六爻
    method: "yarrow"(蓍草法) 或 "coins"(硬币法)
    返回：[初爻, 二爻, 三爻, 四爻, 五爻, 上爻] 的列表，值为6/7/8/9
    """
    func = yarrow_stalk_yao if method == "yarrow" else three_coins_yao
    return [func() for _ in range(6)]


def yaos_to_trigram(yaos: list[int]) -> tuple:
    """三爻转八卦元组"""
    return tuple(YAO_TYPES[y]["value"] for y in yaos)


def get_hexagram_name(yaos: list[int]) -> str:
    """从六爻获取卦名"""
    lower = yaos_to_trigram(yaos[:3])  # 下卦（内卦）
    upper = yaos_to_trigram(yaos[3:])  # 上卦（外卦）

    upper_idx = BAGUA_ORDER.get(upper, 0)
    lower_idx = BAGUA_ORDER.get(lower, 0)

    return GUA_NAMES[upper_idx][lower_idx]


def get_changed_hexagram(yaos: list[int]) -> tuple[str, list[int]]:
    """获取变卦（动爻变化后的卦）"""
    changed = []
    for y in yaos:
        if y == 9:  # 老阳变阴
            changed.append(8)
        elif y == 6:  # 老阴变阳
            changed.append(7)
        else:
            changed.append(y)
    return get_hexagram_name(changed), changed


def divine(method: str = "coins") -> dict:
    """
    完整占卦流程
    返回本卦、变卦、动爻等信息
    """
    yaos = cast_hexagram(method)

    # 本卦
    ben_gua = get_hexagram_name(yaos)

    # 动爻
    dong_yao = [i + 1 for i, y in enumerate(yaos) if YAO_TYPES[y]["changes"]]

    # 变卦
    bian_gua = None
    if dong_yao:
        bian_gua, _ = get_changed_hexagram(yaos)

    # 上下卦信息
    lower = yaos_to_trigram(yaos[:3])
    upper = yaos_to_trigram(yaos[3:])
    lower_info = BAGUA.get(lower, {})
    upper_info = BAGUA.get(upper, {})

    return {
        "method": "大衍筮法（蓍草）" if method == "yarrow" else "三枚硬币法",
        "六爻": yaos,
        "本卦": ben_gua,
        "变卦": bian_gua,
        "动爻": dong_yao,
        "卦辞": GUA_CI.get(ben_gua, ""),
        "下卦": lower_info.get("name", "?") + "（" + lower_info.get("nature", "") + "）",
        "上卦": upper_info.get("name", "?") + "（" + upper_info.get("nature", "") + "）",
    }


def display(result: dict):
    """格式化显示卦象"""
    print("\n" + "═" * 50)
    print(f"  易经占卦 · {result['method']}")
    print("═" * 50)

    # 画卦象
    print("\n  卦象（从上到下）：\n")
    yao_names = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
    for i in range(5, -1, -1):
        y = result["六爻"][i]
        info = YAO_TYPES[y]
        dong = " ←动" if info["changes"] else ""
        print(f"    {yao_names[i]}  {info['symbol']}  {info['name']}{dong}")

    print(f"\n  上卦：{result['上卦']}")
    print(f"  下卦：{result['下卦']}")
    print(f"\n  ┌──────────────────────────────────┐")
    print(f"  │  本卦：{result['本卦']}")
    if result["卦辞"]:
        print(f"  │  卦辞：{result['卦辞']}")
    if result["动爻"]:
        dong_str = "、".join(f"第{d}爻" for d in result["动爻"])
        print(f"  │  动爻：{dong_str}")
    if result["变卦"]:
        print(f"  │  变卦：{result['变卦']}")
        bian_ci = GUA_CI.get(result["变卦"], "")
        if bian_ci:
            print(f"  │  变卦辞：{bian_ci}")
    else:
        print(f"  │  无动爻，卦象静止。")
    print(f"  └──────────────────────────────────┘")
    print()


def probability_comparison(n: int = 10000):
    """比较两种起卦法的概率分布差异"""
    print(f"\n  ── 概率分布比较（{n}次模拟） ──\n")

    for method, label in [("yarrow", "蓍草法"), ("coins", "硬币法")]:
        counts = {6: 0, 7: 0, 8: 0, 9: 0}
        for _ in range(n):
            func = yarrow_stalk_yao if method == "yarrow" else three_coins_yao
            y = func()
            counts[y] += 1

        print(f"  {label}：")
        theory = {"yarrow": {6: 1/16, 7: 5/16, 8: 7/16, 9: 3/16},
                  "coins": {6: 1/8, 7: 3/8, 8: 3/8, 9: 1/8}}
        for val in [6, 7, 8, 9]:
            pct = counts[val] / n * 100
            th = theory[method][val] * 100
            name = YAO_TYPES[val]["name"]
            bar = "█" * int(pct / 2)
            print(f"    {name}({val}): {pct:5.1f}% (理论{th:5.1f}%) {bar}")
        print()


def interactive():
    """交互式易经占卦"""
    print("\n╔══════════════════════════════════════╗")
    print("║   易经占卦 · 周易                   ║")
    print("║   I Ching Divination                 ║")
    print("╚══════════════════════════════════════╝")
    print("\n  2⁶ = 64卦，六爻二进制编码系统。")
    print("  ⚠️ 本程序忠实复现起卦算法，不代表认同其预测效力。\n")

    print("  起卦方法：")
    print("    1. 三枚硬币法（概率均匀）")
    print("    2. 大衍筮法 / 蓍草法（概率不均匀）")
    print("    3. 概率分布比较（模拟10000次）")

    try:
        choice = input("\n  请选择（1/2/3）：").strip()
    except EOFError:
        return

    if choice == "3":
        probability_comparison()
        return

    method = "yarrow" if choice == "2" else "coins"
    result = divine(method)
    display(result)


if __name__ == "__main__":
    interactive()
