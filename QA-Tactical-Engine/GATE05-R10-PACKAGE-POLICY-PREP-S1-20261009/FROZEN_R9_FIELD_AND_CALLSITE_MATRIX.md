# FrozenR9 constraints — metadata/static only

| ID | Field | Existing type | Frozen line | R10 criterion |
|---|---|---|---|---|
| F01 | ContentProfileManifest.activeMods | List<ModContentRecord> | 2795 | Entire declared ordered inventory must be compared with distinct expected policy;count/nonempty alone inadequate |
| F02 | ModContentRecord.loadOrder | Int32 | 2614 | Declare whether array order or loadOrder defines the logical sequence;verify every normal ordinal and ID without sorting an inconsistent observation into approval |
| F03 | ModContentRecord.packageId | String | 2615 | Lowercase literal QA fixtures;production comparer/case/normalization must be declared;do not choose a worldwide catalogue |
| F04 | ModContentRecord.compatibilityVersionRange | String | 2617 | Never substitute compatibility into actual modVersion or use it as package approval |
| F05 | ModContentRecord.modVersion | Nullable String | 2618 | Preserve R9 null/empty/known-distinct/reverse semantics;unknown alone is not universal required-content support |
| F06 | ModPatchSettingsDispositionRecord.supportedModBoundary | String default POC_DECLARED_PACKAGES_ONLY | 2628 | Remove/replace misleading actual trusted default with explicitly checked package-policy binding;not a policy source |
| F07 | patchSettingsDisposition.patchPolicy/settingsPolicy | String | 2624 | Package match does not certify raw patches/settings identity or allow exclusion |
| F08 | patchSettingsDisposition.totalObservedPatches | Int32 | 1640 | Normalizer count rewrite is not observation or package approval;package decisions must not be fixed by changing source values |
| F09 | schemaVersion/contentContractVersion/capabilityFlags | String/String/List<String> | 1536 | New policy binding must be versioned and serialized in actual content;fixture flag/digest is not authority |
| F10 | loadedAssemblies | List<LoadedAssemblyRecord> | 2632 | Keep SHA/MVID/size and declared key checks;package policy does not replace assembly/material coverage |
| F11 | RunningModsListForReading | Native runtime source;NOT EXECUTED | 2133 | Collect observed list independently,then check against configured expected snapshot before newly computed trusted success |
| F12 | modVersion=null collector assignment | Nullable String | 2161 | Preserve explicit unknown;actual source availability/native evidence remain outside preparation |
