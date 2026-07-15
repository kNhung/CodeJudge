"""
Offline weight tuning for HCMUS multi-agent scoring.

Workflow:
  1. Run score_with_multi_agent.py once with --config configs/hcmus_factors.json
     (pre_extracted_factors only; equal weights during LLM run).
  2. Run this script on the resulting JSONL to search optimal factor_weights.
  3. Apply tuned weights via --write-config / --rescore-jsonl, then validate
     with calculate_metric.py.

Train/val split is by problem_id to avoid overfitting student patterns.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from unittest.mock import MagicMock

import numpy as np
from scipy.optimize import differential_evolution, minimize
from scipy.stats import kendalltau, spearmanr

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from codejudge.core.multi_agent_assessor import MultiAgentAssessor

HCMUS_ROOT = Path(__file__).resolve().parent
DEFAULT_JSONL = HCMUS_ROOT / "ouput_to_share" / "report_9" / "260610_1430_multi_agent_gemini-2.5-flash.jsonl"
DEFAULT_FACTORS_CONFIG = HCMUS_ROOT / "configs" / "hcmus_factors.json"
DEFAULT_TUNED_CONFIG = HCMUS_ROOT / "configs" / "hcmus_tuned_weights.json"

QuestionKey = Tuple[str, int]


@dataclass
class QuestionRecord:
    row_id: str
    problem_id: str
    question_index: int
    expect_grade: float
    question_max: float
    factor_evaluation: Dict[str, Dict[str, Any]]
    syntax_errors: List[str]
    factor_names: List[str] = field(default_factory=list)


@dataclass
class ExamRecord:
    row_id: str
    problem_id: str
    expect_grade: float
    questions: List[QuestionRecord]


def load_per_question_records(jsonl_path: Path) -> List[QuestionRecord]:
    records: List[QuestionRecord] = []
    with jsonl_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)
            if data.get("scoring_mode") != "per_question":
                continue
            result = data.get("result", {})
            if not isinstance(result, dict):
                continue
            factor_eval = result.get("factor_evaluation", {})
            if not factor_eval:
                continue
            try:
                expect_grade = float(data.get("expect_grade", 0))
            except (TypeError, ValueError):
                continue
            records.append(
                QuestionRecord(
                    row_id=str(data.get("id", "")),
                    problem_id=str(data.get("problem_id", "")),
                    question_index=int(data.get("question_index", 0)),
                    expect_grade=expect_grade,
                    question_max=float(data.get("question_max", 10.0)),
                    factor_evaluation=factor_eval,
                    syntax_errors=list(result.get("syntax_errors") or []),
                    factor_names=list(result.get("factors") or list(factor_eval.keys())),
                )
            )
    return records


def group_exams(records: Sequence[QuestionRecord]) -> List[ExamRecord]:
    by_id: Dict[str, List[QuestionRecord]] = defaultdict(list)
    for rec in records:
        by_id[rec.row_id].append(rec)

    exams: List[ExamRecord] = []
    for row_id, questions in sorted(by_id.items()):
        questions = sorted(questions, key=lambda q: q.question_index)
        exams.append(
            ExamRecord(
                row_id=row_id,
                problem_id=questions[0].problem_id,
                expect_grade=questions[0].expect_grade,
                questions=questions,
            )
        )
    return exams


def extract_factors_config(
    records: Sequence[QuestionRecord],
    majority_vote: bool = True,
) -> Dict[str, Dict[str, Dict[str, Any]]]:
    """Build config with stable pre_extracted_factors per (problem_id, question_index).

    When majority_vote=True (default), picks the most common factor list per question
  instead of failing on Agent-1 naming drift across students.
    """
    by_key: Dict[QuestionKey, List[List[str]]] = defaultdict(list)
    for rec in records:
        key = (rec.problem_id, rec.question_index)
        by_key[key].append(list(rec.factor_names))

    config: Dict[str, Dict[str, Dict[str, Any]]] = defaultdict(dict)
    for (problem_id, qidx), factor_lists in sorted(by_key.items()):
        counts: Dict[Tuple[str, ...], int] = {}
        for names in factor_lists:
            t = tuple(names)
            counts[t] = counts.get(t, 0) + 1
        if len(counts) == 1:
            chosen = factor_lists[0]
        elif majority_vote:
            chosen = list(max(counts.items(), key=lambda kv: (kv[1], -len(kv[0])))[0])
            mode_freq = counts[tuple(chosen)]
            if mode_freq < len(factor_lists):
                print(
                    f"  Majority factors for {problem_id} Q{qidx}: "
                    f"{mode_freq}/{len(factor_lists)} records"
                )
        else:
            # Strict mode: first vs second mismatch raises
            seen_lists = list(counts.keys())
            if len(seen_lists) > 1:
                raise ValueError(
                    f"Inconsistent factor names for {(problem_id, qidx)}. "
                    f"Re-run scoring with --config pre_extracted_factors."
                )
            chosen = list(seen_lists[0])
        config[problem_id][str(qidx)] = {"pre_extracted_factors": chosen}
    return dict(config)


def build_question_specs(
    records: Sequence[QuestionRecord],
    factors_config: Optional[Dict[str, Any]] = None,
) -> Dict[QuestionKey, List[str]]:
    specs: Dict[QuestionKey, List[str]] = {}
    for rec in records:
        key = (rec.problem_id, rec.question_index)
        if key in specs:
            continue
        if factors_config:
            qcfg = factors_config.get(rec.problem_id, {}).get(str(rec.question_index), {})
            factors = qcfg.get("pre_extracted_factors") or rec.factor_names
        else:
            factors = rec.factor_names
        specs[key] = list(factors)
    return specs


def softmax(x: np.ndarray) -> np.ndarray:
    x = x - np.max(x)
    e = np.exp(x)
    return e / e.sum()


class WeightOptimizer:
    def __init__(
        self,
        exams: Sequence[ExamRecord],
        question_specs: Dict[QuestionKey, List[str]],
        assessor: MultiAgentAssessor,
        syntax_penalties: Optional[Dict[str, float]] = None,
    ):
        self.exams = list(exams)
        self.question_specs = question_specs
        self.assessor = assessor
        self.syntax_penalties = syntax_penalties
        self.question_keys = sorted(question_specs.keys())
        self._slices: List[Tuple[int, int]] = []
        offset = 0
        for key in self.question_keys:
            n = len(question_specs[key])
            self._slices.append((offset, offset + n))
            offset += n

    def vector_to_weights(self, params: np.ndarray) -> Dict[QuestionKey, Dict[str, float]]:
        weights: Dict[QuestionKey, Dict[str, float]] = {}
        for key, (start, end) in zip(self.question_keys, self._slices):
            logits = params[start:end]
            w = softmax(logits)
            factors = self.question_specs[key]
            weights[key] = {f: float(w[i]) for i, f in enumerate(factors)}
        return weights

    def matched_weights(
        self,
        factor_names: Sequence[str],
        factor_weights: Dict[str, float],
    ) -> Optional[Dict[str, float]]:
        matched = {f: factor_weights[f] for f in factor_names if f in factor_weights}
        if not matched or set(matched.keys()) != set(factor_names):
            return matched if matched else None
        return factor_weights

    def score_question(
        self,
        rec: QuestionRecord,
        factor_weights: Dict[str, float],
    ) -> float:
        # Map canonical tuned weights onto this record's actual factor names.
        # When Agent 1 used different wording, fall back to equal weights.
        use_weights = self.matched_weights(rec.factor_names, factor_weights)
        scoring = self.assessor.calculate_score(
            factor_eval=rec.factor_evaluation,
            syntax_errors=rec.syntax_errors,
            question_max=rec.question_max,
            factor_weights=use_weights,
            syntax_penalties=self.syntax_penalties,
        )
        return float(scoring.get("scaled_score", 0.0))

    def predict_exam_total(self, exam: ExamRecord, all_weights: Dict[QuestionKey, Dict[str, float]]) -> float:
        total = 0.0
        for q in exam.questions:
            key = (q.problem_id, q.question_index)
            w = all_weights.get(key)
            if w is None:
                w = {f: 1.0 / len(q.factor_names) for f in q.factor_names}
            total += self.score_question(q, w)
        return total

    def predict_batch(
        self,
        exams: Sequence[ExamRecord],
        params: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        weights = self.vector_to_weights(params)
        actuals, predicteds = [], []
        for exam in exams:
            pred = self.predict_exam_total(exam, weights)
            actuals.append(exam.expect_grade)
            predicteds.append(pred)
        return np.array(actuals), np.array(predicteds)

    def l2_regularization(self, params: np.ndarray) -> float:
        """Penalize deviation from uniform weights (equal-weight baseline)."""
        reg = 0.0
        for (start, end) in self._slices:
            logits = params[start:end]
            w = softmax(logits)
            n = len(w)
            uniform = 1.0 / n
            reg += float(np.sum((w - uniform) ** 2))
        return reg


def compute_metrics(actuals: np.ndarray, predicteds: np.ndarray) -> Dict[str, float]:
    if len(actuals) == 0:
        return {"mae": float("inf"), "spearman": 0.0, "kendall": 0.0, "rmse": float("inf"), "bias": 0.0}
    mae = float(np.mean(np.abs(predicteds - actuals)))
    rmse = float(np.sqrt(np.mean((predicteds - actuals) ** 2)))
    bias = float(np.mean(predicteds - actuals))
    if len(set(actuals)) > 1 and len(set(predicteds)) > 1:
        spearman, _ = spearmanr(actuals, predicteds)
        kendall, _ = kendalltau(actuals, predicteds)
        spearman = float(spearman) if spearman == spearman else 0.0
        kendall = float(kendall) if kendall == kendall else 0.0
    else:
        spearman, kendall = 0.0, 0.0
    return {"mae": mae, "rmse": rmse, "bias": bias, "spearman": spearman, "kendall": kendall}


def make_objective(
    optimizer: WeightOptimizer,
    train_exams: Sequence[ExamRecord],
    spearman_weight: float,
    kendall_weight: float,
    l2_reg: float,
):
    def objective(params: np.ndarray) -> float:
        actuals, predicteds = optimizer.predict_batch(train_exams, params)
        metrics = compute_metrics(actuals, predicteds)
        loss = metrics["mae"] - spearman_weight * metrics["spearman"] - kendall_weight * metrics["kendall"]
        if l2_reg > 0:
            loss += l2_reg * optimizer.l2_regularization(params)
        return loss

    return objective


def equal_weight_params(question_specs: Dict[QuestionKey, List[str]]) -> np.ndarray:
    params: List[float] = []
    for key in sorted(question_specs.keys()):
        n = len(question_specs[key])
        params.extend([0.0] * n)
    return np.array(params, dtype=float)


def weights_to_config(
    weights: Dict[QuestionKey, Dict[str, float]],
    factors_config: Dict[str, Any],
) -> Dict[str, Any]:
    config: Dict[str, Any] = {}
    for (problem_id, qidx), fw in sorted(weights.items()):
        problem = config.setdefault(problem_id, {})
        qcfg = dict(factors_config.get(problem_id, {}).get(str(qidx), {}))
        qcfg["factor_weights"] = {k: round(v, 6) for k, v in fw.items()}
        problem[str(qidx)] = qcfg
    return config


def merge_configs(
    factors_config: Dict[str, Any],
    tuned_weights: Dict[str, Any],
) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}
    all_problems = set(factors_config) | set(tuned_weights)
    for pid in sorted(all_problems):
        merged[pid] = {}
        q_indices = set(factors_config.get(pid, {})) | set(tuned_weights.get(pid, {}))
        for qidx in sorted(q_indices, key=lambda x: int(x)):
            base = dict(factors_config.get(pid, {}).get(qidx, {}))
            tuned = tuned_weights.get(pid, {}).get(qidx, {})
            base.update({k: v for k, v in tuned.items() if k != "pre_extracted_factors"})
            if "pre_extracted_factors" not in base and "pre_extracted_factors" in tuned:
                base["pre_extracted_factors"] = tuned["pre_extracted_factors"]
            merged[pid][qidx] = base
    return merged


def config_to_weights(config: Dict[str, Any]) -> Dict[QuestionKey, Dict[str, float]]:
    weights: Dict[QuestionKey, Dict[str, float]] = {}
    for pid, questions in config.items():
        for qidx, qcfg in questions.items():
            fw = qcfg.get("factor_weights")
            if fw:
                weights[(pid, int(qidx))] = dict(fw)
    return weights


def rescore_jsonl(
    input_jsonl: Path,
    output_jsonl: Path,
    optimizer: WeightOptimizer,
    weights: Dict[QuestionKey, Dict[str, float]],
) -> None:
    per_exam_scores: Dict[str, float] = {}

    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    with input_jsonl.open("r", encoding="utf-8") as fin, output_jsonl.open("w", encoding="utf-8") as fout:
        for line in fin:
            line = line.strip()
            if not line:
                continue
            data = json.loads(line)

            if data.get("scoring_mode") == "per_question":
                result = data.get("result", {})
                key = (str(data.get("problem_id", "")), int(data.get("question_index", 0)))
                fw = weights.get(key, {})
                factor_names = list(result.get("factors") or list((result.get("factor_evaluation") or {}).keys()))
                use_weights = optimizer.matched_weights(factor_names, fw) if fw else None
                qmax = float(data.get("question_max", 10.0))
                scoring = optimizer.assessor.calculate_score(
                    factor_eval=result.get("factor_evaluation", {}),
                    syntax_errors=list(result.get("syntax_errors") or []),
                    question_max=qmax,
                    factor_weights=use_weights,
                    syntax_penalties=optimizer.syntax_penalties,
                )
                result["scoring"] = scoring
                result["final_score"] = scoring.get("scaled_score", 0.0)
                result["quality_score"] = scoring.get("final_score_on_10", 0.0)
                result["total_penalty"] = scoring.get("syntax_penalty_on_10", 0.0)
                data["result"] = result
                data["final_score"] = result["final_score"]
                data["quality_score"] = result["quality_score"]
                data["total_penalty"] = result["total_penalty"]

                row_id = str(data.get("id", ""))
                per_exam_scores[row_id] = per_exam_scores.get(row_id, 0.0) + float(result["final_score"])

            elif data.get("record_type") == "exam_summary":
                row_id = str(data.get("id", ""))
                if row_id in per_exam_scores:
                    data["predicted_total_score"] = round(per_exam_scores[row_id], 4)
                    data["has_error"] = False
                    details = data.get("question_details", [])
                    # question_details updated in prior per_question lines won't propagate here;
                    # rebuild from per_exam if needed — keep summary total only.

            fout.write(json.dumps(data, ensure_ascii=False) + "\n")


def print_metrics(label: str, metrics: Dict[str, float], n: int) -> None:
    print(f"\n--- {label} (n={n}) ---")
    print(f"  MAE      : {metrics['mae']:.4f}")
    print(f"  RMSE     : {metrics['rmse']:.4f}")
    print(f"  Bias     : {metrics['bias']:+.4f}")
    print(f"  Spearman : {metrics['spearman']:.4f}")
    print(f"  Kendall  : {metrics['kendall']:.4f}")


def run_tuning(args: argparse.Namespace) -> None:
    records = load_per_question_records(args.jsonl)
    if not records:
        raise SystemExit(f"No per_question records found in {args.jsonl}")

    exams = group_exams(records)
    print(f"Loaded {len(records)} question records -> {len(exams)} exams")

    factors_config: Dict[str, Any] = {}
    if args.factors_config.is_file():
        with args.factors_config.open("r", encoding="utf-8") as f:
            factors_config = json.load(f)
    else:
        factors_config = extract_factors_config(records, majority_vote=not args.strict_factors)
        if args.write_factors_config:
            args.factors_config.parent.mkdir(parents=True, exist_ok=True)
            with args.factors_config.open("w", encoding="utf-8") as f:
                json.dump(factors_config, f, ensure_ascii=False, indent=2)
            print(f"Wrote factors config: {args.factors_config}")

    question_specs = build_question_specs(records, factors_config)
    total_params = sum(len(v) for v in question_specs.values())
    print(f"Tuning {len(question_specs)} question groups, {total_params} weight parameters")

    assessor = MultiAgentAssessor(llm_client=MagicMock())
    optimizer = WeightOptimizer(exams, question_specs, assessor)

    all_problem_ids = sorted({e.problem_id for e in exams})
    if args.all_data:
        train_exams = list(exams)
        val_exams = list(exams)
        train_problems = set(all_problem_ids)
        val_problems = set(all_problem_ids)
    else:
        val_problems = set(args.val_problems.split(",")) if args.val_problems else {all_problem_ids[-1]}
        train_problems = set(args.train_problems.split(",")) if args.train_problems else set(all_problem_ids) - val_problems
        train_exams = [e for e in exams if e.problem_id in train_problems]
        val_exams = [e for e in exams if e.problem_id in val_problems]
    print(f"Train problems: {sorted(train_problems)} ({len(train_exams)} exams)")
    print(f"Val problems  : {sorted(val_problems)} ({len(val_exams)} exams)")

    baseline_params = equal_weight_params(question_specs)
    baseline_train_actual, baseline_train_pred = optimizer.predict_batch(train_exams, baseline_params)
    baseline_val_actual, baseline_val_pred = optimizer.predict_batch(val_exams, baseline_params)
    baseline_all_actual, baseline_all_pred = optimizer.predict_batch(exams, baseline_params)
    baseline_train = compute_metrics(baseline_train_actual, baseline_train_pred)
    baseline_val = compute_metrics(baseline_val_actual, baseline_val_pred)
    baseline_all = compute_metrics(baseline_all_actual, baseline_all_pred)

    print_metrics("Baseline TRAIN (equal weights)", baseline_train, len(train_exams))
    print_metrics("Baseline VAL   (equal weights)", baseline_val, len(val_exams))
    print_metrics("Baseline ALL   (equal weights)", baseline_all, len(exams))

    objective = make_objective(
        optimizer, train_exams, args.spearman_weight, args.kendall_weight, args.l2_reg
    )
    bounds = [(-3.0, 3.0)] * total_params

    print("\nRunning differential_evolution (this may take a minute)...")
    de_result = differential_evolution(
        objective,
        bounds,
        seed=args.seed,
        maxiter=args.maxiter,
        popsize=args.popsize,
        tol=1e-4,
        polish=True,
        workers=1,
    )
    best_params = de_result.x

    # Local refinement
    local = minimize(objective, best_params, method="Nelder-Mead", options={"maxiter": 2000, "xatol": 1e-4})
    if local.fun < de_result.fun:
        best_params = local.x

    tuned_weights = optimizer.vector_to_weights(best_params)
    tuned_train_actual, tuned_train_pred = optimizer.predict_batch(train_exams, best_params)
    tuned_val_actual, tuned_val_pred = optimizer.predict_batch(val_exams, best_params)
    tuned_all_actual, tuned_all_pred = optimizer.predict_batch(exams, best_params)
    tuned_train = compute_metrics(tuned_train_actual, tuned_train_pred)
    tuned_val = compute_metrics(tuned_val_actual, tuned_val_pred)
    tuned_all = compute_metrics(tuned_all_actual, tuned_all_pred)

    print_metrics("Tuned TRAIN", tuned_train, len(train_exams))
    print_metrics("Tuned VAL", tuned_val, len(val_exams))
    print_metrics("Tuned ALL", tuned_all, len(exams))

    print("\n=== Weight changes (ALL set) ===")
    print(f"  MAE     : {baseline_all['mae']:.4f} -> {tuned_all['mae']:.4f}  ({tuned_all['mae'] - baseline_all['mae']:+.4f})")
    print(f"  Spearman: {baseline_all['spearman']:.4f} -> {tuned_all['spearman']:.4f}  ({tuned_all['spearman'] - baseline_all['spearman']:+.4f})")
    print(f"  Kendall : {baseline_all['kendall']:.4f} -> {tuned_all['kendall']:.4f}  ({tuned_all['kendall'] - baseline_all['kendall']:+.4f})")

    if not args.all_data:
        print("\n=== Weight changes (val set) ===")
        print(f"  MAE     : {baseline_val['mae']:.4f} -> {tuned_val['mae']:.4f}  ({tuned_val['mae'] - baseline_val['mae']:+.4f})")
        print(f"  Spearman: {baseline_val['spearman']:.4f} -> {tuned_val['spearman']:.4f}  ({tuned_val['spearman'] - baseline_val['spearman']:+.4f})")
        print(f"  Kendall : {baseline_val['kendall']:.4f} -> {tuned_val['kendall']:.4f}  ({tuned_val['kendall'] - baseline_val['kendall']:+.4f})")

    tuned_config = weights_to_config(tuned_weights, factors_config)
    full_config = merge_configs(factors_config, tuned_config)

    args.output_config.parent.mkdir(parents=True, exist_ok=True)
    with args.output_config.open("w", encoding="utf-8") as f:
        json.dump(full_config, f, ensure_ascii=False, indent=2)
    print(f"\nSaved tuned config: {args.output_config}")

    if args.rescore_jsonl:
        out_path = args.rescore_jsonl
        rescore_jsonl(args.jsonl, out_path, optimizer, tuned_weights)
        print(f"\nRescored JSONL: {out_path}")
        print("Validate with:")
        print(f"  python evaluation/hcmus/calculate_metric.py {out_path}")

    print("\n=== Per-question tuned weights ===")
    for (pid, qidx), fw in sorted(tuned_weights.items()):
        print(f"\n  {pid} / Q{qidx}:")
        for name, w in sorted(fw.items(), key=lambda x: -x[1]):
            short = name[:80] + ("..." if len(name) > 80 else "")
            try:
                print(f"    {w:.3f}  {short}")
            except UnicodeEncodeError:
                print(f"    {w:.3f}  {short.encode('ascii', 'replace').decode('ascii')}")

    # Leave-one-problem-out quick report
    if args.loocv:
        print("\n=== Leave-one-problem-out (quick) ===")
        for held_out in all_problem_ids:
            tr = [e for e in exams if e.problem_id != held_out]
            te = [e for e in exams if e.problem_id == held_out]
            obj = make_objective(optimizer, tr, args.spearman_weight, args.kendall_weight, args.l2_reg)
            r = differential_evolution(
                obj, bounds, seed=args.seed, maxiter=max(30, args.maxiter // 3),
                popsize=max(5, args.popsize // 2), tol=1e-3, polish=False, workers=1,
            )
            _, pred = optimizer.predict_batch(te, r.x)
            m = compute_metrics(np.array([e.expect_grade for e in te]), pred)
            print(f"  Hold out {held_out}: MAE={m['mae']:.4f} Spearman={m['spearman']:.4f} Kendall={m['kendall']:.4f}")


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass

    parser = argparse.ArgumentParser(description="Tune HCMUS multi-agent factor weights offline")
    parser.add_argument("--jsonl", type=Path, default=DEFAULT_JSONL, help="Input JSONL from score_with_multi_agent.py")
    parser.add_argument("--factors-config", type=Path, default=DEFAULT_FACTORS_CONFIG, help="Config with pre_extracted_factors")
    parser.add_argument("--write-factors-config", action="store_true", help="Write extracted factors config if missing")
    parser.add_argument(
        "--strict-factors",
        action="store_true",
        help="Fail if factor names differ across students (default: majority vote)",
    )
    parser.add_argument("--output-config", type=Path, default=DEFAULT_TUNED_CONFIG, help="Output path for tuned weights JSON")
    parser.add_argument("--all-data", action="store_true", help="Optimize on full dataset (use with --l2-reg)")
    parser.add_argument("--l2-reg", type=float, default=0.0, help="L2 penalty toward uniform weights")
    parser.add_argument("--train-problems", type=str, default="", help="Comma-separated problem_ids for training (default: all except val)")
    parser.add_argument("--val-problems", type=str, default="96_final-123", help="Comma-separated problem_ids for validation")
    parser.add_argument("--spearman-weight", type=float, default=0.5, help="Reward Spearman in objective (subtracted from loss)")
    parser.add_argument("--kendall-weight", type=float, default=0.5, help="Reward Kendall in objective (subtracted from loss)")
    parser.add_argument("--maxiter", type=int, default=120, help="differential_evolution max iterations")
    parser.add_argument("--popsize", type=int, default=12, help="differential_evolution population multiplier")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--rescore-jsonl", type=Path, default=None, help="Write rescored JSONL with tuned weights applied")
    parser.add_argument(
        "--rescore-only",
        type=Path,
        default=None,
        metavar="TUNED_CONFIG",
        help="Skip optimization; rescore --jsonl using factor_weights from this config JSON",
    )
    parser.add_argument("--loocv", action="store_true", help="Run leave-one-problem-out cross-validation report")
    args = parser.parse_args()

    if args.rescore_only:
        if not args.rescore_jsonl:
            raise SystemExit("--rescore-only requires --rescore-jsonl")
        records = load_per_question_records(args.jsonl)
        exams = group_exams(records)
        with args.factors_config.open("r", encoding="utf-8") as f:
            factors_config = json.load(f)
        with args.rescore_only.open("r", encoding="utf-8") as f:
            tuned_config = json.load(f)
        question_specs = build_question_specs(records, factors_config)
        assessor = MultiAgentAssessor(llm_client=MagicMock())
        optimizer = WeightOptimizer(exams, question_specs, assessor)
        weights = config_to_weights(tuned_config)
        rescore_jsonl(args.jsonl, args.rescore_jsonl, optimizer, weights)
        print(f"Rescored JSONL: {args.rescore_jsonl}")
        print(f"  python evaluation/hcmus/calculate_metric.py {args.rescore_jsonl}")
        return

    run_tuning(args)


if __name__ == "__main__":
    main()
