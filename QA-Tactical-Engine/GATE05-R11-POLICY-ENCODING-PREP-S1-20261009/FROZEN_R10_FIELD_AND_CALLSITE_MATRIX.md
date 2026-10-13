# Frozen R10 field/callsite constraints

Preparation only / no candidate execution.

|concept|current_type|first_line|last_line|
|---|---|---|---|
|CanonicalNormalize policyId.Trim|String|1697|1703|
|CanonicalNormalize revision.Trim|String|1697|1703|
|CanonicalNormalize policyDigest/status.Trim|String|1697|1703|
|Content codec JSON Serialize/Deserialize|ContentProfileManifest JSON|1790|1813|
|Policy digest record overload|ExpectedPackagePolicyRecord|1815|1820|
|Policy digest delimiter UTF8 preimage|String ID/revision+IEnumerable<String>|1821|1839|
|Check typed result identity/list|PackagePolicyCheckResult|1883|1892|
|Check physical list/order|List<ModContentRecord>/StringIDs|1906|1937|
|TryAdmit typed disposition/boundary|PackagePolicyDispositionRecord|1953|2000|
|Structural boundary checks|String+optional typed disposition|2094|2137|
|Actual Compute check/binding|Configuredpolicy+ContentProfileManifest|2859|2885|
|Current policy DTO/result/schema absence|StringID/revision/list/digest;no policy schemaVersion|2945|2973|
