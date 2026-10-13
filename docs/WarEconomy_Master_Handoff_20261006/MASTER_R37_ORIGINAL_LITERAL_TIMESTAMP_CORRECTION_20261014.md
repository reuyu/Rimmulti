# 原文 raw UTC / PairID controlling correction

Master 2026-10-14: R35 preparation oracle and BOTH R29 upstream raw UTF8 inputs independently re-read and SHA/bytes matched. All six Child raw strings are `2026-10-11T00:00:01.0000000Z`, Parent `2026-10-11T00:00:00.1234567Z`. The previous R36/R37 Master and QA prose saying Child `00:00:01Z` was incorrect. Raw identity contains seven zero fraction digits; they must remain. Do not rewrite raw/oracles/matrices to match prose. This correction controls later instructions over the erroneous prose; historical documents remain intact.

Case5 original PairID is `  operatorPairId=5 "Ω" \ original  `; Case6 `  operatorPairId=6 "Ω" \ original  `. Exact JSON escape representation comes from oracle, never copy Markdown rendering as raw input. Producer qa.R29.pair.05/06 descriptions are not authoritative. Raw inputs and expected bytes are controlling, even when an upstream report confidently describes another value.

This correction changes descriptions and subsequent WP only. Original raw12/config14/decl7/PairIDs/hashes remain unchanged. No runtime test, fixture, candidate execution, closure or new architecture decision. Foundation HOLD/native E2 NOT_RELEASED/current SRS1.6.
