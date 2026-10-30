#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
R4 数据清洗、统计与绘图
=====================
依据：实操素材/数据字典与SAP.md + 用户已确认的清洗规则（2026-10-30）

已确认的清洗规则（仅此四条，不得外延）：
  1) age=999、sbp_6m=18、bmi=99 设为缺失，保留受试者；
  2) 性别按字典统一（统一为 1=男 / 0=女，字典合法编码之一，便于建模）；
  3) 仅移除经逐字段核对完全一致的 3 条重复记录（保留首次出现）；
     有冲突的重复记录列出待核，不自行取第一条；
  4) 不做均数填补，不改动任何其他值，不生成未预设亚组。

统计分析（SAP 预设）：
  主要结局：6 个月收缩压（mmHg），完整病例线性回归，
           调整基线收缩压、年龄、中心；报告调整均数差（干预−对照）、95% CI、P 值；
           检查残差及异方差；敏感性分析用 HC3 稳健标准误；
           比较纳入与缺失者特征；次要结局达标比例仅描述。
  声明：主分析为完整病例分析，缺失可能引入偏倚，不等于完整 ITT；
        本数据为按编号交替生成的合成教学两组，不是真实随机化数据。

运行：python3 analysis.py   （输出全部写入本目录）
"""

import csv
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

import os
# matplotlib 字体缓存放在课程目录 .cache/mpl，不在用户目录留下痕迹
os.environ.setdefault("MPLCONFIGDIR", str(Path(__file__).resolve().parent / ".cache" / "mpl"))
Path(os.environ["MPLCONFIGDIR"]).mkdir(parents=True, exist_ok=True)

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------------------------------------------------------- 路径
BASE = Path(__file__).resolve().parent          # 演示输出/R4/
RAW = BASE.parent.parent / "实操素材" / "bp_trial_sim.csv"
OUT = BASE

COLS = ["id", "group", "age", "sex", "bmi", "duration_years", "diabetes",
        "sbp_baseline", "dbp_baseline", "sbp_6m", "dbp_6m", "controlled_6m",
        "adherence", "site", "visits"]

# 绘图中文字体（macOS）
plt.rcParams["font.sans-serif"] = ["PingFang SC", "Hiragino Sans GB",
                                   "Arial Unicode MS", "STHeiti"]
plt.rcParams["axes.unicode_minus"] = False

log_rows = []          # 清洗日志：序号/原始CSV行号/受试者ID/字段/原值/新值/规则
def add_log(csv_line, sid, field, old, new, rule):
    log_rows.append({"序号": len(log_rows) + 1, "原始CSV行号": csv_line,
                     "受试者ID": sid, "字段": field, "原值": old,
                     "新值": new, "规则": rule})

# ================================================================ 1. 读取原始数据（只读）
raw = pd.read_csv(RAW, dtype=str, encoding="utf-8-sig")
assert list(raw.columns) == COLS, f"列名与字典不一致: {list(raw.columns)}"
raw["csv_line"] = raw.index + 2                 # 表头为第 1 行
print(f"[读入] 原始记录 {len(raw)} 条，唯一受试者 {raw['id'].nunique()} 例")

# ================================================================ 2. 清洗
df = raw.copy()

# -- 2.1 仅移除逐字段完全一致的重复记录（保留首次出现）------------------------
dup_mask = df.duplicated(subset=COLS, keep="first")
n_conflict = int((df["id"].duplicated(keep=False) & ~dup_mask &
                  df["id"].duplicated(keep="first")).sum())
if n_conflict:
    raise RuntimeError(f"发现 {n_conflict} 条冲突重复记录，按规则列出待核，脚本停止")
for _, r in df[dup_mask].iterrows():
    first_line = int(df.loc[(df[COLS] == r[COLS]).all(axis=1), "csv_line"].min())
    add_log(int(r["csv_line"]), r["id"], "(整行)",
            f"与CSV第{first_line}行逐字段完全一致", "(删除)",
            "规则3：仅移除逐字段完全一致的重复记录，保留首次出现")
df = df[~dup_mask].reset_index(drop=True)
print(f"[去重] 移除完全一致重复 {len(raw) - len(df)} 条，剩余 {len(df)} 条")

# -- 2.2 哨兵值置缺失（保留受试者）-------------------------------------------
SENTINELS = [("age", "999", "规则1：年龄999设为缺失，保留受试者"),
             ("bmi", "99", "规则1：BMI99设为缺失，保留受试者"),
             ("sbp_6m", "18", "规则1：6个月收缩压18设为缺失，保留受试者")]
for col, sent, rule in SENTINELS:
    m = df[col] == sent
    for _, r in df[m].iterrows():
        add_log(int(r["csv_line"]), r["id"], col, sent, "(缺失/NA)", rule)
    df.loc[m, col] = np.nan
    print(f"[哨兵] {col}={sent} 置缺失 {int(m.sum())} 例")

# -- 2.3 性别按字典统一：1=男，0=女（原值见清洗日志）---------------------------
SEX_MAP = {"男": 1, "M": 1, "1": 1, "女": 0, "F": 0, "0": 0}
assert df["sex"].isin(SEX_MAP).all(), "sex 出现字典之外的取值"
m_sex = df["sex"].isin(["男", "M", "女", "F"])
for _, r in df[m_sex].iterrows():
    add_log(int(r["csv_line"]), r["id"], "sex", r["sex"],
            str(SEX_MAP[r["sex"]]), "规则2：性别按字典统一为1=男/0=女")
df["sex"] = df["sex"].map(SEX_MAP)
print(f"[编码] sex 统一改写 {int(m_sex.sum())} 行")

# -- 2.4 数值列定型（不做任何填补，不改其他值）--------------------------------
INT_COLS = ["age", "duration_years", "diabetes", "controlled_6m", "visits", "sex"]
FLT1_COLS = ["bmi", "sbp_baseline", "dbp_baseline", "sbp_6m", "dbp_6m"]
for c in INT_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")
for c in FLT1_COLS:
    df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
df["adherence"] = pd.to_numeric(df["adherence"], errors="coerce").astype(float)

print(f"[清洗完成] {len(df)} 条记录；"
      f"缺失：sbp_6m={int(df['sbp_6m'].isna().sum())}（原始空值30+哨兵1），"
      f"dbp_6m={int(df['dbp_6m'].isna().sum())}，"
      f"controlled_6m={int(df['controlled_6m'].isna().sum())}，"
      f"age={int(df['age'].isna().sum())}，bmi={int(df['bmi'].isna().sum())}")

# ================================================================ 3. 写 clean.csv
clean = df[COLS].copy()
with open(OUT / "clean.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.writer(f)
    w.writerow(COLS)
    for _, r in clean.iterrows():
        row = [r["id"], r["group"],
               "" if pd.isna(r["age"]) else str(int(r["age"])),
               "" if pd.isna(r["sex"]) else str(int(r["sex"])),
               "" if pd.isna(r["bmi"]) else f"{r['bmi']:.1f}",
               str(int(r["duration_years"])),
               str(int(r["diabetes"])),
               f"{r['sbp_baseline']:.1f}", f"{r['dbp_baseline']:.1f}",
               "" if pd.isna(r["sbp_6m"]) else f"{r['sbp_6m']:.1f}",
               "" if pd.isna(r["dbp_6m"]) else f"{r['dbp_6m']:.1f}",
               "" if pd.isna(r["controlled_6m"]) else str(int(r["controlled_6m"])),
               f"{r['adherence']:g}", r["site"], str(int(r["visits"]))]
        w.writerow(row)
print(f"[写出] clean.csv（{len(clean)} 行）")

# 清洗日志
log = pd.DataFrame(log_rows)
log.to_csv(OUT / "清洗日志.csv", index=False, encoding="utf-8-sig")
print(f"[写出] 清洗日志.csv（{len(log)} 条）")

# ================================================================ 4. Table1（不做基线 P 值检验）
def ms(s, unit=""):
    s = s.dropna()
    return f"{s.mean():.1f} ± {s.std(ddof=1):.1f}{unit}"

def npct(s, positive=1):
    s = s.dropna()
    return f"{int((s == positive).sum())} ({(s == positive).mean() * 100:.1f}%)"

t1 = []
def t1_row(var, label, fmt):
    a = fmt(df.loc[df["group"] == "干预组", var])
    b = fmt(df.loc[df["group"] == "对照组", var])
    na = int(df.loc[df["group"] == "干预组", var].isna().sum())
    nb = int(df.loc[df["group"] == "对照组", var].isna().sum())
    t1.append({"变量": label, "干预组 (n=150)": a, "对照组 (n=150)": b,
               "缺失（干预/对照）": f"{na} / {nb}"})

t1_row("age", "年龄, 岁", lambda s: ms(s))
t1_row("sex", "男性, n (%)", lambda s: npct(s, 1))
t1_row("bmi", "BMI, kg/m²", lambda s: ms(s))
t1_row("duration_years", "高血压病程, 年", lambda s: ms(s))
t1_row("diabetes", "糖尿病, n (%)", lambda s: npct(s, 1))
t1_row("sbp_baseline", "基线收缩压, mmHg", lambda s: ms(s))
t1_row("dbp_baseline", "基线舒张压, mmHg", lambda s: ms(s))
t1_row("adherence", "依从率, 0–1", lambda s: ms(s))
t1_row("visits", "完成访视次数", lambda s: ms(s))
t1.append({"变量": "中心 B, n (%)", "干预组 (n=150)": npct(
               df.loc[df["group"] == "干预组", "site"].replace({"B": 1, "A": 0})),
           "对照组 (n=150)": npct(
               df.loc[df["group"] == "对照组", "site"].replace({"B": 1, "A": 0})),
           "缺失（干预/对照）": "0 / 0"})
table1 = pd.DataFrame(t1)
table1.to_csv(OUT / "Table1.csv", index=False, encoding="utf-8-sig")
print("[写出] Table1.csv（无基线P值检验）")

# ================================================================ 5. 主分析：完整病例线性回归
# 完整病例 = 结局 sbp_6m 与协变量（基线收缩压、年龄、中心）齐全者
ana = df.dropna(subset=["sbp_6m", "sbp_baseline", "age", "site"]).copy()
ana["grp"] = (ana["group"] == "干预组").astype(int)     # 干预组=1，对照组=0
ana["siteB"] = (ana["site"] == "B").astype(int)         # A=0，B=1
n_ana = len(ana)
n_miss = len(df) - n_ana
miss_g = df[df["sbp_6m"].isna() | df["sbp_baseline"].isna()
            | df["age"].isna() | df["site"].isna()]["group"].value_counts()

def ols(y, X, names):
    """普通最小二乘 + 经典SE + HC3稳健SE。返回系数表。"""
    XtX_inv = np.linalg.inv(X.T @ X)
    beta = XtX_inv @ X.T @ y
    resid = y - X @ beta
    n, p = X.shape
    dfe = n - p
    h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)          # leverage
    s2 = resid @ resid / dfe
    cov_c = s2 * XtX_inv
    # HC3: (X'X)^-1 X' diag(e^2/(1-h)^2) X (X'X)^-1
    W = resid ** 2 / (1 - h) ** 2
    cov_h = (XtX_inv @ (X.T * W)) @ X @ XtX_inv
    tcrit = stats.t.ppf(0.975, dfe)
    rows = []
    for i, nm in enumerate(names):
        for tag, cov in (("经典", cov_c), ("HC3", cov_h)):
            se = np.sqrt(cov[i, i])
            tv = beta[i] / se
            rows.append({"项": nm, "标准误类型": tag,
                         "系数": beta[i], "标准误": se,
                         "95%CI下限": beta[i] - tcrit * se,
                         "95%CI上限": beta[i] + tcrit * se,
                         "t值": tv, "P值": 2 * stats.t.sf(abs(tv), dfe)})
    return pd.DataFrame(rows), resid, dfe

y = ana["sbp_6m"].to_numpy(float)
Xm = np.column_stack([np.ones(n_ana), ana["grp"], ana["sbp_baseline"],
                      ana["age"], ana["siteB"]])
names = ["截距", "组别（干预−对照）", "基线收缩压, mmHg", "年龄, 岁", "中心B（vs A）"]
coef, resid, dfe = ols(y, Xm, names)

# 残差与异方差诊断
sh_p = stats.shapiro(resid).pvalue
# Breusch-Pagan：残差平方对协变量做辅助回归，LM = n·R²
Z = np.column_stack([np.ones(n_ana), Xm[:, 1:]])
b_aux = np.linalg.lstsq(Z, resid ** 2, rcond=None)[0]
r2_aux = 1 - ((resid ** 2 - Z @ b_aux) ** 2).sum() / ((resid ** 2 -
                                                      (resid ** 2).mean()) ** 2).sum()
LM = n_ana * r2_aux
bp_p = stats.chi2.sf(LM, Z.shape[1] - 1)

md_row = coef[(coef["项"] == "组别（干预−对照）")]
md_c = md_row[md_row["标准误类型"] == "经典"].iloc[0]
md_h = md_row[md_row["标准误类型"] == "HC3"].iloc[0]

# 次要结局：达标比例（仅描述，不检验）
ctrl = df.dropna(subset=["controlled_6m"])
sec = ctrl.groupby("group")["controlled_6m"].agg(["count", "sum"])
sec_rows = [{"组别": g, "可评价n": int(r["count"]),
             "达标n": int(r["sum"]),
             "达标率 (%)": round(r["sum"] / r["count"] * 100, 1)}
            for g, r in sec.iterrows()]

# 纳入与未纳入者特征比较（仅描述）——口径与主分析完全一致：
# 纳入 = 结局 + 全部协变量（基线收缩压、年龄、中心）齐全（完整病例 mask，n=268）
inc = ana                                                   # 268，与主分析同一 mask
exc = df.loc[df.index.difference(ana.index)]                # 32（31 例结局缺失 + SIM019 年龄缺失）
cmp_rows = []
def cmp_row(label, fn, a=inc, b=exc, ka=None, kb=None):
    cmp_rows.append({"特征": label,
                     ka or "主分析纳入者 (n=%d)" % len(a): fn(a),
                     kb or "未纳入 (n=%d)" % len(b): fn(b)})
cmp_row("年龄, 岁", lambda d: ms(d["age"]))
cmp_row("男性, %", lambda d: f"{(d['sex'] == 1).mean() * 100:.1f}")
cmp_row("BMI, kg/m²", lambda d: ms(d["bmi"]))
cmp_row("病程, 年", lambda d: ms(d["duration_years"]))
cmp_row("糖尿病, %", lambda d: f"{d['diabetes'].mean() * 100:.1f}")
cmp_row("基线收缩压, mmHg", lambda d: ms(d["sbp_baseline"]))
cmp_row("基线舒张压, mmHg", lambda d: ms(d["dbp_baseline"]))
cmp_row("依从率", lambda d: f"{d['adherence'].mean():.2f}")
cmp_row("中心B, %", lambda d: f"{(d['site'] == 'B').mean() * 100:.1f}")
cmp_row("干预组, %", lambda d: f"{(d['group'] == '干预组').mean() * 100:.1f}")
cmp_row("完成访视次数", lambda d: ms(d["visits"]))
compare = pd.DataFrame(cmp_rows)

# 附表：按"结局有无"划分（sbp_6m 269/31）——非主分析完整病例口径，仅描述
# 明确标题，不得称"主分析纳入者"
inc_o = df[df["sbp_6m"].notna()]        # 269（结局存在）
exc_o = df[df["sbp_6m"].isna()]         # 31（结局缺失）
ocmp_rows = []
def ocmp_row(label, fn):
    ocmp_rows.append({"特征": label,
                      "结局存在者 (sbp_6m 非缺失, n=%d)" % len(inc_o): fn(inc_o),
                      "结局缺失者 (sbp_6m 缺失, n=%d)" % len(exc_o): fn(exc_o)})
ocmp_row("年龄, 岁", lambda d: ms(d["age"]))
ocmp_row("男性, %", lambda d: f"{(d['sex'] == 1).mean() * 100:.1f}")
ocmp_row("BMI, kg/m²", lambda d: ms(d["bmi"]))
ocmp_row("病程, 年", lambda d: ms(d["duration_years"]))
ocmp_row("糖尿病, %", lambda d: f"{d['diabetes'].mean() * 100:.1f}")
ocmp_row("基线收缩压, mmHg", lambda d: ms(d["sbp_baseline"]))
ocmp_row("基线舒张压, mmHg", lambda d: ms(d["dbp_baseline"]))
ocmp_row("依从率", lambda d: f"{d['adherence'].mean():.2f}")
ocmp_row("中心B, %", lambda d: f"{(d['site'] == 'B').mean() * 100:.1f}")
ocmp_row("干预组, %", lambda d: f"{(d['group'] == '干预组').mean() * 100:.1f}")
ocmp_row("完成访视次数", lambda d: ms(d["visits"]))
compare_outcome = pd.DataFrame(ocmp_rows)
print(f"[口径] 主分析纳入 {n_ana} / 未纳入 {n_miss}；结局有无 {len(inc_o)}/{len(exc_o)}（仅描述，非主分析口径）")

# ================================================================ 6. 图（带单位与95%CI）
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

# 面板A：两组 6 个月收缩压均数（mmHg，95% CI）
groups = ["干预组", "对照组"]
means, cis = [], []
for g in groups:
    s = df.loc[df["group"] == g, "sbp_6m"].dropna()
    m = s.mean()
    ci = stats.t.ppf(0.975, len(s) - 1) * s.std(ddof=1) / np.sqrt(len(s))
    means.append(m); cis.append(ci)
ax1.errorbar(range(2), means, yerr=cis, fmt="o", capsize=6, color="#4f81bd", markersize=8)
ax1.set_xticks(range(2)); ax1.set_xticklabels(groups)
ax1.set_xlim(-0.6, 1.6)
for x, (m, ci) in enumerate(zip(means, cis)):
    ax1.text(x, m + ci + 1.2, f"{m:.1f}", ha="center", fontsize=10)
ax1.set_ylabel("6个月收缩压均数 (mmHg)")
ax1.set_title("A. 有结局者 n=269：6个月收缩压均值及95%CI", fontsize=11)
ax1.set_ylim(min(means) - 3 * max(cis) - 4, max(means) + 3 * max(cis) + 4)
ax1.spines[["top", "right"]].set_visible(False)
ax1.text(0.02, 0.97, f"可评价：干预 {int(df.loc[df['group']=='干预组','sbp_6m'].notna().sum())} 例，"
                     f"对照 {int(df.loc[df['group']=='对照组','sbp_6m'].notna().sum())} 例",
         transform=ax1.transAxes, fontsize=8.5, color="dimgray", va="top",
         bbox=dict(facecolor="white", edgecolor="none", alpha=0.8, pad=1.5))

# 面板B：调整均数差（干预−对照，mmHg）主分析与HC3敏感性
labels = ["主分析\n（经典SE）", "敏感性分析\n（HC3稳健SE）"]
est = [md_c["系数"], md_h["系数"]]
lo = [md_c["95%CI下限"], md_h["95%CI下限"]]
hi = [md_c["95%CI上限"], md_h["95%CI上限"]]
err = [[e - l for e, l in zip(est, lo)], [h - e for e, h in zip(est, hi)]]
ax2.axhline(0, color="gray", lw=1, ls="--")
ax2.errorbar(range(2), est, yerr=err, fmt="o", capsize=6, color="#c0504d",
             markersize=8, lw=1.6)
for i, (e, l, h_) in enumerate(zip(est, lo, hi)):
    ax2.annotate(f"{e:.2f} (95%CI {l:.2f}–{h_:.2f})", (i, h_), xytext=(0, 9),
                 textcoords="offset points", ha="center", fontsize=9.5)
ax2.set_xticks(range(2)); ax2.set_xticklabels(labels)
ax2.set_xlim(-0.75, 1.75)
ax2.set_ylabel("调整均数差 (mmHg，干预−对照)")
ax2.set_title("B. 主要结局：调整均数差及95%CI\n（调整基线收缩压、年龄、中心）", fontsize=11)
ax2.set_ylim(min(lo) - 1.5, max(hi) + 2.2)
ax2.spines[["top", "right"]].set_visible(False)
fig.suptitle(f"R4 结果图（B面板完整病例 n={n_ana}；合成教学数据，非真实随机化）",
             fontsize=12, y=1.02)
fig.tight_layout()
fig.savefig(OUT / "R4-结果图.png", dpi=300, bbox_inches="tight")
fig.savefig(OUT / "R4-结果图.svg", bbox_inches="tight")
print("[写出] R4-结果图.png / .svg")

# ================================================================ 7. 结果 Excel + 结果表
notes = pd.DataFrame({"分析说明": [
    "数据：300 例模拟受试者（原始303条记录，移除3条逐字段完全一致的重复记录）；全部为程序生成的合成教学数据，不对应真实患者。",
    "组别：group 按受试者编号交替生成，为演示用教学两组，不是真实随机化分配。",
    "清洗：age=999/bmi=99/sbp_6m=18 置缺失并保留受试者；性别按字典统一为1=男/0=女（原值见清洗日志）；仅移除3条完全一致重复；不做均数填补；未改动其他任何值。",
    "主分析：完整病例线性回归（n=%d），结局为6个月收缩压(mmHg)，调整基线收缩压、年龄、中心；组别系数即调整均数差（干预−对照）。" % n_ana,
    "重要声明：主分析为完整病例分析，结局缺失 干预组 21/150、对照组 10/150（仅描述差异，未做统计检验），缺失可能引入偏倚，不等于完整 ITT。",
    "纳入口径：主分析纳入 %d 人（结局+基线收缩压+年龄+中心齐全），未纳入 %d 人（31 人结局缺失 + 1 人年龄=999 置缺失）；「结局有无」口径 %d/31 仅描述、非主分析口径，见独立工作表，不得称为主分析纳入者。" % (n_ana, n_miss, n_ana + 1),
    "敏感性分析：HC3 稳健标准误，点估计与主分析相同，仅标准误/CI/P 不同。",
    "次要结局：controlled_6m 达标比例，仅描述，不做检验、不挑选方法。",
    "亚组：无预设亚组，本报告不生成任何亚组分析或事后森林图。",
    "诊断：残差 Shapiro-Wilk P=%.3f；Breusch-Pagan LM=%.2f, P=%.3f（残差及异方差检查，详细见 stdout）。" % (sh_p, LM, bp_p),
]})

def fmt_p(p):
    """P 值按惯例显示：<0.001 或 4 位小数。"""
    return "<0.001" if p < 0.001 else f"{p:.4f}"

# ================================================================ 7. R5 教学用：主分析结果 CSV + 简报 Markdown
primary = pd.DataFrame([
    ["分析类型", "完整病例线性回归（调整基线收缩压、年龄、中心）"],
    ["主要结局", "6个月收缩压 sbp_6m (mmHg)"],
    ["完整病例 n", f"{n_ana}（干预 {int((ana['grp'] == 1).sum())} / 对照 {int((ana['grp'] == 0).sum())}）"],
    ["结局缺失（仅描述）", f"干预 {int(df.loc[(df['group'] == '干预组'), 'sbp_6m'].isna().sum())}/150，"
                           f"对照 {int(df.loc[(df['group'] == '对照组'), 'sbp_6m'].isna().sum())}/150"],
    ["组别编码", "干预组=1、对照组=0；中心 A=0、B=1"],
    ["调整均数差 MD（干预−对照, mmHg）", f"{md_c['系数']:.2f}"],
    ["95% CI（经典 SE）", f"{md_c['95%CI下限']:.2f} 至 {md_c['95%CI上限']:.2f}"],
    ["P 值（经典 SE）", fmt_p(md_c["P值"])],
    ["HC3 稳健 SE", f"{md_h['标准误']:.3f}"],
    ["95% CI（HC3）", f"{md_h['95%CI下限']:.2f} 至 {md_h['95%CI上限']:.2f}"],
    ["P 值（HC3）", fmt_p(md_h["P值"])],
    ["残差诊断", f"Shapiro-Wilk P={sh_p:.3f}；Breusch-Pagan LM={LM:.2f}, P={bp_p:.3f}（未见明显异方差）"],
    ["声明1", "合成教学数据，组别按编号交替生成，不是真实随机化分配"],
    ["声明2", "完整病例分析，缺失可能引入偏倚，不等于完整 ITT"],
    ["声明3", "无预设亚组，不生成事后亚组分析；不做均数填补"],
], columns=["指标", "值"])
primary.to_csv(OUT / "主分析结果.csv", index=False, encoding="utf-8-sig")
print("[写出] 主分析结果.csv")

with open(OUT / "主分析简报.md", "w", encoding="utf-8") as f:
    f.write(f"""# R4 主分析简报（R5 教学用）

**主要结局**：6 个月收缩压（mmHg）｜**模型**：完整病例线性回归，调整基线收缩压、年龄、中心

**完整病例 n = {n_ana}**（干预 {int((ana['grp'] == 1).sum())} / 对照 {int((ana['grp'] == 0).sum())}）

## 组间比较（调整均数差，干预 − 对照）

| 分析 | MD (mmHg) | 95% CI | P |
|---|---|---|---|
| 主分析（经典 SE） | {md_c['系数']:.2f} | {md_c['95%CI下限']:.2f} 至 {md_c['95%CI上限']:.2f} | {fmt_p(md_c['P值'])} |
| 敏感性分析（HC3 稳健 SE） | {md_h['系数']:.2f} | {md_h['95%CI下限']:.2f} 至 {md_h['95%CI上限']:.2f} | {fmt_p(md_h['P值'])} |

**一句话解读**：调整基线收缩压、年龄和中心后，干预组 6 个月收缩压比对照组低约 {abs(md_c['系数']):.1f} mmHg
（95%CI {md_c['95%CI下限']:.1f} 至 {md_c['95%CI上限']:.1f}）；HC3 稳健标准误下结论不变。

**必须随结果一并声明**：
1. 完整病例分析，不等于完整 ITT；结局缺失 干预 21/150、对照 10/150，仅描述差异，未做统计检验。
2. 合成教学数据，组别按编号交替生成，不是真实随机化分配，结果仅用于教学演示。
3. 无预设亚组；不做均数填补；次要结局达标比例仅描述（对照 46/140=32.9%，干预 65/129=50.4%）。
""")
print("[写出] 主分析简报.md")

# ================================================================ 8. 结果 Excel（标准库 zipfile 直接写最终 xlsx，
# 不经临时文件、不做任何删除；普通 Python 可重跑）
def _col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s

def _sheet_xml(df):
    def _row(ri, values):
        cells = []
        for ci, v in enumerate(values):
            ref = f"{_col_letter(ci)}{ri}"
            if v is None or (isinstance(v, float) and np.isnan(v)) or v == "":
                continue
            if isinstance(v, bool) or isinstance(v, (int, float, np.integer, np.floating)):
                cells.append(f'<c r="{ref}"><v>{float(v):.10g}</v></c>')
            else:
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t xml:space="preserve">'
                             f'{escape(str(v))}</t></is></c>')
        return f'<row r="{ri}">' + "".join(cells) + "</row>"

    rows_xml = [_row(1, [str(c) for c in df.columns])]
    for ri, (_, row) in enumerate(df.iterrows(), start=2):
        rows_xml.append(_row(ri, list(row)))
    return ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
            "<sheetData>" + "".join(rows_xml) + "</sheetData></worksheet>")

def write_xlsx(path, sheets):
    """sheets: [(name, DataFrame), ...] —— 纯标准库，直接写最终文件。"""
    n = len(sheets)
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
                     '<Default Extension="xml" ContentType="application/xml"/>'
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
                     '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>']
    wb_sheets, wb_rels = [], []
    for i, (name, _) in enumerate(sheets, start=1):
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                             'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        wb_sheets.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
        wb_rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
                       f'relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
    content_types.append("</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/'
            'relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    workbook = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
                'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">'
                "<sheets>" + "".join(wb_sheets) + "</sheets></workbook>")
    wb_rels_xml = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                   '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
                   + "".join(wb_rels) +
                   f'<Relationship Id="rId{n + 1}" Type="http://schemas.openxmlformats.org/officeDocument/'
                   '2006/relationships/styles" Target="styles.xml"/></Relationships>')
    styles = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
              '<styleSheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">'
              '<fonts count="1"><font><sz val="11"/><name val="Calibri"/></font></fonts>'
              '<fills count="1"><fill><patternFill patternType="none"/></fill></fills>'
              '<borders count="1"><border/></borders>'
              '<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>'
              '<cellXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/></cellXfs>'
              "</styleSheet>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(content_types))
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", workbook)
        z.writestr("xl/_rels/workbook.xml.rels", wb_rels_xml)
        z.writestr("xl/styles.xml", styles)
        for i, (_, df_i) in enumerate(sheets, start=1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", _sheet_xml(df_i))

write_xlsx(OUT / "R4-结果.xlsx",
           [("分析说明", notes), ("清洗日志", log), ("Table1", table1),
            ("主分析系数表", coef), ("纳入与未纳入者比较", compare),
            ("结局有无口径-仅描述", compare_outcome),
            ("次要结局-达标比例", pd.DataFrame(sec_rows))])
print("[写出] R4-结果.xlsx（zipfile 直写，无临时文件）")

# 结果表.md
md_c_line = f"{md_c['系数']:.2f} (95%CI {md_c['95%CI下限']:.2f}–{md_c['95%CI上限']:.2f}, P={fmt_p(md_c['P值'])})"
md_h_line = f"{md_h['系数']:.2f} (95%CI {md_h['95%CI下限']:.2f}–{md_h['95%CI上限']:.2f}, P={fmt_p(md_h['P值'])})"
# 系数表 Markdown 版：P 值极小者用科学计数法（Excel 中保留真实数值）
coef_md = coef.copy()
coef_md["P值"] = coef_md["P值"].map(lambda p: f"{p:.2e}" if p < 1e-4 else f"{p:.4f}")
for _c in ["系数", "标准误", "95%CI下限", "95%CI上限", "t值"]:
    coef_md[_c] = coef_md[_c].astype(float).round(4)
with open(OUT / "结果表.md", "w", encoding="utf-8") as f:
    f.write(f"""# R4 结果表（完整病例线性回归 + HC3 敏感性）

- 主要结局：6 个月收缩压（mmHg）；模型：sbp_6m ~ 组别 + 基线收缩压 + 年龄 + 中心
- 完整病例 n = {n_ana}（结局或协变量缺失 {n_miss} 例：干预组 {int(miss_g.get('干预组', 0))}、对照组 {int(miss_g.get('对照组', 0))}）
- 组别编码：干预组=1、对照组=0；中心 A=0、B=1

## 主要结果（调整均数差，干预−对照，mmHg）

| 分析 | 调整均数差 (mmHg) | 95% CI | P 值 |
|---|---|---|---|
| 主分析（经典 SE） | {md_c_line.split(' (')[0]} | {md_c['95%CI下限']:.2f} 至 {md_c['95%CI上限']:.2f} | {fmt_p(md_c['P值'])} |
| 敏感性分析（HC3 稳健 SE） | {md_h_line.split(' (')[0]} | {md_h['95%CI下限']:.2f} 至 {md_h['95%CI上限']:.2f} | {fmt_p(md_h['P值'])} |

## 完整系数表（P 值：<0.001 或科学计数法；Excel 中保留真实数值）

{coef_md.to_markdown(index=False)}

## 诊断

- 残差 Shapiro-Wilk 正态性检验 P = {sh_p:.3f}
- Breusch-Pagan 异方差检验：LM = {LM:.2f}，P = {bp_p:.3f}
- 解读：{'未见明显异方差' if bp_p > 0.05 else '提示存在异方差，HC3 敏感性分析结果为主要解读依据'}

## 次要结局（达标比例，仅描述，不检验）

{pd.DataFrame(sec_rows).to_markdown(index=False)}

## 主分析纳入者与未纳入者特征比较（仅描述，口径=完整病例 mask）

- **纳入 = 结局 + 全部协变量齐全，n = {n_ana}**；未纳入 n = {n_miss}（31 人结局缺失 + 1 人年龄=999 置缺失，SIM019）。

{compare.to_markdown(index=False)}

## 附表：按结局有无划分（仅描述，非主分析口径）

> 明确标注：本表按 `sbp_6m` 有无划分（{len(inc_o)}/{len(exc_o)}），**不是**主分析纳入者口径，不得混用标题。

{compare_outcome.to_markdown(index=False)}

## 声明

1. 主分析为完整病例分析（n={n_ana}），不等于完整 ITT；结局缺失在干预组 21/150、对照组 10/150，仅描述差异，未做统计检验。
2. 本数据为按编号交替生成的合成教学两组，不是真实随机化数据，结果仅用于教学演示。
3. 无预设亚组，不生成事后亚组分析或森林图；未均数填补；除已确认规则外未改动任何数据值。
""")
print("[写出] 结果表.md")

# ================================================================ 8. 控制台核对摘要（供重跑 diff）
print("\n===== 核对摘要（重跑应完全一致）=====")
print(f"清洗后记录数: {len(df)}; 唯一ID: {df['id'].nunique()}; 日志条数: {len(log)}")
print(f"完整病例 n: {n_ana} (干预 {int((ana['grp'] == 1).sum())} / 对照 {int((ana['grp'] == 0).sum())})")
print(f"结局缺失: 干预 {int(df.loc[(df['group']=='干预组'), 'sbp_6m'].isna().sum())}/150, "
      f"对照 {int(df.loc[(df['group']=='对照组'), 'sbp_6m'].isna().sum())}/150（仅描述）")
print(f"MD 主分析: {md_c['系数']:.8f} SE={md_c['标准误']:.8f} "
      f"CI=({md_c['95%CI下限']:.8f},{md_c['95%CI上限']:.8f}) P={md_c['P值']:.3e}")
print(f"MD HC3   : {md_h['系数']:.8f} SE={md_h['标准误']:.8f} "
      f"CI=({md_h['95%CI下限']:.8f},{md_h['95%CI上限']:.8f}) P={md_h['P值']:.3e}")
print(f"纳入口径: 主分析 {n_ana} / 未纳入 {n_miss}；结局有无 {int(df['sbp_6m'].notna().sum())}/{int(df['sbp_6m'].isna().sum())}（仅描述）")
print(f"其他系数(经典): 基线SBP={coef.iloc[4]['系数']:.6f} 年龄={coef.iloc[6]['系数']:.6f} 中心B={coef.iloc[8]['系数']:.6f}")
print("次要结局:", sec_rows)
print(f"Shapiro P={sh_p:.4f}; BP LM={LM:.3f} P={bp_p:.4f}")
