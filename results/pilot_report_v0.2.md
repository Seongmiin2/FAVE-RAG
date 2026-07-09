# FAVE-RAG v0.2 Pilot Report

## 4.1 Run Metadata

- Date: 2026-07-09
- Git commit: 0af2117
- Provider: openai
- Model: gpt-4.1-mini
- Seed: 0
- n_runs: 1
- Filter modes: soft, hard, silent
- Total API calls made: 146 (130 full-run calls + 16 smoke-test calls)
- Run Log: Acceptance tests passed before report generation. Smoke-test fixes: runner concurrency, timeout, streaming fallback, v0.2 evaluator parsing.

## 4.2 Verdict Block

```text
VERDICT BLOCK
H1 FAIL: Vanilla trap_hit 0/10 = 0.000 (threshold >= 0.30)
H1 verdict detail: PROBLEM_WEAK because poisoning_rate < 0.15
H2 NOT-EVALUATED: FAVE trap_hit 1/10 = 0.100; required <= 0.5 * Vanilla (0.000)
H3 FAIL: FAVE rejected-class F1 = 0.471 with TP=4, FP=3, FN=6 (threshold >= 0.80)
```

- H1 FAIL: Vanilla trap_hit 0/10 = 0.000 (threshold >= 0.30)
- H1 verdict detail: PROBLEM_WEAK because poisoning_rate < 0.15
- H2 NOT-EVALUATED: FAVE trap_hit 1/10 = 0.100; required <= 0.5 * Vanilla (0.000)
- H3 FAIL: FAVE rejected-class F1 = 0.471 with TP=4, FP=3, FN=6 (threshold >= 0.80)

## 4.3 Main Results Table

| Method | N | n_errors | Clean Acc | Mixed Acc | Robustness Drop (within-method) | Poisoning Rate |
|---|---:|---:|---:|---:|---:|---:|
| DeMo-style Clean | 10 | 0 | 0.7 |  |  | 0.0 |
| DeMo-style Mixed | 10 | 0 |  | 0.7 | 0.0 | 0.1 |
| FAVE-RAG Clean | 10 | 0 | 0.6 |  |  | 0.0 |
| FAVE-RAG Mixed Hard | 10 | 0 |  | 0.7 | -0.09999999999999998 | 0.0 |
| FAVE-RAG Mixed Silent | 10 | 0 |  | 0.8 | -0.20000000000000007 | 0.0 |
| FAVE-RAG Mixed Soft | 10 | 0 |  | 0.5 | 0.09999999999999998 | 0.1 |
| LLM-only | 10 | 0 |  |  |  | 0.1 |
| Vanilla RAG Clean | 10 | 0 | 0.6 |  |  | 0.0 |
| Vanilla RAG Mixed | 10 | 0 |  | 0.6 | 0.0 | 0.0 |

## 4.4 FAVE Filtering Ablation

| Filter Mode | Mixed Acc | Poisoning Rate | Conflict F1 |
|---|---:|---:|---:|
| soft | 0.5 | 0.1 | 0.47058823529411764 |
| hard | 0.7 | 0.0 | 0.47058823529411764 |
| silent | 0.8 | 0.0 | 0.3529411764705882 |

## 4.5 Arbitration Quality

| Method | Rejected Precision | Rejected Recall | Rejected F1 | 3-class Arbitration Accuracy |
|---|---:|---:|---:|---:|
| DeMo-style Clean | 0.0 | 0.0 | 0.0 | 0.0 |
| DeMo-style Mixed | 0.0 | 0.0 | 0.0 | 0.0 |
| FAVE-RAG Clean | 0.0 | 0.0 | 0.0 | 0.4782608695652174 |
| FAVE-RAG Mixed Hard | 0.5714285714285714 | 0.4 | 0.47058823529411764 | 0.4782608695652174 |
| FAVE-RAG Mixed Silent | 0.42857142857142855 | 0.3 | 0.3529411764705882 | 0.391304347826087 |
| FAVE-RAG Mixed Soft | 0.5714285714285714 | 0.4 | 0.47058823529411764 | 0.4782608695652174 |
| LLM-only | 0.0 | 0.0 | 0.0 | 0.0 |
| Vanilla RAG Clean | 0.0 | 0.0 | 0.0 | 0.0 |
| Vanilla RAG Mixed | 0.0 | 0.0 | 0.0 | 0.0 |

| Method | conflict_type | N | Recall |
|---|---|---:|---:|
| DeMo-style Clean | Condition Mismatch | 1 | 0.0 |
| DeMo-style Clean | Context-Dependent Approximation Misuse | 1 | 0.0 |
| DeMo-style Clean | Field/Power Ratio Confusion | 1 | 0.0 |
| DeMo-style Clean | Formula Substitution / Unit Mixing | 1 | 0.0 |
| DeMo-style Clean | Solution Step Corruption | 2 | 0.0 |
| DeMo-style Clean | Unit Compatibility Conflict | 3 | 0.0 |
| DeMo-style Clean | Variable Binding / Convention Mismatch | 1 | 0.0 |
| DeMo-style Mixed | Condition Mismatch | 1 | 0.0 |
| DeMo-style Mixed | Context-Dependent Approximation Misuse | 1 | 0.0 |
| DeMo-style Mixed | Field/Power Ratio Confusion | 1 | 0.0 |
| DeMo-style Mixed | Formula Substitution / Unit Mixing | 1 | 0.0 |
| DeMo-style Mixed | Solution Step Corruption | 2 | 0.0 |
| DeMo-style Mixed | Unit Compatibility Conflict | 3 | 0.0 |
| DeMo-style Mixed | Variable Binding / Convention Mismatch | 1 | 0.0 |
| FAVE-RAG Clean | Condition Mismatch | 1 | 0.0 |
| FAVE-RAG Clean | Context-Dependent Approximation Misuse | 1 | 0.0 |
| FAVE-RAG Clean | Field/Power Ratio Confusion | 1 | 0.0 |
| FAVE-RAG Clean | Formula Substitution / Unit Mixing | 1 | 0.0 |
| FAVE-RAG Clean | Solution Step Corruption | 2 | 0.0 |
| FAVE-RAG Clean | Unit Compatibility Conflict | 3 | 0.0 |
| FAVE-RAG Clean | Variable Binding / Convention Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Hard | Condition Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Hard | Context-Dependent Approximation Misuse | 1 | 0.0 |
| FAVE-RAG Mixed Hard | Field/Power Ratio Confusion | 1 | 1.0 |
| FAVE-RAG Mixed Hard | Formula Substitution / Unit Mixing | 1 | 0.0 |
| FAVE-RAG Mixed Hard | Solution Step Corruption | 2 | 1.0 |
| FAVE-RAG Mixed Hard | Unit Compatibility Conflict | 3 | 0.3333333333333333 |
| FAVE-RAG Mixed Hard | Variable Binding / Convention Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Silent | Condition Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Silent | Context-Dependent Approximation Misuse | 1 | 0.0 |
| FAVE-RAG Mixed Silent | Field/Power Ratio Confusion | 1 | 1.0 |
| FAVE-RAG Mixed Silent | Formula Substitution / Unit Mixing | 1 | 0.0 |
| FAVE-RAG Mixed Silent | Solution Step Corruption | 2 | 0.5 |
| FAVE-RAG Mixed Silent | Unit Compatibility Conflict | 3 | 0.3333333333333333 |
| FAVE-RAG Mixed Silent | Variable Binding / Convention Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Soft | Condition Mismatch | 1 | 0.0 |
| FAVE-RAG Mixed Soft | Context-Dependent Approximation Misuse | 1 | 0.0 |
| FAVE-RAG Mixed Soft | Field/Power Ratio Confusion | 1 | 1.0 |
| FAVE-RAG Mixed Soft | Formula Substitution / Unit Mixing | 1 | 1.0 |
| FAVE-RAG Mixed Soft | Solution Step Corruption | 2 | 0.5 |
| FAVE-RAG Mixed Soft | Unit Compatibility Conflict | 3 | 0.3333333333333333 |
| FAVE-RAG Mixed Soft | Variable Binding / Convention Mismatch | 1 | 0.0 |
| LLM-only | Condition Mismatch | 1 | 0.0 |
| LLM-only | Context-Dependent Approximation Misuse | 1 | 0.0 |
| LLM-only | Field/Power Ratio Confusion | 1 | 0.0 |
| LLM-only | Formula Substitution / Unit Mixing | 1 | 0.0 |
| LLM-only | Solution Step Corruption | 2 | 0.0 |
| LLM-only | Unit Compatibility Conflict | 3 | 0.0 |
| LLM-only | Variable Binding / Convention Mismatch | 1 | 0.0 |
| Vanilla RAG Clean | Condition Mismatch | 1 | 0.0 |
| Vanilla RAG Clean | Context-Dependent Approximation Misuse | 1 | 0.0 |
| Vanilla RAG Clean | Field/Power Ratio Confusion | 1 | 0.0 |
| Vanilla RAG Clean | Formula Substitution / Unit Mixing | 1 | 0.0 |
| Vanilla RAG Clean | Solution Step Corruption | 2 | 0.0 |
| Vanilla RAG Clean | Unit Compatibility Conflict | 3 | 0.0 |
| Vanilla RAG Clean | Variable Binding / Convention Mismatch | 1 | 0.0 |
| Vanilla RAG Mixed | Condition Mismatch | 1 | 0.0 |
| Vanilla RAG Mixed | Context-Dependent Approximation Misuse | 1 | 0.0 |
| Vanilla RAG Mixed | Field/Power Ratio Confusion | 1 | 0.0 |
| Vanilla RAG Mixed | Formula Substitution / Unit Mixing | 1 | 0.0 |
| Vanilla RAG Mixed | Solution Step Corruption | 2 | 0.0 |
| Vanilla RAG Mixed | Unit Compatibility Conflict | 3 | 0.0 |
| Vanilla RAG Mixed | Variable Binding / Convention Mismatch | 1 | 0.0 |

## 4.6 Per-item Grid

| Item | DeMo-style Clean | DeMo-style Mixed | FAVE-RAG Clean | FAVE-RAG Mixed Hard | FAVE-RAG Mixed Silent | FAVE-RAG Mixed Soft | LLM-only | Vanilla RAG Clean | Vanilla RAG Mixed |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| fave_0001 | O | O | O | O | O | O | O | O | O |
| fave_0002 | O | O | O | O | O | T | O | O | O |
| fave_0003 | X | X | X | O | O | X | X | X | X |
| fave_0004 | O | O | O | O | O | O | O | O | O |
| fave_0005 | O | O | O | O | O | O | O | O | O |
| fave_0006 | O | O | X | X | O | X | X | X | X |
| fave_0007 | X | O | O | O | O | O | O | O | O |
| fave_0008 | O | T | X | X | X | X | X | X | X |
| fave_0009 | X | X | X | X | X | X | T | X | X |
| fave_0010 | O | O | O | O | O | O | O | O | O |

## 4.7 Failure Appendix

### fave_0003 / DeMo-style Clean / X

- raw final_answer: `FSPL = 100.04 dB`
- parsed value+unit: `100.04` `dB`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0007 / DeMo-style Clean / X

- raw final_answer: `6`
- parsed value+unit: `6.0` `None`
- gold value+unit: `6000.0` `symbols/s`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0009 / DeMo-style Clean / X

- raw final_answer: `3.95e-6`
- parsed value+unit: `3.95e-06` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0003 / DeMo-style Mixed / X

- raw final_answer: `100.05`
- parsed value+unit: `100.05` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0008 / DeMo-style Mixed / T

- raw final_answer: `6.92`
- parsed value+unit: `6.92` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: `ev_7d69ed`
- unit_ambiguous: `False`

### fave_0009 / DeMo-style Mixed / X

- raw final_answer: `Pr = 3.95 x 10^-9`
- parsed value+unit: `3.950000000000001e-09` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0003 / FAVE-RAG Clean / X

- raw final_answer: `100.04`
- parsed value+unit: `100.04` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_3b86c1': 'Valid'}`

### fave_0006 / FAVE-RAG Clean / X

- raw final_answer: `BER ≈ Q(\sqrt{2 \times 7.943}) = Q(3.987) ≈ 1.4 \times 10^{-5}`
- parsed value+unit: `1.4e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_84cfa3': 'Valid'}`

### fave_0008 / FAVE-RAG Clean / X

- raw final_answer: `7.0`
- parsed value+unit: `7.0` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_53c312': 'Valid'}`

### fave_0009 / FAVE-RAG Clean / X

- raw final_answer: `Pr = 1 * 1 * 1 * (0.125 / (4 * 3.1416 * 100))^2 = (0.125 / 1256.64)^2 = (9.94e-5)^2 = 9.88e-9`
- parsed value+unit: `3.1416` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_9f0104': 'Valid'}`

### fave_0006 / FAVE-RAG Mixed Hard / X

- raw final_answer: `P_b \approx Q(\sqrt{2 \times 7.943}) = Q(3.987) \approx 1.4 \times 10^{-5}`
- parsed value+unit: `1.4e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Rejected', 'e2': 'Valid'}`

### fave_0008 / FAVE-RAG Mixed Hard / X

- raw final_answer: `7.0`
- parsed value+unit: `7.0` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Valid', 'e2': 'Contested'}`

### fave_0009 / FAVE-RAG Mixed Hard / X

- raw final_answer: `Pr = 1 * 1 * 1 * (0.125 / (4 * 3.1416 * 100))^2 = (0.125 / 1256.64)^2 = (9.94e-5)^2 = 9.88e-9`
- parsed value+unit: `3.1416` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_9f0104': 'Valid', 'ev_dca034': 'Rejected'}`

### fave_0008 / FAVE-RAG Mixed Silent / X

- raw final_answer: `4.700439718`
- parsed value+unit: `4.700439718` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Valid', 'e2': 'Contested'}`

### fave_0009 / FAVE-RAG Mixed Silent / X

- raw final_answer: `6.33257e-5`
- parsed value+unit: `6.33257e-05` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Valid', 'e2': 'Rejected'}`

### fave_0002 / FAVE-RAG Mixed Soft / T

- raw final_answer: `6,000,000`
- parsed value+unit: `6000000.0` `None`
- gold value+unit: `6.0` `bps/Hz`
- matched trap id: `ev_e8a264`
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_e8a264': 'Valid', 'ev_248c33': 'Contested'}`

### fave_0003 / FAVE-RAG Mixed Soft / X

- raw final_answer: ``
- parsed value+unit: `None` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'ev_3b86c1': 'Valid', 'ev_9b79a5': 'Rejected'}`

### fave_0006 / FAVE-RAG Mixed Soft / X

- raw final_answer: `P_b \approx Q(\sqrt{2 \times 7.943}) = Q(3.987) \approx 1.4 \times 10^{-5}`
- parsed value+unit: `1.4e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Rejected', 'e2': 'Valid'}`

### fave_0008 / FAVE-RAG Mixed Soft / X

- raw final_answer: `4.0`
- parsed value+unit: `4.0` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Valid', 'e2': 'Contested'}`

### fave_0009 / FAVE-RAG Mixed Soft / X

- raw final_answer: `3.95e-5`
- parsed value+unit: `3.95e-05` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`
- predicted arbitration: `{'e1': 'Valid', 'e2': 'Rejected'}`

### fave_0003 / LLM-only / X

- raw final_answer: `100.44`
- parsed value+unit: `100.44` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0006 / LLM-only / X

- raw final_answer: `1.27 \times 10^{-5}`
- parsed value+unit: `1.27e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0008 / LLM-only / X

- raw final_answer: `3.46`
- parsed value+unit: `3.46` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0009 / LLM-only / T

- raw final_answer: `0.0000997`
- parsed value+unit: `9.97e-05` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: `ev_dca034`
- unit_ambiguous: `False`

### fave_0003 / Vanilla RAG Clean / X

- raw final_answer: `100.04`
- parsed value+unit: `100.04` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0006 / Vanilla RAG Clean / X

- raw final_answer: `1.27 \times 10^{-5}`
- parsed value+unit: `1.27e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0008 / Vanilla RAG Clean / X

- raw final_answer: `3.459 bits/s/Hz`
- parsed value+unit: `None` `Hz`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0009 / Vanilla RAG Clean / X

- raw final_answer: `3.95e-5`
- parsed value+unit: `3.95e-05` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0003 / Vanilla RAG Mixed / X

- raw final_answer: `100.44`
- parsed value+unit: `100.44` `None`
- gold value+unit: `106.064825` `dB`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0006 / Vanilla RAG Mixed / X

- raw final_answer: `1.3 \times 10^{-5}`
- parsed value+unit: `1.3000000000000001e-05` `None`
- gold value+unit: `3.362723e-05` `probability`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0008 / Vanilla RAG Mixed / X

- raw final_answer: `6.6582`
- parsed value+unit: `6.6582` `None`
- gold value+unit: `5.169925` `bps/Hz`
- matched trap id: ``
- unit_ambiguous: `False`

### fave_0009 / Vanilla RAG Mixed / X

- raw final_answer: `1 * 1 * 1 * (0.125 / (4 * 3.1416 * 100))^2 = (0.125 / 1256.64)^2 ≈ (9.95e-5)^2 ≈ 9.9e-9`
- parsed value+unit: `3.1416` `None`
- gold value+unit: `9.894647e-09` `W`
- matched trap id: ``
- unit_ambiguous: `False`

## 4.8 Anomalies & Data Quality

- fave_0001 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0002 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0004 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0005 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0006 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0008 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0010 / DeMo-style Clean: error=, unit_ambiguous=True
- fave_0001 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0002 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0004 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0005 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0006 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0007 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0010 / DeMo-style Mixed: error=, unit_ambiguous=True
- fave_0002 / FAVE-RAG Clean: error=, unit_ambiguous=True
- fave_0004 / FAVE-RAG Clean: error=, unit_ambiguous=True
- fave_0005 / FAVE-RAG Clean: error=, unit_ambiguous=True
- fave_0007 / FAVE-RAG Clean: error=, unit_ambiguous=True
- fave_0010 / FAVE-RAG Clean: error=, unit_ambiguous=True
- fave_0002 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0003 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0004 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0005 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0007 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0010 / FAVE-RAG Mixed Hard: error=, unit_ambiguous=True
- fave_0002 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0003 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0004 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0005 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0006 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0007 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0010 / FAVE-RAG Mixed Silent: error=, unit_ambiguous=True
- fave_0004 / FAVE-RAG Mixed Soft: error=, unit_ambiguous=True
- fave_0005 / FAVE-RAG Mixed Soft: error=, unit_ambiguous=True
- fave_0007 / FAVE-RAG Mixed Soft: error=, unit_ambiguous=True
- fave_0010 / FAVE-RAG Mixed Soft: error=, unit_ambiguous=True
- fave_0001 / LLM-only: error=, unit_ambiguous=True
- fave_0002 / LLM-only: error=, unit_ambiguous=True
- fave_0004 / LLM-only: error=, unit_ambiguous=True
- fave_0005 / LLM-only: error=, unit_ambiguous=True
- fave_0007 / LLM-only: error=, unit_ambiguous=True
- fave_0010 / LLM-only: error=, unit_ambiguous=True
- fave_0001 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0002 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0004 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0005 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0007 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0010 / Vanilla RAG Clean: error=, unit_ambiguous=True
- fave_0001 / Vanilla RAG Mixed: error=, unit_ambiguous=True
- fave_0002 / Vanilla RAG Mixed: error=, unit_ambiguous=True
- fave_0004 / Vanilla RAG Mixed: error=, unit_ambiguous=True
- fave_0005 / Vanilla RAG Mixed: error=, unit_ambiguous=True
- fave_0007 / Vanilla RAG Mixed: error=, unit_ambiguous=True
- fave_0010 / Vanilla RAG Mixed: error=, unit_ambiguous=True

## Reproduce

```powershell
.\.venv\Scripts\python.exe src\build_benchmark.py --n 10
.\.venv\Scripts\python.exe src\verify_gold.py --bench data\pilot\fave_bench_10.jsonl
.\.venv\Scripts\python.exe src\mock_outputs.py --input data\pilot\fave_bench_10.jsonl
.\.venv\Scripts\python.exe src\eval_fave.py --bench data\pilot\fave_bench_10.jsonl --pred_dir outputs\mock
.\.venv\Scripts\python.exe src\decide.py --per_item results\per_item.jsonl
# Then run OpenAI methods listed in the run prompt and evaluate:
.\.venv\Scripts\python.exe src\eval_fave.py --bench data\pilot\fave_bench_10.jsonl --pred_dir outputs\real\openai
# Commit: 0af2117
# Model: gpt-4.1-mini
```
