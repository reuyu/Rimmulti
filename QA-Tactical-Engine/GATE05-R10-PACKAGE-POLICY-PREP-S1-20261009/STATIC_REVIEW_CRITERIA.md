# Defensive static criteria — R10 NOT_REVIEWED

| ID | Review topic | Required source/evidence predicate |
|---|---|---|
| S01 | Expected policy independently supplied | Pure comparison/admission helper has distinct policy+observed input;expected list is not copied from actual or trusted because embedded |
| S02 | Canonical ID/revision/list binding | Declared schema/framing includes policyId,typed revision and every ordered packageId;digest equality is identity,not authority |
| S03 | Complete actual inventory/order check | Trace independent observed enumeration vs expected declaration;all ordinals/IDs checked,not count/name/nonempty |
| S04 | No self-approval/default trusted boundary | Default-only supportedModBoundary replaced with checked binding;generic embedded policy does not approve itself |
| S05 | Actual Compute linkage | Collected RunningMods reaches same pure package checker before newly computed trusted fingerprint success;no helper-only isolated gate |
| S06 | Unconfigured state | Static-only no-arg provider has concrete unavailable/BLOCKED/fail-closed before supported success without explicit policy;no execution of rejection/unconfigured branch |
| S07 | Snapshot/configuration semantics | Review explicit immutable snapshot/deep ownership/change behavior;policy installation seam is not proof of trusted operator origin and not automatically an executable QA API |
| S08 | Cached/caller paths | Identify current GetActual/cached linkage and concrete limitations within WP;do not certify cache lifecycle/native by a pure positive package helper |
| S09 | Normalization meaning | Expected/actual IDs/order/revision/digest are not rewritten to fit policy;retain R9 version meanings;patch summary rewrite is not source provenance |
| S10 | Representation version | New actual manifest fields bind expected policy identity/digest consistently;do not silently invent frozen API/format/global schema in preparation |
| S11 | Other material support | Package policy check is not raw patch/settings exclusion approval or assembly/material coverage closure;keep separate OPEN |
| S12 | Native/operator/worker-validator origin | Explicitly UNTESTED until separate release;synthetic policy digest/seam does not establish final Domain authority |
| S13 | Protected scope/diff | R9 frozen source diff must identify policy-only edits;Worker/csproj/72547prefix fixed;outside suffix concrete BLOCKED instead of expansion |
| S14 | Fresh exact graph/admission | Master exact frozenR10/static pure-helper admission then own oracle/build/pre/run/post;no mutableR10 review now,old runner or inherited PASS |
