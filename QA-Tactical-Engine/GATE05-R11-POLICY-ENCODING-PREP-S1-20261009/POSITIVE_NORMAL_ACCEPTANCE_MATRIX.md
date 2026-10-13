# R11 positive normal acceptance preparation

Preparation only / no candidate execution.

|id|topic|reference_case|exact_expected_assertion|
|---|---|---|---|
|N01|Typed schema/fixed representation|BASE|Four keys exact order and types/schemaVersion;digest excluded from canonical input;compact UTF8/noBOM|
|N02|Independent equal instances|BASE/EQUAL_SEPARATE|Equal reference bytes/digest and separate construction;typed identity equal|
|N03|Opaque ID-only change|BASE/ID_ONLY/CASE_ID|Exact ordinal ID changed,revision/list fixed;bytes/digest/binding differ;no case fold|
|N04|Opaque revision-only change|BASE/REV_ONLY/REV_NUMERIC_TEXT|Revision string exact,ID/list fixed;007 distinct from7,no number parsing|
|N05|Order-only change|BASE/ORDER_ONLY|SameID/revision,exact ordered canonical list and digest differ;actual inventory independently matching|
|N06|Unicode identity|UNICODE_ID/UNICODE_REV|Exact BMP/supplementary and combining-codepoint sequence retained,no Unicode normalization|
|N07|Quoted/control display text|DISPLAY_ID/DISPLAY_REV|Quotes/backslash/tab/CR/LF roundtrip exact;chosen documented escape reference bytes|
|N08|Leading/trailing whitespace|SPACED_ID/SPACED_REV|NoTrim of ID/revision at declaration/check/admission/content serialization;UTF16 ordinal sequence exact|
|N09|Normal package case|BASE/PACKAGE_CASE_LOWER|Canonical lowercased package list/order exact,equal reference bytes/digest;opaque identity remains exact|
|N10|Policy roundtrip/reconstruction|Allnormalcases|Deserialize returns typed schema/ID/revision/list;reserialize chosen convention reproduces reference bytes,not status/count alone|
|N11|Check/admission/full binding|Separatefullydeclaredmatchingpositivefixtures|All returned schema/ID/revision/digest/list/ordinal/meaning and full admitted content compared with predeclared oracle;raw returned list contract reconciled before execution|
|N12|Caller mutation and lossless content binding|Normalfreshinstances|Pure serialization/check and admission caller changes recorded separately;fresh-originaltrue/explicitNormalize/false transport preserve declared opaque identity|
|N13|R9/current content regression|Futurefreshgeneric+supportedcontrols|Unknown/null/empty/known-distinct/reverse meanings,65/current floatbits/int32/largeInt64/Unicode/ordered content multiplicity;no nativeallfieldclaim|
|N14|Prospective exact evidence graph|FutureMasteradmittedcandidate|Chosen escape oracle before finalbuild,en-US/de-DEfreshprocesses,typed meaning then bytes/digest;actual numeric exits/prepost/loaded sourcePDB graph|
