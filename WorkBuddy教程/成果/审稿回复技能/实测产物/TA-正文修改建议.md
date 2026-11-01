# T-A 实测产物 ①：正文修改建议（六处完整英文拟稿）

- 用例：T-A 正常审稿任务（立场已给，3 条意见），2026-11-02 修复复测版
- 稿件状态：**原稿未提供、无固定分页** → 位置一律 Section + paragraph；以下全部为 **PROPOSED（新拟稿）**，不存在"已修改"表述
- 数据来源说明：本项目数据为程序生成的**合成研究数据**（`资料/研究数据.csv`，不对应真实患者；group 为按编号交替生成的伪分组，非真实随机化）；以下段落引用的全部数字来自 `成果/数据分析/`（完整分析报告.md、模型系数表.csv、纳入与未纳入比较.csv）
- 作者立场（已确认）：意见 1、2 接受；意见 3 不接受实质要求（不做事后亚组、不新增探索性亚组、不以样本量不足为理由）

---

## 拟稿 1｜Section 2.2, paragraph 1（Outcomes and statistical analysis）— 服务于意见 1

```text
The primary outcome was 6-month office systolic blood pressure. The primary
analysis was a linear regression of 6-month systolic blood pressure on group
assignment, adjusted for baseline systolic blood pressure, age, and study
site. No subgroup analyses were prespecified in the analysis plan.
```

Status: **PROPOSED**

## 拟稿 2｜Section 3.3, paragraph 1（Primary result）— 服务于意见 1

```text
In the primary analysis (n = 268), the adjusted mean difference in 6-month
systolic blood pressure (intervention minus control) was −5.60 mm Hg (95% CI
−7.67 to −3.52; P < 0.001). In a prespecified check of the standard-error
estimator, refitting the model with HC3 robust standard errors gave −5.60 mm
Hg (95% CI −7.68 to −3.52); this check addresses the variance specification
only and is not a sensitivity analysis for missing data. All regression
coefficients with 95% confidence intervals are reported in Table 2.
```

Status: **PROPOSED**

## 拟稿 3｜Section 2.4, paragraph 2（Missing-data handling）— 服务于意见 2

```text
No imputation of any kind, including mean imputation, was applied. The
primary analysis is a complete-case analysis and is described as such
throughout; it is not described as a complete intention-to-treat analysis.
The pattern and volume of missing data are reported descriptively.
```

Status: **PROPOSED**

## 拟稿 4｜Section 3.4, paragraph 2（Missing-data pattern）— 服务于意见 2

```text
As prespecified, participants included in the primary analysis (n = 268) were
compared with those excluded (n = 32). The 6-month outcome was missing for
21/150 (14.0%) intervention participants and 10/150 (6.7%) control
participants, and excluded participants included a larger share of the
intervention group (65.6% vs 48.1%, P = 0.092). This comparison describes the
pattern of missingness in this dataset; it cannot determine the missing-data
mechanism, and the direction of any bias in the complete-case estimate cannot
be determined from these data.
```

Status: **PROPOSED**

## 拟稿 5｜Section 4.3, paragraph 1（Limitations, item 2）— 服务于意见 2

```text
Because the primary analysis is a complete-case analysis, its estimate may be
biased if missing data are related to outcomes or to group allocation; the
direction of any such bias cannot be determined from the comparisons available
in this dataset.
```

Status: **PROPOSED**

## 拟稿 6｜Section 2.4, final sentence + Section 4.3, third limitation — 服务于意见 3

```text
Section 2.4, final sentence:
No subgroup analyses were prespecified in the analysis plan, none were
performed, and no post hoc significance screening was carried out.

Section 4.3, third limitation:
No subgroup analyses were prespecified or performed; accordingly, no subgroup
results are reported and no exploratory subgroup findings are highlighted.
```

Status: **PROPOSED**（说明性文字）/ **NO CHANGE**（稿件不新增任何亚组分析）

---

## 来源对照（本文件全部数字）

| 值 | 来源（文件+位置） |
|---|---|
| −5.60（95% CI −7.67 至 −3.52），P<0.001 | 模型系数表.csv 第 2 行（−5.5959→−5.60；−7.6712→−7.67；−3.5206→−3.52）🔸 四舍五入 |
| −5.60（95% CI −7.68 至 −3.52）HC3 | 模型系数表.csv HC3 列（SE 1.0616 → CI −7.68 至 −3.52）🔸 四舍五入 |
| n=268（干预 129 / 对照 139） | 完整分析报告.md §2 |
| 21/150（14.0%）vs 10/150（6.7%） | 完整分析报告.md §2 |
| 65.6% vs 48.1%，P=0.092 | 纳入与未纳入比较.csv 第 12 行；完整分析报告.md:56–58 |
| 268 vs 32 | 完整分析报告.md §2 |
