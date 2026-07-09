# FAVE-RAG Pilot

FAVE-RAG tests a narrow but important RAG failure mode:

> Relevance does not guarantee validity.

The project focuses on true-but-inapplicable procedural evidence in telecommunications math. The evidence may be factually correct in general, but invalid for the current problem because of units, variable binding, applicability conditions, physical constraints, or corrupted solution steps.

This is intentionally different from robust RAG settings where invalid evidence is mostly irrelevant, factually false, contradictory, or malicious. The pilot benchmark should make that distinction explicit enough to survive the obvious reviewer question: "Is this just CRAG or Astute RAG in a telecom domain?"

## Research Claim

Existing retrieval evaluators can flag false, irrelevant, or conflicting evidence. FAVE-RAG instead evaluates whether a model can reject evidence that is topically relevant and often true, but contextually inapplicable to the current mathematical procedure.

Example:

```text
Question: Given B = 10 MHz and SNR = 20 dB, calculate Shannon capacity.
True formula: C = B log2(1 + SNR)
Invalid use: substituting SNR = 20 directly instead of converting 20 dB to 100.
```

## Project Structure

```text
data/
  raw/
  pilot/
knowledge_cards/
prompts/
outputs/
  mock/
  real/
results/
src/
  common/
```

## Run The Mock Pipeline

No paid LLM API is used.

If `python` is not recognized on Windows, install Python and enable "Add python.exe to PATH", or use the Windows launcher command `py` after installation.

```powershell
python src/build_benchmark.py --n 10
python src/mock_outputs.py --input data/pilot/fave_bench_10.jsonl
python src/eval_fave.py --bench data/pilot/fave_bench_10.jsonl --pred_dir outputs/mock
```

Optional public dataset access check:

```powershell
pip install -r requirements.txt
python src/load_wirelessmath.py
```

## Current Outputs

The pipeline creates:

```text
data/pilot/fave_bench_10.jsonl
data/raw/wirelessmathbench_full.jsonl
data/raw/wirelessmathbench_sample.jsonl
data/raw/wirelessmathbench_xl_full.jsonl
data/raw/wirelessmathbench_xl_sample.jsonl
data/raw/fave_candidate_40.jsonl
data/raw/fave_candidate_40.csv
outputs/mock/llm_only.jsonl
outputs/mock/vanilla_clean.jsonl
outputs/mock/vanilla_mixed.jsonl
outputs/mock/demo_mixed.jsonl
outputs/mock/fave_mixed.jsonl
results/fave_summary.csv
results/fave_conflict_detection.csv
```

This repository already includes the seed `fave_bench_10.jsonl` and example result CSVs so the research design can be inspected before Python is configured.

## Data Collection Status

Real Hugging Face dataset access was tested on July 8, 2026.

```text
XINLI1997/WirelessMathBench
- split: train
- rows: 587
- columns: id, type, background, question_text, options, correct_answer, equation, domain
- saved full split: data/raw/wirelessmathbench_full.jsonl
- saved sample: data/raw/wirelessmathbench_sample.jsonl

XINLI1997/WirelessMATHBench-XL
- splits: train, test
- selected split: train
- rows: 3227
- columns: question_id, paper_id, type, background, question_text, equation, options, correct_answer, prompt
- saved full split: data/raw/wirelessmathbench_xl_full.jsonl
- saved sample: data/raw/wirelessmathbench_xl_sample.jsonl
```

Candidate extraction:

```powershell
python src/prepare_real_candidates.py --n 40
```

This creates actual dataset-derived FAVE annotation candidates:

```text
data/raw/fave_candidate_40.jsonl
data/raw/fave_candidate_40.csv
```

The current `fave_candidate_40` file was selected from 3814 scored real rows. These rows are not yet final FAVE benchmark rows. They need gold formula, unit, valid evidence, invalid evidence, and arbitration labels before being used as evaluated benchmark items.

## Real LLM Experiments

After adding `OPENAI_API_KEY` to `.env`, run:

```powershell
python src/run_experiment.py --method llm_only
python src/run_experiment.py --method vanilla_clean
python src/run_experiment.py --method vanilla_mixed
python src/run_experiment.py --method demo_mixed
python src/eval_fave.py --bench data/pilot/fave_bench_10.jsonl --pred_dir outputs/real/openai
```

The current real runner writes provider-specific outputs under `outputs/real/{provider}/` and intentionally stops if the required API key is missing.

## OpenAI Pilot Result

The first real OpenAI run on the 10-item seed benchmark completed on July 9, 2026.

```text
LLM-only mixed accuracy: 0.70
Vanilla RAG clean accuracy: 0.70
Vanilla RAG mixed accuracy: 0.70
DeMo-style mixed accuracy: 0.80
FAVE-RAG mixed accuracy: 0.70
FAVE-RAG conflict detection F1: 0.842
```

Interpretation: the validity checker is already detecting many rejected evidence items, but the current 10-item seed does not yet show a robustness gain over Vanilla RAG. This means the next benchmark iteration should strengthen true-but-inapplicable distractors, add more closed-book filtered items, and inspect conflict-type-specific failures.

## Benchmark Schema

Each row contains:

```text
id
source
question
gold_answer
gold_formula
required_variables
required_units
valid_evidence
invalid_evidence
contested_evidence
clean_context
mixed_context
expected_arbitration
```

## Pilot Design

Week 1:
Create 10 formula cards and 40 candidate problems. Split candidates by closed-book solvability so contamination is interpretable.

Week 2:
Generate controlled invalid evidence across six conflict types. Use multiple invalid evidence items per problem and vary valid:invalid ratios.

Week 3:
Run LLM-only, Vanilla RAG, CRAG-style, DeMo-style, and FAVE-RAG with two models at temperature 0.

Week 4:
Analyze accuracy versus invalid evidence ratio, conflict detection F1, constraint violation rate, and case studies.

## Required Baselines For A Paper

Vanilla RAG alone is not enough. The pilot should include at least:

- LLM-only
- Vanilla RAG
- CRAG-style retrieval evaluator
- DeMo-style decomposed reasoning
- FAVE-RAG arbitration plus solving

The decisive experiment is whether a factuality-oriented filter fails on true-but-inapplicable evidence while FAVE-RAG rejects it.

## Known Limitations

The current outputs are mock outputs for plumbing and evaluation only.

The 10 examples are hand-crafted seed items, not yet a benchmark. Before claiming research results, expand to 40-50 items, run LLM-only filtering, and get at least a small double-labeling set with agreement such as Cohen's kappa.

## Next Steps

1. Add `closed_book_layer`: whether each problem is solved correctly without evidence.
2. Add mixed context ratios: 2:1, 1:1, 1:2 valid-to-invalid.
3. Implement real LLM runners under `outputs/real`.
4. Add CRAG-style factuality baseline.
5. Double-label at least 30 evidence items with a telecom-aware annotator.
