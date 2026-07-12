#!/usr/bin/env python3
"""
谶纬流变 · 占卜推演引擎集
Comparative Mantology - Interactive Divination Engines

跨越七大文明区域的14种占卜/预测方法的程序化实现。
每种方法忠实复现其推演算法，不代表认同其预测效力。

作者：李平江
"""

import sys

MENU = """
╔══════════════════════════════════════════════════════╗
║       谶 纬 流 变 · 占 卜 推 演 引 擎 集           ║
║       Comparative Mantology Engines                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  ─── A档：确定性算法（输入→唯一输出）───            ║
║                                                      ║
║   1. 八字命理 · 四柱推命         (中国)              ║
║   2. 紫微斗数 · 排盘             (中国)              ║
║   3. 数秘术 · Numerology         (希腊/全球)         ║
║   4. 生肖相合 · 十二属相         (中国)              ║
║   5. 血型性格 · 血液型判断       (日本)              ║
║                                                      ║
║  ─── B档：概率性算法（含随机元素）───                ║
║                                                      ║
║   6. 易经占卦 · 蓍草法/硬币法   (中国)  2⁶=64       ║
║   7. 塔罗牌 · Tarot              (欧洲)  78张       ║
║   8. 沙占 · Geomancy             (阿拉伯) 2⁴=16    ║
║   9. Ifá占卜 · 约鲁巴            (西非)  2⁸=256    ║
║  10. 签诗 · 庙签 · 求签          (中国/日本)        ║
║  11. 奇门遁甲 · 布盘             (中国)             ║
║  12. 风水八宅法                   (中国)             ║
║  13. 阴阳道 · 方違え             (日本)             ║
║                                                      ║
║   0. 退出                                            ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
"""

BINARY_NOTE = """
  ┌─────────────────────────────────────────────┐
  │  跨文明二进制占卜家族：                     │
  │    沙占    2⁴ = 16 种图形  （阿拉伯/非洲） │
  │    易经    2⁶ = 64 卦      （中国）         │
  │    Ifá     2⁸ = 256 Odù    （西非约鲁巴）   │
  │  三个独立发展的系统，不约而同的二进制编码。  │
  └─────────────────────────────────────────────┘
"""


def run_engine(choice: str):
    """运行对应的占卜引擎"""
    try:
        if choice == "1":
            from engines.bazi import interactive
            interactive()
        elif choice == "2":
            from engines.ziwei import interactive
            interactive()
        elif choice == "3":
            from engines.numerology import interactive
            interactive()
        elif choice == "4":
            from engines.zodiac import interactive
            interactive()
        elif choice == "5":
            from engines.blood_type import interactive
            interactive()
        elif choice == "6":
            from engines.yijing import interactive
            interactive()
        elif choice == "7":
            from engines.tarot import interactive
            interactive()
        elif choice == "8":
            from engines.geomancy import interactive
            interactive()
        elif choice == "9":
            from engines.ifa import interactive
            interactive()
        elif choice == "10":
            from engines.qianshi import interactive
            interactive()
        elif choice == "11":
            from engines.qimen import interactive
            interactive()
        elif choice == "12":
            from engines.bazhai import interactive
            interactive()
        elif choice == "13":
            from engines.onmyodo import interactive
            interactive()
        else:
            print("  无效选择。")
    except KeyboardInterrupt:
        print("\n  已中断。")
    except Exception as e:
        print(f"\n  运行出错：{e}")


def main():
    """主循环"""
    print(BINARY_NOTE)

    while True:
        print(MENU)
        try:
            choice = input("  请选择（0-13）：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n  再见！")
            break

        if choice == "0":
            print("\n  再见！谶纬流变，见微知著。")
            break

        run_engine(choice)

        try:
            input("\n  按回车返回主菜单...")
        except (EOFError, KeyboardInterrupt):
            break


if __name__ == "__main__":
    main()
