# Forecast content review — 14 November 2026

All 60 current retake exercises were reviewed, including every keyed answer and all 180 distractors. The answer identities of P01–P30 were preserved; P31–P60 are new variations. Each current solution now has a derivation, four separate explanations identified by option text, assumptions/limits, and technical references where applicable. They are authored study explanations, not official lecturer solutions.

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

`scripts/test_forecast_content.py` checks 60 four-option, single-answer questions and 240 matching option explanations. It independently checks all RSA choices, transaction arithmetic, OTP identities over byte-key fixtures, the exact birthday threshold, DH, Vigenère, key counts, hash examples, origin tuples, DNS probability, and actual Merkle-path reconstruction. A toy invertible cipher checks CBC dependency propagation only; it is not an AES security or avalanche test.

Existing ordering tests still cover all 24 permutations and 288 grading cases. Site validation checks generated pages, internal references, and scripts. Human review of the mechanism and stated assumptions complements these checks; tests alone do not establish the correctness of every prose claim or predict the future exam.

## Multiple-choice format

The forecast contains only four-option questions with one accepted answer. The interactive historical bank also contains multiple-choice questions only; source acceptance notes still apply to a few older questions. A persistent “בלי שאלות פתוחות” filter defaults on and hides open sections in the full archive while retaining multiple-choice sections. The supplied PDFs remain unchanged source documents and are explicitly labelled unfiltered.


## Expansion to 60 and confidence review — 14 November 2026

P31–P60 add changes of operation and assumptions rather than thirty numerical copies. Topics include RSA signing/decryption/key generation, certificate identity and constraints, OCSP authority separation, CT promises and inconsistent views, UTXO validity, multisig, PoW, Merkle updates, OTP reuse, CBC IV changes, EDE cancellation, substitution patterns, Vigenère key recovery, hash definitions and constructions, replay, password secrets, DH authentication and Web defenses.

Review clarified P37 to state both recorded TLS 1.2 RSA traffic and a stolen RSA key; otherwise its retrospective-decryption distractor would depend on unstated facts. P60 explicitly uses an RSA certificate with both RSA key exchange and authenticated ECDHE. P36 distinguishes an intermediate certificate from a trust anchor. P38 distinguishes an SCT promise from a verified inclusion path. P39 assumes the same deterministic append-only log, same tree size, and no hash collisions. P44 excludes the changed leaf and includes the root. P46 isolates IV tampering before application checks. P57 specifies a normal text element, avoiding unsafe generalization to script contexts. P59 names the synchronizer-token model.

All numerical answer alternatives were checked for RSA, Vigenère, XOR and modular hashing. Additional tests cover actual 32-leaf Merkle changes, ideal PoW success counts, substitution equality patterns, and algebraic CBC/EDE dependencies using a toy permutation (not a claim of AES/DES security). Existing grading, shuffle, history/reload and clear-history tests remain active for ten setup sources, including six sets and the top-20 collection.

All 60 confidence scores are independently recomputed from source records. Coverage uses 18 dates from October 2022 through October 2026, deduplicates source files, and excludes open sections. Seven A/B pairs and three summer pairs are checked. Skill evidence is a conservative documented manual map, not exhaustive clause-level annotation. Scores are heuristic confidence in a related skill and are not calibrated occurrence probabilities. Broader extrapolations are explicitly marked and receive a 20-point deduction; no claim of improved predictive accuracy is made before the actual retake is known.
