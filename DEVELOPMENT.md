# Build and validation

The site is a static fork of `salimkh25/cyber-security-exams`, retaining the interactive quiz and original resources. Python 3 and Node.js are used for generation and validation; no Python third-party packages are required.

```text
python scripts/build.py
python scripts/validate.py
python -m http.server 8765 --bind 127.0.0.1
```

Open `http://127.0.0.1:8765/`. GitHub Pages serves `main` at the repository root. No server-side data collection or API is used. Google Fonts has local font fallbacks.

Edit the sources in `scripts/index.template.html`, `scripts/content.py`, `scripts/forecast.py`, the inherited question bank under `מאגר שאלות`, and the imported source records under `data`. HTML pages and analytical JSON are generated. Do not edit generated output alone.

The reviewed forecast explanations and clarified stems are owned by `scripts/forecast_review.py`. Each option has a structured explanation tied to its text and canonical identity. `scripts/test_forecast_content.py` checks that every forecast question remains single-answer multiple choice and that all four explanations are present; it also independently checks calculations. See `FORECAST_REVIEW.md` for the content-review findings.

The “בלי שאלות פתוחות” preference is shared by the quiz entry page and archive pages through `study.js`. It defaults on and hides archive articles explicitly marked `data-question-type="open"`. The original 2022 open-section headings identify 26 archived occurrences across duplicate documents; all historical interactive questions and all predictions are explicitly typed multiple-choice. Print views respect the active archive filter.

The 182 historical question records represent 186 dated occurrences across 18 exam dates. Duplicate files for one date count once. Seven verified A/B pairs feed the comparison; special sessions and undated sample papers are excluded from pair statistics. The 2022 comparison uses multiple-choice questions only; its open questions remain available in the full solution archive.

Thirty forecast exercises are kept separate from historical statistics. Ten are new variants, and twenty are reused exercises from the October 17 practice set, selected again with updated evidence. Topic rankings are study priorities, not calibrated probabilities. The October forecast audit is an explicit manual coding of skills covered by its 50 exercises, not a claim about a student's expected grade.

Validation covers solution coverage, internal links and anchors, evidence references, question uniqueness, collection sizes, dated occurrences, pairing statistics, JavaScript syntax, and independently computed Vigenere, RSA, Diffie–Hellman, OTP, birthday and transaction arithmetic.

Browser verification checks shuffled answers, a 100-point latest-exam submission, a 90-point forecast submission with one intentional wrong answer, wrong-only review and retry, immediate practice explanations, search and priority filters, progress persistence, desktop and 390-pixel mobile layouts. Browser tests are documented in `VERIFICATION.md`; they are not replayed by the CI job.

The inherited solutions are attributed to the supplied organized-exams folder; they are not represented as official lecturer explanations. The October PDF explicitly marks option A as correct for all ten questions. Imported explanations may refer to original answer letters, while the quiz shuffles choices; the interface explains this and always shows the correct answer text.

Answer ordering is mandatory. `answer-order.js` supplies Fisher–Yates permutations for each new quiz/practice attempt, each generated print version, bank rendering, and every reading-page load (latest exam, forecasts, standalone solutions and old exercises). Source answer indices remain canonical for grading. Active attempts and their result views keep the same order. A repeated question seed reproduces the question selection, while answer positions are drawn afresh. Random draws can legitimately repeat an order or put the correct choice first.

Reading pages include varied static fallback orders and matching answer keys; `study.js` reshuffles the choices and regenerates the displayed letters on load. Historical explanation letters are explicitly identified as source references. Original PDF files remain unmodified archival sources. Inherited standalone HTML exams and the old quiz entry point redirect to the maintained app, which provides shuffled practice and printable versions.

`scripts/test-answer-order.cjs`, invoked by validation/CI, exhausts all 24 four-choice permutations and 288 grading cases against the generated quiz's actual grading/key functions. It also verifies that legacy shuffle preferences cannot disable ordering.
