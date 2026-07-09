# FAVE-RAG OpenAI Pilot Report

Run date: 2026-07-09  
Benchmark: `data/pilot/fave_bench_10.jsonl`  
Model provider: OpenAI  
Methods: LLM-only, Vanilla RAG Clean, Vanilla RAG Mixed, DeMo-style Mixed, FAVE-RAG Mixed

## 1. Executive Summary

The first real OpenAI pilot successfully ran end-to-end on the 10-item FAVE-RAG seed benchmark.

The main finding is:

> FAVE-RAG already detects many invalid evidence items, but this 10-item seed benchmark does not yet show a final-answer robustness gain over Vanilla RAG.

This is not a failure. It is useful pilot evidence. It says the current bottleneck is not API plumbing or evidence classification alone. The next step is to make the benchmark harder and more diagnostic: stronger true-but-inapplicable distractors, closed-book filtering, and conflict-type-specific analysis.

## 2. Main Accuracy Results

| Method | N | Clean Accuracy | Mixed Accuracy | Robustness Drop |
|---|---:|---:|---:|---:|
| LLM-only | 10 | - | 0.70 | - |
| Vanilla RAG Clean | 10 | 0.70 | - | - |
| Vanilla RAG Mixed | 10 | - | 0.70 | 0.00 |
| DeMo-style Mixed | 10 | - | 0.80 | -0.10 |
| FAVE-RAG Mixed | 10 | - | 0.70 | 0.00 |

Interpretation:

- Vanilla RAG did not collapse under mixed evidence on this seed set.
- DeMo-style reasoning performed best on final answer accuracy in this pilot.
- FAVE-RAG did not improve final answer accuracy yet, despite doing evidence arbitration.
- The expected paper figure, where Vanilla drops as invalid evidence increases and FAVE stays flatter, did not appear in this 10-item seed.

## 3. Evidence Conflict Detection

| Method | TP | FP | FN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|
| FAVE-RAG Mixed | 8 | 1 | 2 | 0.889 | 0.800 | 0.842 |

Interpretation:

- FAVE-RAG is already doing something meaningful: it identifies most rejected evidence items.
- The arbitration module is stronger than the final solving result suggests.
- The current weakness is downstream use of arbitration labels, not only classification.

## 4. Case-Level Pattern

Commonly solved correctly:

- `fave_0001`: Shannon capacity with SNR dB conversion.
- `fave_0002`: Spectral efficiency.
- `fave_0004`: SINR.
- `fave_0005`: Rayleigh outage probability.
- `fave_0010`: SNR dB to linear conversion.

Commonly problematic:

- `fave_0006`: BPSK BER. Outputs often used a close but differently approximated value, and the evaluator is sensitive to scientific notation formatting.
- `fave_0008`: MIMO capacity. Several methods produced a lower spectral efficiency than the current gold answer.
- `fave_0009`: Friis received power. Some outputs differed by orders of magnitude, suggesting either a calculation error or a benchmark/gold-answer review item.

Important note: `fave_0009` should be manually checked. Friis examples are easy to mis-scale, and this item may be contaminating the accuracy comparison if the gold or expected tolerance is not well calibrated.

## 5. Evaluation Caveats

The current evaluator is useful for quick pilot iteration, but it is not paper-grade.

Known issues:

- It handles normal decimal and `e` notation better than LaTeX-style scientific notation such as `3.3 × 10^{-5}`.
- It checks whether any extracted number is close to the gold number, which is more forgiving than strict final-answer parsing.
- It does not yet normalize units such as W, mW, Mbps, bps, bps/Hz.
- It does not distinguish arithmetic error from formula-selection error.

Before using this in a paper, we need:

- robust final-answer extraction,
- unit normalization,
- per-item tolerance rules,
- manual audit of gold answers,
- error labels such as formula, unit, arithmetic, and evidence-use error.

## 6. Research Interpretation

The pilot supports one part of the FAVE-RAG hypothesis:

> A validity-checking stage can detect true-but-inapplicable evidence with non-trivial F1.

But it does not yet support the stronger claim:

> FAVE-RAG improves final-answer robustness under mixed valid/invalid evidence.

Why the stronger claim did not appear yet:

- The benchmark has only 10 seed items.
- Some invalid evidence is too weak to fool the model.
- Several questions are solvable from parametric knowledge alone.
- GPT-style models often ignore bad evidence when the math is familiar.
- The FAVE solver prompt may be too cautious or may not exploit valid evidence better than DeMo-style prompting.

## 7. Next Actions

Priority 1: Audit the 10 seed items.

- Recalculate gold answers for `fave_0006`, `fave_0008`, and `fave_0009`.
- Add item-level tolerance and unit metadata.
- Confirm whether each invalid evidence item is genuinely true-but-inapplicable rather than obviously wrong.

Priority 2: Build `fave_bench_40`.

- Use the real `fave_candidate_40` file as a source pool.
- Add closed-book filtering: mark whether LLM-only solves each item.
- Keep separate layers:
  - closed-book solvable,
  - evidence-dependent,
  - ambiguous/contested.

Priority 3: Strengthen adversarial evidence.

- Add valid:invalid ratios: 2:1, 1:1, 1:2.
- Add 2-3 invalid evidence items per problem.
- Use subtle procedural distractors rather than obvious wrong statements.

Priority 4: Improve evaluation.

- Parse LaTeX scientific notation.
- Normalize common telecom units.
- Add error-type analysis.
- Report conflict detection by conflict type.

## 8. Bottom Line

This pilot is a useful first result, but not yet a publishable result.

The promising signal is evidence arbitration: FAVE-RAG achieved conflict detection F1 of 0.842.

The weak signal is final-answer robustness: FAVE-RAG did not beat Vanilla or DeMo-style prompting on the 10-item seed.

The correct next move is not to abandon the idea. It is to sharpen the benchmark so that it actually stresses the gap between relevance and validity.
