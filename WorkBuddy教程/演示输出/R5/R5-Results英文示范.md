# R5 英文 Results 示范（带来源标签）

- **性质**：教学示范稿，用于对照 R4 结果表逐格核数。**不是投稿终稿。**
- **规则**：①所有数字只来自 R4 结果表/Table1，照抄不换算；②先写人群与基线，再主要结局，再诊断与敏感性，再缺失，再次要结局；③只描述，不解释原因；④每个数字后 `[标签]` 标出处，核对完由作者删除。
- **研究性质声明**：本文所述为合成教学数据，组别按编号交替生成，非随机化。
- 更新时间：2026-10-30 19:05 (GMT+8)

---

## Results

### Participant flow and analysis set

The dataset comprised 303 records; three records were identical across all 15 fields and were removed, leaving 300 unique participants, with 150 in each group [CHK-1; CHK-7.1]. Of these 300 participants, 32 were not included in the primary analysis: 31 had no 6-month blood pressure record, and one had an implausible age value (999) that was set to missing under the prespecified cleaning rules [RES-0]. The primary complete-case analysis therefore included 268 participants (intervention, n = 129; control, n = 139) [RES-0].

### Baseline characteristics

Baseline characteristics were similar between the two groups (Table 1). Mean (SD) age was 72.0 (7.4) years in the intervention group and 72.1 (6.7) years in the control group, and 74 participants (49.3%) and 78 (52.0%), respectively, were male [T1-2; T1-3]. Mean (SD) baseline systolic blood pressure was 150.3 (12.3) mmHg in the intervention group and 151.1 (11.9) mmHg in the control group [T1-7]; mean (SD) baseline diastolic blood pressure was 87.7 (7.4) mmHg and 88.2 (6.8) mmHg [T1-8]. Mean (SD) body mass index was 24.7 (2.9) kg/m² and 25.4 (3.1) kg/m² [T1-4], and mean (SD) duration of hypertension was 10.7 (5.2) years and 11.0 (6.3) years [T1-5]. Diabetes was present in 78 participants (52.0%) in the intervention group and 71 (47.3%) in the control group [T1-6]. Mean (SD) adherence was 0.7 (0.2) in both groups [T1-9], and 76 participants (50.7%) and 70 (46.7%) were recruited at centre B [T1-11]. The mean (SD) number of completed visits was 4.0 (1.4) and 3.7 (1.4) [T1-10].

### Primary outcome

After adjustment for baseline systolic blood pressure, age and centre, the adjusted mean difference in 6-month systolic blood pressure between the intervention and control groups was −5.60 mmHg (95% CI −7.67 to −3.52; P < 0.001) [RES-1]. In the same model, 6-month systolic blood pressure was associated with baseline systolic blood pressure (coefficient 0.97 per mmHg, SE 0.04; P < 0.001) [COEF-5], whereas age (coefficient −0.01 per year, SE 0.08; P = 0.908) [COEF-7] and centre B versus centre A (coefficient −0.53, SE 1.06; P = 0.618) [COEF-9] were not.

### Model assumptions and sensitivity analysis for variance specification

Residuals were consistent with a normal distribution (Shapiro–Wilk P = 0.921) [DIAG-1], and the Breusch–Pagan test provided no evidence of heteroskedasticity (LM = 1.91; P = 0.752) [DIAG-2]. As a sensitivity analysis for the variance specification, the model was refitted with heteroskedasticity-consistent (HC3) standard errors; the adjusted mean difference was unchanged at −5.60 mmHg (95% CI −7.69 to −3.51; P < 0.001) [RES-2], and the standard error of the group coefficient increased from 1.054 to 1.062 [COEF-3; COEF-4]. This analysis addresses the variance specification only and is **not** a sensitivity analysis for missing outcome data.

### Missing outcome data

Six-month blood pressure was missing for 21 of 150 participants (14.0%) in the intervention group and 10 of 150 (6.7%) in the control group [RES-0]. These proportions are reported descriptively; no statistical test was performed and no imputation of any kind, including mean imputation, was applied [DECL-1; DECL-3]. Compared with participants included in the primary analysis, those not included were slightly younger (mean 70.1 vs 72.2 years) [INC-2], less often male (40.6% vs 51.9%) [INC-3], and more often in the intervention group (65.6% vs 48.1%) [INC-11]; they also had a longer mean duration of hypertension (11.8 vs 10.7 years) [INC-5] and a similar mean number of completed visits (4.1 vs 3.8) [INC-12].

The missing-data mechanism cannot be determined from these comparisons, and the complete-case analysis may therefore be biased; the primary analysis is not a complete intention-to-treat analysis [DECL-1]. **Sensitivity analyses for missing outcome data (for example multiple imputation or worst-case scenarios) have not been performed** and are not reported here.

### Secondary outcome

At 6 months, the proportion of participants achieving the <140/90 mmHg target was 46/140 (32.9%) in the control group and 65/129 (50.4%) in the intervention group [SEC-1; SEC-2]. These proportions are descriptive only; no between-group test was performed and no inference is drawn [DECL-3]. The denominators differ from those of the primary model because the secondary analysis required the outcome but not complete covariate data (269 participants with an available outcome versus 268 in the adjusted model) [RES-0].

### Subgroup analyses

No subgroup analyses were prespecified, and none were performed; no post hoc subgroup comparison or forest plot is presented [DECL-3].

### Nature of the data

All results reported here derive from a simulated dataset generated for teaching purposes, in which group assignment was produced by alternating participant identifiers rather than by randomisation [DECL-2]. The findings illustrate reporting practice and do not constitute evidence of clinical efficacy.

---

## 标签 → 出处对照

| 标签 | 文件 | 位置 | 取用值 |
|---|---|---|---|
| CHK-1 | `演示输出/R4/R4-数据体检报告.md` | §1 结论速览，"数据行数"行／"唯一受试者数"行 | 303 条 / 300 例 |
| CHK-7.1 | 同上 | §7.1 完全重复行表 | 3 条（行 302/303/304） |
| RES-0 | `演示输出/R4/结果表.md` | 顶部说明行（"完整病例 n = 268…32 例：干预组 21、对照组 11"） | 268；129/139；32；21/10 |
| RES-1 | 同上 | 「主要结果」表第 1 行 | −5.60；−7.67 至 −3.52；<0.001 |
| RES-2 | 同上 | 「主要结果」表第 2 行（HC3） | −5.60；−7.69 至 −3.51；<0.001 |
| COEF-3 | 同上 | 「完整系数表」组别，经典 SE 行 | 系数 −5.5959；SE 1.054 |
| COEF-4 | 同上 | 「完整系数表」组别，HC3 行 | SE 1.0616 |
| COEF-5 | 同上 | 「完整系数表」基线收缩压，经典行 | 0.9708；SE 0.0435；P 1.38e-62 |
| COEF-7 | 同上 | 「完整系数表」年龄，经典行 | −0.0088；SE 0.076；P 0.9079 |
| COEF-9 | 同上 | 「完整系数表」中心B，经典行 | −0.5285；SE 1.0575；P 0.6177 |
| DIAG-1 | 同上 | 「诊断」第 1 条 | Shapiro-Wilk P = 0.921 |
| DIAG-2 | 同上 | 「诊断」第 2 条 | LM = 1.91；P = 0.752 |
| SEC-1 | 同上 | 「次要结局」表 对照组行 | 140；46；32.9% |
| SEC-2 | 同上 | 「次要结局」表 干预组行 | 129；65；50.4% |
| INC-2 | 同上 | 「主分析纳入者与未纳入者」表 年龄行 | 72.2 / 70.1 |
| INC-3 | 同上 | 同表 男性行 | 51.9% / 40.6% |
| INC-5 | 同上 | 同表 病程行 | 10.7 / 11.8 |
| INC-11 | 同上 | 同表 干预组行 | 48.1% / 65.6% |
| INC-12 | 同上 | 同表 完成访视次数行 | 3.8 / 4.1 |
| DECL-1 | 同上 | 「声明」第 1 条 | 完整病例 ≠ 完整 ITT；21/150、10/150 |
| DECL-2 | 同上 | 「声明」第 2 条 | 合成教学数据、按编号交替 |
| DECL-3 | 同上 | 「声明」第 3 条 | 无预设亚组；无均数填补 |
| T1-2 | `演示输出/R4/Table1.csv` | 第 2 行 年龄 | 72.0 ± 7.4 / 72.1 ± 6.7 |
| T1-3 | 同上 | 第 3 行 男性 | 74 (49.3%) / 78 (52.0%) |
| T1-4 | 同上 | 第 4 行 BMI | 24.7 ± 2.9 / 25.4 ± 3.1 |
| T1-5 | 同上 | 第 5 行 高血压病程 | 10.7 ± 5.2 / 11.0 ± 6.3 |
| T1-6 | 同上 | 第 6 行 糖尿病 | 78 (52.0%) / 71 (47.3%) |
| T1-7 | 同上 | 第 7 行 基线收缩压 | 150.3 ± 12.3 / 151.1 ± 11.9 |
| T1-8 | 同上 | 第 8 行 基线舒张压 | 87.7 ± 7.4 / 88.2 ± 6.8 |
| T1-9 | 同上 | 第 9 行 依从率 | 0.7 ± 0.2 / 0.7 ± 0.2 |
| T1-10 | 同上 | 第 10 行 完成访视次数 | 4.0 ± 1.4 / 3.7 ± 1.4 |
| T1-11 | 同上 | 第 11 行 中心 B | 76 (50.7%) / 70 (46.7%) |

---

## 写法说明（供核对时判断"该不该这么写"）

| 处理 | 原因 |
|---|---|
| 效应量只写 aMD，不写"组均值" | 本段呈现调整均数差；未调整组均值见 R4 结果图 A。图 A 有结局者 n=269，与主模型完整病例 n=268 不同，不能混用分母 |
| HC3 单独设小节，标题就写明"variance specification" | 避免读者误当缺失敏感性分析 |
| 缺失段**不加**"两组差异显著" | 未做检验 |
| 缺失段**不下** MAR / MNAR 结论 | 观察数据无法判定；只写"无法确定 + 可能偏倚" |
| 明确写"未做缺失敏感性分析" | 事实如此，写"已做"即不实 |
| 次要结局标 269 与 268 的差异 | 两个分母不同，不解释会被当成算错 |
| 亚组单独一小节写"没有" | 主动关闭 C6 的口子，比等审稿人再问更稳 |
| 全篇无 demonstrate/prove/efficacy | 合成数据不能证因果 |
