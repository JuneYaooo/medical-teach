# -*- coding: utf-8 -*-
"""
家庭血压自测支持社区试验 —— 样本量计算（两独立样本均数比较）

设计参数（全部为规划假设，状态=待确认，见《样本量参数来源表.md》）：
  - 主要结局：6 个月诊室收缩压（mmHg）
  - 检验：两独立样本均数比较（双侧），alpha = 0.05，power = 0.80，1:1 分组
  - 预计脱落率 15%（失访 + 关键结局缺失），据此做样本膨胀

固定算法（不得更改顺序）：
  1) 每臂原始样本量 n_raw = 2 * (z_{1-alpha/2} + z_{1-beta})^2 * SD^2 / delta^2
  2) 向上取整得每臂整数 n_int = ceil(n_raw)
  3) 按 15% 脱落膨胀：n_final = ceil(n_int / (1 - 0.15))
  4) 总样本量 = 2 * n_final

与主模型的关系：
  主分析为线性回归（ANCOVA 型）：6 个月收缩压 ~ 组别 + 基线收缩压 + 年龄 + 社区。
  在简化假设下（残差近似正态、方差齐、协变量与组别近似独立），若基线收缩压与
  结局的相关为 r，调整后的残差方差约为 SD^2*(1-r^2)，残差标准差约为 SD*sqrt(1-r^2)；
  若按调整模型直接测算，样本量近似乘以折减因子 (1-r^2)（不是其倒数）。
  本次计算仍按未调整的两独立样本模型做资源规划：折减因子取决于实际 r（未知），
  且协变量与组别的实际相关会改变有效方差的构成，故本计算不能保证对所有实际情形
  都保守；纵向参数（结局 SD、基线—结局相关、效应量）需既有配对数据或另行完成
  随访后实测，短期核实无法替代。

运行：python3 sample_size.py   （仅依赖 Python 标准库）
"""

import math
from statistics import NormalDist

ALPHA = 0.05          # 双侧
POWER = 0.80          # 1 - beta
DROPOUT = 0.15        # 预计脱落率（失访/主要结局缺失）
DELTAS = [3, 4, 5]    # 组间差假设（mmHg），来源与状态见参数来源表
SDS = [12, 15, 18]    # 标准差假设（mmHg），来源与状态见参数来源表


def z_values(alpha: float, power: float) -> tuple[float, float]:
    """双侧检验的 z_{1-alpha/2} 与 z_{1-beta}。"""
    nd = NormalDist()
    z_alpha = nd.inv_cdf(1 - alpha / 2)
    z_beta = nd.inv_cdf(power)
    return z_alpha, z_beta


def n_per_arm(delta: float, sd: float,
              alpha: float = ALPHA, power: float = POWER,
              dropout: float = DROPOUT) -> dict:
    """按固定顺序计算每臂样本量。"""
    z_a, z_b = z_values(alpha, power)
    n_raw = 2 * (z_a + z_b) ** 2 * sd ** 2 / delta ** 2   # 第1步：原始值
    n_int = math.ceil(n_raw)                              # 第2步：先取整
    n_final = math.ceil(n_int / (1 - dropout))            # 第3步：再按脱落膨胀
    return {"n_raw": n_raw, "n_int": n_int,
            "n_final": n_final, "total": 2 * n_final}


def main() -> None:
    z_a, z_b = z_values(ALPHA, POWER)
    print(f"双侧 alpha={ALPHA}，power={POWER}，1:1 分组，脱落率 {DROPOUT:.0%}")
    print(f"z_(1-a/2)={z_a:.4f}，z_(1-b)={z_b:.4f}")
    print()
    print("敏感性矩阵（行=组间差 delta mmHg，列=标准差 SD mmHg；每臂例数/总例数）")
    header = "| 组间差\\SD | " + " | ".join(f"{sd} mmHg" for sd in SDS) + " |"
    sep = "|---" * (len(SDS) + 1) + "|"
    print(header)
    print(sep)
    for d in DELTAS:
        cells = []
        for sd in SDS:
            r = n_per_arm(d, sd)
            cells.append(f"{r['n_final']}/臂，共{r['total']}")
        print(f"| {d} mmHg | " + " | ".join(cells) + " |")
    print()
    print("明细（n_raw 原始值 → n_int 取整后每臂 → n_final 脱落膨胀后每臂 / 总例数）")
    for d in DELTAS:
        for sd in SDS:
            r = n_per_arm(d, sd)
            print(f"delta={d}, SD={sd}: n_raw={r['n_raw']:.1f} -> n_int={r['n_int']} "
                  f"-> n_final={r['n_final']} 每臂 / 总计 {r['total']}")


if __name__ == "__main__":
    main()
