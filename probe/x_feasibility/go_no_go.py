"""§7 go/no-go, applied verbatim over the JSONL records of a probe campaign.

``contracts/ops/collector-probe.md`` §7 gives seven criteria and three verdicts. This module
computes them and nothing else: it does not soften a threshold, it does not average away a
bad run, and it has no flag that relaxes a criterion. §7's own words: "áp dụng nguyên văn,
không nới".

Verdicts
--------
``GO``            all of GO-1..GO-7 pass. Reads only as: *"nguồn X khả thi ở mức ngân sách
                  đã thử, trong cửa sổ đã đo"*. Not that X is stable (REQ-A7 stays ``KC``).
``NO_GO``         some criterion failed. Report **blocked** for source X with the numbers.
                  Do not move to the paid X API and do not relax §2 and re-run -- both are
                  the Owner's decision, not this tool's (SRC-PLAN §12).
``INCONCLUSIVE``  N < 5, or GO-6 failed, or N > 10. Fix the cause and run again; do not
                  reason from missing data.

Exit codes: 0 GO, 1 NO_GO, 2 INCONCLUSIVE, 3 usage/IO error.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from probe.x_feasibility import PROTOCOL_VERSION
from probe.x_feasibility.config import PROBE_RUN_COUNT_MAX, PROBE_RUN_COUNT_MIN
from probe.x_feasibility.record import read_records

GO = "GO"
NO_GO = "NO_GO"
INCONCLUSIVE = "INCONCLUSIVE"

EXIT_CODES: dict[str, int] = {GO: 0, NO_GO: 1, INCONCLUSIVE: 2}

# --- §7 thresholds, PROVISIONAL as the contract labels them --------------------------
GO1_LIMIT_REACHED_SHARE_MIN = 0.60
GO2_CHALLENGES_PER_RUNS = (1, 5)  # "≤ 1 trên mỗi 5 đợt"
GO3_BLOCKED_MAX = 0
GO4_NEW_POSTS_MEDIAN_MIN = 5
GO5_PARSE_RATIO_MIN = 0.90
GO6_PARSER_DEGRADED_MAX = 0
GO7_UNOBSERVABLE_SHARE_MIN = 1.0


@dataclass(frozen=True)
class CriterionResult:
    criterion_id: str
    passed: bool
    observed: float | int | str
    threshold: str
    statement_vi: str

    def line(self) -> str:
        mark = "PASS" if self.passed else "FAIL"
        return f"  {self.criterion_id}  {mark}  quan sát={self.observed}  ngưỡng={self.threshold}"


@dataclass(frozen=True)
class GoNoGoReport:
    verdict: str
    n_runs: int
    criteria: tuple[CriterionResult, ...]
    reason_vi: str

    @property
    def failed_ids(self) -> tuple[str, ...]:
        return tuple(c.criterion_id for c in self.criteria if not c.passed)

    def to_dict(self) -> dict[str, Any]:
        return {
            "protocol_version": PROTOCOL_VERSION,
            "verdict": self.verdict,
            "n_runs": self.n_runs,
            "failed_criteria": list(self.failed_ids),
            "reason_vi": self.reason_vi,
            "criteria": [
                {
                    "criterion_id": c.criterion_id,
                    "passed": c.passed,
                    "observed": c.observed,
                    "threshold": c.threshold,
                    "statement_vi": c.statement_vi,
                }
                for c in self.criteria
            ],
        }

    def render_vi(self) -> str:
        lines = [
            "GO/NO-GO — contracts/ops/collector-probe.md §7 (áp dụng nguyên văn)",
            f"Số đợt N = {self.n_runs}",
            "",
        ]
        lines += [c.line() for c in self.criteria]
        lines += ["", f"KẾT LUẬN: {self.verdict}", self.reason_vi]
        return "\n".join(lines)


def _sum(records: list[dict[str, Any]], field: str) -> int:
    return sum(int(r[field]) for r in records)


def evaluate(records: list[dict[str, Any]]) -> GoNoGoReport:
    """Apply §7 to a list of validated §5 records."""
    n = len(records)
    if n == 0:
        return GoNoGoReport(
            verdict=INCONCLUSIVE,
            n_runs=0,
            criteria=(),
            reason_vi=("KHÔNG KẾT LUẬN — không có đợt nào. §7 tính trên 5 ≤ N ≤ 10 đợt đã chạy."),
        )

    limit_reached = sum(1 for r in records if r["stop_reason"] == "limit_reached")
    go1_observed = limit_reached / n
    go1 = CriterionResult(
        "GO-1",
        go1_observed >= GO1_LIMIT_REACHED_SHARE_MIN,
        round(go1_observed, 4),
        f">= {GO1_LIMIT_REACHED_SHARE_MIN}",
        "Số đợt kết thúc bằng limit_reached (chạy hết ngân sách mà không bị cắt).",
    )

    challenges = _sum(records, "challenge_count")
    allowed, per = GO2_CHALLENGES_PER_RUNS
    go2 = CriterionResult(
        "GO-2",
        challenges * per <= allowed * n,
        challenges,
        f"<= {allowed} trên mỗi {per} đợt (N={n} ⇒ <= {allowed * n / per:g})",
        "challenge_count cộng dồn. Mỗi challenge cần người ngồi trước máy xử lý.",
    )

    blocked = _sum(records, "blocked_count")
    go3 = CriterionResult(
        "GO-3",
        blocked == GO3_BLOCKED_MAX,
        blocked,
        f"= {GO3_BLOCKED_MAX}",
        "blocked_count cộng dồn. Một lần bị chặn thật là tín hiệu định tính, không phải nhiễu.",
    )

    tail = [int(r["posts_new_vs_previous_runs"]) for r in records[1:]]
    go4_observed: float | str = statistics.median(tail) if tail else "n/a (chỉ có 1 đợt)"
    go4 = CriterionResult(
        "GO-4",
        bool(tail) and statistics.median(tail) >= GO4_NEW_POSTS_MEDIAN_MIN,
        go4_observed,
        f">= {GO4_NEW_POSTS_MEDIAN_MIN} bài/đợt",
        "Trung vị posts_new_vs_previous_runs ở các đợt SAU đợt đầu. Trung vị, không trung bình.",
    )

    seen = _sum(records, "posts_seen")
    parsed = _sum(records, "posts_parsed_ok")
    go5_observed: float | str = round(parsed / seen, 4) if seen else "n/a (posts_seen = 0)"
    go5 = CriterionResult(
        "GO-5",
        seen > 0 and parsed / seen >= GO5_PARSE_RATIO_MIN,
        go5_observed,
        f">= {GO5_PARSE_RATIO_MIN}",
        "posts_parsed_ok / posts_seen cộng dồn. posts_seen = 0 KHÔNG phải một tỉ lệ đạt.",
    )

    degraded = _sum(records, "parser_degraded_count")
    go6 = CriterionResult(
        "GO-6",
        degraded == GO6_PARSER_DEGRADED_MAX,
        degraded,
        f"= {GO6_PARSER_DEGRADED_MAX}",
        "parser_degraded_count. Bố cục đổi giữa probe ⇒ kết quả không kết luận được.",
    )

    filled = sum(1 for r in records if str(r.get("unobservable_scope_vi", "")).strip())
    go7_observed = filled / n
    go7 = CriterionResult(
        "GO-7",
        go7_observed >= GO7_UNOBSERVABLE_SHARE_MIN,
        f"{filled}/{n}",
        "100%",
        "unobservable_scope_vi được điền ở MỌI đợt. Kỷ luật ghi chép, không phải phép đo.",
    )

    criteria = (go1, go2, go3, go4, go5, go6, go7)

    if n < PROBE_RUN_COUNT_MIN:
        return GoNoGoReport(
            INCONCLUSIVE,
            n,
            criteria,
            f"KHÔNG KẾT LUẬN — N = {n} < {PROBE_RUN_COUNT_MIN}. §7: không suy diễn từ dữ "
            "liệu thiếu. Chạy thêm đợt rồi tính lại.",
        )
    if n > PROBE_RUN_COUNT_MAX:
        return GoNoGoReport(
            INCONCLUSIVE,
            n,
            criteria,
            f"KHÔNG KẾT LUẬN — N = {n} > {PROBE_RUN_COUNT_MAX}. §3.1 đặt trần 10 đợt để "
            "probe không biến thành 'dùng thật mà chưa có hợp đồng'; vượt trần thì tập đợt "
            "này không còn là cái §7 mô tả.",
        )
    if not go6.passed:
        return GoNoGoReport(
            INCONCLUSIVE,
            n,
            criteria,
            "KHÔNG KẾT LUẬN — GO-6 trượt (bố cục đổi giữa probe). §7: sửa bộ đọc rồi chạy "
            "lại TỪ ĐẦU; không kết luận từ tập đợt đã lẫn hai bố cục.",
        )

    failed = [c.criterion_id for c in criteria if not c.passed]
    if failed:
        return GoNoGoReport(
            NO_GO,
            n,
            criteria,
            "NO-GO — trượt " + ", ".join(failed) + ". §7: báo quyết định BLOCKED cho nguồn "
            "X kèm số liệu. KHÔNG chuyển sang X API trả phí, KHÔNG nới ranh giới §2 rồi "
            "chạy lại. Quyết định tiếp theo là của Owner.",
        )
    return GoNoGoReport(
        GO,
        n,
        criteria,
        "GO — nguồn X khả thi Ở MỨC NGÂN SÁCH ĐÃ THỬ, TRONG CỬA SỔ ĐÃ ĐO. Không có nghĩa "
        "nguồn X ổn định lâu dài (REQ-A7 vẫn KC), không có nghĩa collector đã hoạt động, "
        "không có nghĩa AC-01/AC-04 đã pass (§10). Owner dùng chính số liệu này để chốt "
        "REQ-OQ05.",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="go_no_go",
        description=(
            "Tính go/no-go của probe SP1 theo contracts/ops/collector-probe.md §7, "
            "nguyên văn. Không có cờ nào nới ngưỡng."
        ),
    )
    parser.add_argument(
        "jsonl",
        nargs="?",
        default="evidence/runs/SP1-x-feasibility/runs.jsonl",
        help="File JSONL các đợt probe (mặc định: evidence/runs/SP1-x-feasibility/runs.jsonl)",
    )
    parser.add_argument("--json", action="store_true", help="In kết quả dạng JSON")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        records = read_records(Path(args.jsonl))
    except (FileNotFoundError, ValueError) as exc:
        print(f"Không đọc được bản ghi: {exc}", file=sys.stderr)
        return 3
    report = evaluate(records)
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.render_vi())
    return EXIT_CODES[report.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
