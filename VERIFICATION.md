# Verification — 2026-11-14

Local content validation passed: 294 generated HTML pages, 3,096 internal links, 182 historical questions with solutions, 30 forecast exercises, and seven A/B pairs. Mathematical checks independently recompute the Vigenere strings, RSA remainders, DH key, OTP transformation, birthday approximation, key counts and BTC change/fee examples. The new October PDF is byte-for-byte identical to the provided file; it has six pages and no annotations. Its cover and question pages were visually inspected. Original local study files were read without modification.

Connected Brave browser verification used the browser tool, without a Playwright process fallback. Confirmed:

- The latest-exam collection contains exactly ten questions; shuffled correct selections score 100/100.
- Forecast simulation 1 contains exactly ten questions; nine correct selections plus one deliberate mistake score 90/100.
- Wrong-only review shows one item; retry starts the same missed question with an eight-minute timer.
- Practice mode shows immediate feedback and an expandable, substantive answer after selection.
- The full bank displays 182 questions; searching Q163 finds the August question and its new explanation.
- Prediction priority and text filters narrow 30 → 3 → 1 items. Marking the last item mastered and enabling pending-only produces the empty state. The checkbox persists on reload and was reset after testing.
- Desktop at 1429×688 and mobile at 390×844 show no page-level horizontal overflow. Tables intentionally scroll within their own containers on narrow screens.
- No browser console errors were observed in these flows. Local test progress is on localhost, separate from the published site's storage.
- Four historical questions with explicit source acceptance notes now grade all accepted alternatives. In a browser test, choosing the RSA option for Q013 (all alternatives accepted in its source) scored 100 and marked all four alternatives accepted; the explanation explicitly says there is no unique defensible answer as worded. Q021, Q038 and Q055 accept original alternatives A and B.

## Visual fidelity review

Reference: the live upstream `index.html#setup`, retained as the design reference rather than a new generated concept. Browser screenshots of the reference and implementation were inspected with `view_image`; QA images remain outside the repository.

| Comparison point | Reference / implementation | Result |
| --- | --- | --- |
| Main workflow | Setup → exam/practice → review/retry | Preserved and exercised |
| RTL structure | Right-to-left questions, answer sheet, top navigation | Preserved |
| Typography | IBM Plex Sans Hebrew, Suez One headings, IBM Plex Mono | Preserved; missing font import on new reading pages was found and fixed |
| Palette | Existing light/dark variables, blue accent, green/red feedback | Preserved |
| Surfaces and spacing | Bordered panels, rounded controls, restrained reading width | Existing components retained; new reading sections follow the same tokens |
| Responsive behavior | Wrapping navigation and stacked mobile layout | Checked at 390 pixels; no clipped primary content |
| Visible copy | Existing quiz controls remain | Intentional additions: new-study navigation, collection name, solution disclosures and attribution |

The new reading pages use a document layout and accessible disclosures rather than copying the quiz's two-column layout. This is an intentional extension for long explanations. The implementation was checked against the reference design; no material visual mismatch remained in the inspected states. Print CSS and before/after-print handlers are included; a physical printout was not tested.

## Mandatory answer-order follow-up

- Reloaded the latest-exam reading page: eight of ten question orders changed in the observed random draw, and all ten displayed answer keys matched their new positions.
- All 30 forecast reading-page keys matched the shuffled choices. Checked an archived old exercise and Q021 with two accepted alternatives; their letters and answer text matched the displayed order.
- Checked all 60 visible question-bank cards with answers enabled against source answer identities, including multi-answer questions. Correct choices occupied all four positions. HTML subscript markup was normalized for the comparison.
- Generated two printable ten-question versions and verified all 20 answer-key entries against the displayed choices and source answers.
- Submitted a latest-exam question whose correct choice was displayed at B; it was graded correct and retained that position in review. No browser console errors were observed.
- Automated checks exhaust all 24 permutations and 288 grading cases. Shuffling cannot be disabled by a previous saved preference. Original PDFs retain their original order; generated learning and print views shuffle automatically.

## Forecast review and multiple-choice filtering

- All 30 current forecast questions now contain a derivation, one explanation for the correct option, three explicit distractor explanations and a note on assumptions. Browser inspection found 120 option explanations across the 30 forecast cards. See `FORECAST_REVIEW.md` for the corrected claims and independent calculation checks.
- In practice mode, the revised fee question appeared with the correct option at D. It was graded correctly, and the expanded solution contained all four explanations identified by option text.
- The archive filter defaults to “בלי שאלות פתוחות”. Archive document 01 showed 12 multiple-choice sections and hid five open sections. Unchecking revealed all five, and that choice persisted on reload. Re-enabling the filter and opening document 03 showed 12 multiple-choice sections with its four open sections hidden.
- The same preference appeared checked on the interactive entry page. The archive index displayed multiple-choice counts. At a 390-pixel mobile viewport, the page width was 375 pixels with no horizontal overflow. No console errors were observed in these flows. The preference was restored to multiple-choice-only after testing.

## Earlier historical-answer scope

The 162 imported explanations were mapped by source filename and original question number and retain provenance. Their complete semantics were not independently re-proved one by one in this update. The 20 new exam explanations and ten new forecast variants received targeted content and arithmetic review. Historical broad-topic assignments are coarse; combined questions can test several mechanisms. The old forecast audit is an explicit, conservative manual classification of exercise coverage. No claim is made that the new ranking has a measured out-of-sample predictive accuracy.
