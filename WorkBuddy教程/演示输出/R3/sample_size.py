# -*- coding: utf-8 -*-
"""
R3 教学样本量计算（正态近似）
⚠️ 全部参数为教学假设，仅用于课堂演示，不可用于任何真实研究的样本量确定。

主算例：两组率比较，统一采用【合并方差正态近似】（Pooled），不混用其他近似作主结果：
    n/组 = [ z_{1-α/2} * sqrt(2*pbar*(1-pbar)) + z_{1-β} * sqrt(p1*(1-p1)+p2*(1-p2)) ]^2 / (p1-p2)^2
    其中 pbar = (p1+p2)/2（等分组合并率）
    向上取整两次，顺序固定：先对 n 向上取整，再对脱落调整后的人数向上取整。

z 值由 norm_ppf(alpha, power) 从参数计算，不硬编码。

连续型主要结局（6 个月收缩压）：效应量 δ 与标准差 SD 待课堂确认，确认前不计算样本量。

补充说明（非主结果）：未合并方差公式 n/组 = (z_a+z_b)^2 * [p1(1-p1)+p2(1-p2)] / (p1-p2)^2
"""

import math

# ---------------- 教学假设参数 ----------------
P1 = 0.40          # 对照组率（教学假设）
P2_NEW = 0.50      # 干预组率（新设定，教学假设）
P2_OLD = 0.55      # 干预组率（原设定，用于对照）
ALPHA = 0.05       # 双侧检验水准（教学假设）
POWER = 0.80       # 把握度 1-β（教学假设）
DROPOUT = 0.15     # 脱落率（教学假设）

# ---------------- 标准正态分位数（由参数计算，不硬编码） ----------------
def norm_ppf(p):
    """标准正态分布分位数，二分法，无 scipy 依赖。"""
    lo, hi = -10.0, 10.0
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if 0.5 * (1.0 + math.erf(mid / math.sqrt(2.0))) < p:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def z_values(alpha, power):
    """从 alpha、power 参数计算两个 z 值。"""
    return norm_ppf(1 - alpha / 2.0), norm_ppf(power)


# ---------------- 主算例：合并方差正态近似 ----------------
def n_pooled(p1, p2, alpha=ALPHA, power=POWER):
    z_a, z_b = z_values(alpha, power)
    pbar = (p1 + p2) / 2.0
    numerator = (z_a * math.sqrt(2 * pbar * (1 - pbar))
                 + z_b * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
    return numerator / (p1 - p2) ** 2


def report(tag, p1, p2, alpha=ALPHA, power=POWER, dropout=DROPOUT):
    """按固定顺序两次向上取整：先 n，再脱落调整。"""
    z_a, z_b = z_values(alpha, power)
    n_raw = n_pooled(p1, p2, alpha, power)
    n_up = math.ceil(n_raw)                 # 第一次取整：样本量 n
    n_adj = math.ceil(n_up / (1 - dropout))  # 第二次取整：脱落调整
    print(f"[{tag}] p1={p1}, p2={p2}, |Δ|={abs(p1 - p2):.2f}")
    print(f"  z_(1-alpha/2)={z_a:.6f}, z_(1-beta)={z_b:.6f}（由 alpha={alpha}, power={power} 参数计算）")
    print(f"  合并方差公式 n/组 = {n_raw:.4f}")
    print(f"  第一次向上取整: {n_up} 人/组")
    print(f"  脱落 {dropout:.0%} 调整: {n_up} / {1 - dropout} = {n_up / (1 - dropout):.4f}"
          f" -> 第二次向上取整 {n_adj} 人/组（两组合计 {2 * n_adj}）\n")
    return {"tag": tag, "p1": p1, "p2": p2, "delta": p1 - p2,
            "n_raw": n_raw, "n_up": n_up, "n_adj": n_adj}


print("=" * 60)
print("主算例（合并方差正态近似，两次向上取整：先 n 再脱落）")
print("=" * 60)
old = report("原设定（对照）", P1, P2_OLD)
new = report("新设定（主算例）", P1, P2_NEW)

# ---------------- 敏感性表：干预组率变动 ----------------
print("=" * 60)
print(f"敏感性表（p1={P1} 固定，p2 变动；alpha={ALPHA}, power={POWER}, 脱落={DROPOUT:.0%}）")
print("=" * 60)
print(f"{'p2':>6} | {'Δ':>6} | {'n/组(原始)':>12} | {'n/组(取整)':>10} | {'含脱落 n/组':>10} | {'合计':>6}")
print("-" * 60)
sens = []
for p2 in [0.45, 0.50, 0.55, 0.60]:
    n_raw = n_pooled(P1, p2)
    n_up = math.ceil(n_raw)
    n_adj = math.ceil(n_up / (1 - DROPOUT))
    sens.append((p2, abs(P1 - p2), n_raw, n_up, n_adj))
    print(f"{p2:>6.2f} | {abs(P1 - p2):>6.2f} | {n_raw:>12.4f} | {n_up:>10d} | {n_adj:>10d} | {2 * n_adj:>6d}")

# ---------------- 补充说明：未合并方差公式（非主结果） ----------------
print()
print("=" * 60)
print("补充说明：未合并方差公式（仅作对照，不作为主结果）")
print("=" * 60)
z_a, z_b = z_values(ALPHA, POWER)
for tag, p1, p2 in [("原设定", P1, P2_OLD), ("新设定", P1, P2_NEW)]:
    n_unpooled = (z_a + z_b) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p1 - p2) ** 2
    print(f"[{tag}] 未合并公式 n/组 = {n_unpooled:.4f} -> {math.ceil(n_unpooled)}"
          f" -> 含脱落 {math.ceil(math.ceil(n_unpooled) / (1 - DROPOUT))} 人/组")

# ---------------- 连续型主要结局：待确认，不计算 ----------------
print()
print("连续型主要结局（6 个月收缩压）：δ 与 SD 待课堂确认，确认前不计算样本量。")
print("公式（供确认后使用）：n/组 = 2 * (z_(1-alpha/2) + z_(1-beta))^2 * SD^2 / delta^2")
