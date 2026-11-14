# Forecast content review — 14 November 2026

All 30 current retake exercises were reviewed, including every keyed answer and all 90 distractors. The selected answer identities did not need changing. Each current solution now has a derivation, four separate explanations identified by option text, assumptions/limits, and technical references where applicable. They are authored study explanations, not official lecturer solutions.

The new source is `scripts/forecast_review.py`. Twenty question scenarios still originate in the October practice set; their November explanations have been rewritten and explicitly marked as reviewed. The historical October archive is preserved separately. Unrelated old-exam explanations are no longer appended inside the ten new variants, which avoids mixing two different sets of numbers in one solution.

## Corrections and clarified assumptions

| Exercises | Review result |
| --- | --- |
| P01, P16 | Recomputed every offered RSA alternative. Distinguished verification, private-exponent inversion, modulus n, and the explicitly specified φ(n) condition. |
| P02 | Distinguished the direct issuer's public key from the trust anchor and the website key. |
| P03 | Made Alice and the two-output transaction explicit; rechecked change, fees, and every distractor's sums. |
| P04 | Made the target different from the original and asked for a formula valid for every eligible pair. This removes special-case ambiguity in the XOR distractors. |
| P05, P17 | Separated same-origin XSS from cross-origin CSRF. P17 explicitly accepts a normal POST form; no unstated preflight protection is assumed. |
| P06 | Explained all three composition methods and why the classical-cipher distractor is unrelated. |
| P07 | Specified distinct inputs and the ideal distribution. Verified the exact birthday probability crosses 50% at 4,823 inputs (about 50.0009%), consistent with the approximation. |
| P08 | Distinguished confirmations from miner signatures and explained the probabilistic, assumption-dependent guarantee. |
| P09, P10, P21 | Recomputed DH, Vigenère and key counts; each numerical distractor now has its own explanation. |
| P11, P12 | Distinguished SCT promises, inclusion, revocation status, privacy and certificate validation. |
| P13 | Added at least five blocks, unchanged IV and raw-block decryption before padding checks. Explained unpredictable P4 changes versus the exact corresponding bit flip in P5. |
| P14 | Removed the overgeneralization from perfect trees to every full binary tree. Distinguished sibling hashes from positions, known leaf data and the trusted root. |
| P15, P23 | Corrected the inherited password-hash example: an unknown original password does not automatically make a targeted hash attack a second-preimage attack. |
| P18 | Distinguished key-hash matching from signature verification and avoided claiming that every SIGHASH mode commits to every transaction field. |
| P19 | Corrected the claim that syntactic validity alone rules out an earlier TLS failure. The question now explicitly reaches Finished with matching keys and identifies the historical TLS 1.2 model. |
| P20 | Distinguished a network interception position from TLS decryption; discussed metadata and availability limits. |
| P22 | Removed unrelated two-block/padding boilerplate; reasoned directly about P, Q, P and block-cipher injectivity. |
| P24–P28 | Checked salts, normalized origins, HSTS preload, CSP nonces and parameter binding against the relevant definitions; explained each distractor separately. |
| P29 | Made the uniform 16-bit space explicit and distinguished TXID guessing from total DNS-poisoning success. |
| P30 | Distinguished incomplete HTTP requests from half-open TCP connections and clarified why an idle timeout alone can be insufficient. |

## Validation and limits

`scripts/test_forecast_content.py` checks 30 four-option, single-answer questions and 120 matching option explanations. It independently checks all RSA choices, transaction arithmetic, OTP identities over byte-key fixtures, the exact birthday threshold, DH, Vigenère, key counts, hash examples, origin tuples, DNS probability, and actual Merkle-path reconstruction. A toy invertible cipher checks CBC dependency propagation only; it is not an AES security or avalanche test.

Existing ordering tests still cover all 24 permutations and 288 grading cases. Site validation checks generated pages, internal references, and scripts. Human review of the mechanism and stated assumptions complements these checks; tests alone do not establish the correctness of every prose claim or predict the future exam.

## Multiple-choice format

The forecast contains only four-option questions with one accepted answer. The interactive historical bank also contains multiple-choice questions only; source acceptance notes still apply to a few older questions. A persistent “בלי שאלות פתוחות” filter defaults on and hides open sections in the full archive while retaining multiple-choice sections. The supplied PDFs remain unchanged source documents and are explicitly labelled unfiltered.
