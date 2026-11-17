# Exploratory chronological backtest — 17 November 2026

This is a work-in-progress analysis, not evidence that the current question-level scores are calibrated or that any particular question will appear. `python scripts/backtest_topics.py` reproduces the fold data in `data/topic-backtest.json`.

For each of seven A/B pairs, the historical predictors use only dated exams strictly before that pair's A date; the current-A predictor uses that A exam. The target B exam and later exams are excluded. Each method ranks nine broad topics; this exercise measures how much of the target B exam falls in five topic slots. Where scores tie at the cutoff, credit is averaged over all equivalent tie breaks. Thus the result is expected coverage under random tie breaking, not necessarily the coverage of any particular selection. Each exam has equal weight in the overall mean.

| Predictor | Mean fraction of B questions covered | Mean fraction of distinct B topics covered |
| --- | ---: | ---: |
| Earlier exams, topic frequency | 56.5% | 57.8% |
| Earlier B exams, topic frequency | 58.4% | 60.5% |
| Topics in that pair's A exam | 61.0% | 58.9% |
| Equal combination of the above three | 61.0% | 62.3% |
| Uniform random five of nine topics (expected) | 55.6% | 55.6% |

For the hybrid, coverage by fold was 66.7%, 60.0%, 70.0%, 60.0%, 80.0%, 40.0%, and 50.0%. The 2025 summer target is an example of a substantial miss. The first fold had no earlier dated exams and no earlier B exams; its history-only predictions are ties. The small and dependent sample cannot support a reliable winner, confidence calibration, or causal claim. Methods and broad primary-topic labels were chosen with knowledge of the corpus; those labels were assigned retrospectively. This is exploratory evaluation, not a genuine pre-registered prediction. The fixed five-topic task differs from the ten-question mock and ignores subtopic shifts within a broad category. A retrospective category hit is not evidence that the exact wording, question, or required reasoning was predicted.

The live 1–100 skill scores use manually mapped skill evidence, latest-A indicators, smoothing and weights. This experiment does **not** reconstruct or validate those scores, nor does it test whether the chosen ten questions would have matched previous exams. Do not replace the live ranking solely because the hybrid has the highest topic-recall mean in this tiny exploratory sample. The next useful checks are time-bounded reconstruction of skill evidence, audit of labels against original source questions, and a prospective holdout or other genuinely independent evidence.
