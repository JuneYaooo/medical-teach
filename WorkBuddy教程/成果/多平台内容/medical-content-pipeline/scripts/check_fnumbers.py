#!/usr/bin/env python3
"""check_fnumbers.py — 医学内容编号检查辅助脚本

能力边界（重要，向使用者说明）：
  本脚本【只检查事实卡编号引用】，不判断医学语义：
  - 不判断某句是否为医学论断（因此检测不出"未编号的医学句"）；
  - 不核对"适用与限定"是否丢失；
  - 不核对数字与单位是否正确；
  - 不核对编号与句子内容是否匹配。
  以上必须由人工按"事实×载体对照表"完成。脚本通过 ≠ 内容正确。

约束：
  仅使用 Python 3 标准库；不联网、不安装依赖、不调用任何外部账号；
  只读写调用方指定的指定文件路径。

用法：
  python3 check_fnumbers.py --factcard 事实卡.csv --input 载体.md [更多.md ...] [--report 报告.md]

退出码：
  0 = 检查完成且未发现编号错误
  1 = 发现未知编号或事实卡为空/列缺失等问题之外的编号错误
  2 = 事实卡缺失/不可读/列缺失（按流程应先索取事实卡）
"""

import argparse
import csv
import re
import sys

TAG_RE = re.compile(r"\[(F\d{2,3})\]")
REQUIRED_COLS = ["编号", "事实陈述", "来源", "适用与限定", "核对状态", "医生签署"]
# 判定规则：以"已签署"开头的值计为已签署；含"模拟"字样的按模拟签署提示（不代表真实审核）。
SIGNED_PREFIX = "已签署"
SIMULATED_MARKER = "模拟"


def fail(msg, code):
    print(msg)
    sys.exit(code)


def load_factcard(path):
    """读取事实卡；返回 (编号->行 的字典, 是否全部已签署)。"""
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            reader.fieldnames = [c.strip() for c in (reader.fieldnames or [])]
            fields = reader.fieldnames
            missing = [c for c in REQUIRED_COLS if c not in fields]
            if missing:
                fail(f"[错误] 事实卡缺少必需列：{', '.join(missing)}。请先补全事实卡。", 2)
            facts = {}
            all_signed = True
            for row in reader:
                fid = (row.get("编号") or "").strip()
                if not fid:
                    continue
                if fid in facts:
                    fail(f"[错误] 事实卡中编号重复：{fid}。请修正事实卡。", 2)
                facts[fid] = row
                if not (row.get("医生签署") or "").strip().startswith(SIGNED_PREFIX):
                    all_signed = False
    except FileNotFoundError:
        fail(f"[错误] 找不到事实卡文件：{path}\n[流程] 缺少事实卡：请先向内容发起人索取事实卡，不得凭记忆生成医学内容。", 2)
    except OSError as e:
        fail(f"[错误] 事实卡无法读取：{path}（{e}）\n[流程] 请先提供可读取的事实卡。", 2)

    if not facts:
        fail("[错误] 事实卡为空：没有任何编号行。请先索取有效事实卡。", 2)
    return facts, all_signed


def check_file(path, facts):
    """对单个文件做编号检查，返回结果字典。不做任何语义判断。"""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except (OSError, UnicodeDecodeError) as e:
        fail(f"[错误] 输入文件无法读取：{path}（{e}）", 2)
    tags = TAG_RE.findall(text)
    used, unknown = [], []
    for t in tags:
        (used if t in facts else unknown).append(t)
    dupes = sorted({t for t in used if used.count(t) > 1})
    never_cited = sorted(set(facts) - set(used))
    return {
        "path": path,
        "total_tags": len(tags),
        "valid_tags": len(used),
        "unknown_tags": sorted(set(unknown)),
        "per_fact": {fid: used.count(fid) for fid in sorted(facts) if used.count(fid)},
        "never_cited": never_cited,
        "dupes": dupes,
    }


def main():
    ap = argparse.ArgumentParser(description="只检查事实卡编号引用，不判断医学语义。")
    ap.add_argument("--factcard", help="事实卡 CSV 路径（缺省时按'缺事实卡'流程退出）")
    ap.add_argument("--input", nargs="+", required=True, help="待检查的载体 Markdown 文件（可多个）")
    ap.add_argument("--report", help="可选：把报告写入该 Markdown 路径（须位于指定文件内）")
    args = ap.parse_args()

    print("== medical-content-pipeline 编号检查 ==")
    print("说明：本脚本只检查编号引用，不判断医学语义；"
          "未编号医学句、限定词丢失、数字正确性须人工按对照表核对。")

    if not args.factcard:
        fail("[流程] 缺少事实卡：请先向内容发起人索取事实卡（CSV），不得凭记忆生成医学内容。", 2)

    facts, all_signed = load_factcard(args.factcard)
    print(f"[事实卡] {args.factcard}：{len(facts)} 张卡")

    if all_signed:
        simulated = any(SIMULATED_MARKER in row.get("医生签署", "") for row in facts.values())
        if simulated:
            print("[状态] 测试数据含模拟签署，仅测试状态分支，不代表真实医生审核，不能据此发布。")
        else:
            print("[状态] 事实卡签署字段均记录为'已签署'；本脚本不核验签署真实性，也不据此批准发布。")
    else:
        print("[状态] 事实卡未全部签署；审核状态需独立记录，本脚本不批准发布。")

    results = [check_file(p, facts) for p in args.input]
    has_error = False
    for r in results:
        print(f"\n-- {r['path']}")
        print(f"   编号标签总数：{r['total_tags']}，有效引用：{r['valid_tags']}")
        if r["unknown_tags"]:
            has_error = True
            print(f"   [错误] 引用了事实卡中不存在的编号：{', '.join(r['unknown_tags'])}"
                  f"（可能是换主题后未换事实卡，或编号笔误）")
        else:
            print("   未知编号：无")
        if r["dupes"]:
            print(f"   提示：被多次引用的编号：{', '.join(r['dupes'])}（是否合理请人工判断）")
        if r["never_cited"]:
            print(f"   提示：事实卡中从未被引用的编号：{', '.join(r['never_cited'])}"
                  f"（是否需要覆盖请人工判断）")
        else:
            print("   事实卡全部编号均被引用")

    if has_error:
        fail("\n[结果] 编号检查未通过：存在未知编号。", 1)
    print("\n[结果] 编号检查通过（仅指编号层面；语义、限定、数字仍须人工按对照表核对）。")

    if args.report:
        lines = ["# 编号检查报告（check_fnumbers.py）", "",
                 "> 本脚本只检查编号引用，不判断医学语义；未编号医学句、限定词丢失、数字正确性须人工核对。", ""]
        lines.append(f"- 事实卡：{args.factcard}（{len(facts)} 张卡）")
        lines.append(f"- 医生签署状态：{'全部已签署' if all_signed else '未全部签署；不构成发布批准'}")
        lines.append("")
        for r in results:
            lines.append(f"## {r['path']}")
            lines.append(f"- 编号标签总数：{r['total_tags']}；有效引用：{r['valid_tags']}")
            lines.append(f"- 未知编号：{', '.join(r['unknown_tags']) or '无'}")
            lines.append(f"- 从未被引用：{', '.join(r['never_cited']) or '无'}")
            lines.append(f"- 多次引用：{', '.join(r['dupes']) or '无'}")
            lines.append("")
        try:
            with open(args.report, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            print(f"[报告] 已写入：{args.report}")
        except OSError as e:
            print(f"[警告] 报告写入失败：{e}")


if __name__ == "__main__":
    main()
