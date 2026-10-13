import os, hashlib

census_path = r'scratch\WorkerBridgeMod\Source\EngineHostCensus.cs'
with open(census_path, 'rb') as f:
    orig = f.read()

prefix = orig[:72547]
assert hashlib.sha256(prefix).hexdigest().upper() == 'F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887', 'Prefix SHA mismatch!'

suffix_code = '''    public static class ContentProfileProvider
    {
        public const string MANIFEST_SCHEMA_VERSION = "ADR-006B-v5";
        public const string CONTENT_CONTRACT_VERSION = "ADR-006B-v5-R8";
        public const string SUPPORTED_COVERAGE_PROFILE = "POC_SUPPORTED_CORE_DLC_ASSEMBLIES_V5";
        public const string MOD_PATCH_SUPPORT_STATUS = "TYPED_OBSERVATION_EXPLICIT_DISPOSITION_V1";

        private static string? _cachedFingerprint = null;
        private static string? _cachedCanonicalJson = null;
        private static ContentProfileManifest? _cachedManifest = null;
        private static string? _lastComputationError = null;

        public static bool IsCached => _cachedFingerprint != null;
        public static string? LastComputationError => _lastComputationError;
        public static string? CachedCanonicalJson => _cachedCanonicalJson;
        public static ContentProfileManifest? CachedManifest => _cachedManifest;

        public static string FormatLossless(float val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        public static string FormatLossless(double val)
        {
            return val.ToString("R", System.Globalization.CultureInfo.InvariantCulture);
        }

        public static string GetActualContentProfileFingerprint()
        {
            if (_cachedFingerprint != null) return _cachedFingerprint;
            _cachedFingerprint = ComputeActualContentProfileFingerprint();
            return _cachedFingerprint;
        }

        public static void InvalidateCache()
        {
            _cachedFingerprint = null;
            _cachedCanonicalJson = null;
            _cachedManifest = null;
            _lastComputationError = null;
        }

        /// <summary>
        /// Deterministically normalizes the manifest collections in-place.
        /// Unordered sets are sorted by canonical ordinal keys with deterministic tie-breaking.
        /// Ordered collections (activeMods loadOrder, verbs, stages, comps) preserve their defined sequence and multiplicity.
        /// In-place caller mutation contract: mutates the supplied manifest instance directly.
        /// </summary>
        public static void CanonicalNormalize(ContentProfileManifest manifest)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));

            // 1. DLC expansions (Unordered set -> defName ordinal sort)
            if (manifest.dlcExpansions != null)
            {
                manifest.dlcExpansions.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
            }

            // 2. Active mods (Ordered list -> loadOrder preserved, tie-broken by packageId)
            if (manifest.activeMods != null)
            {
                foreach (var m in manifest.activeMods)
                {
                    if (m == null) continue;
                    if (string.IsNullOrEmpty(m.compatibilityVersionRange) && !string.IsNullOrEmpty(m.modVersion))
                    {
                        m.compatibilityVersionRange = m.modVersion ?? "";
                    }
                    else if (string.IsNullOrEmpty(m.modVersion) && !string.IsNullOrEmpty(m.compatibilityVersionRange))
                    {
                        m.modVersion = m.compatibilityVersionRange;
                    }
                    if (string.IsNullOrEmpty(m.patchDisposition))
                    {
                        m.patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
                    }
                    if (string.IsNullOrEmpty(m.settingsDisposition))
                    {
                        m.settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED";
                    }
                }

                manifest.activeMods.Sort((a, b) =>
                {
                    int c = a.loadOrder.CompareTo(b.loadOrder);
                    return c != 0 ? c : string.CompareOrdinal(a?.packageId ?? "", b?.packageId ?? "");
                });
            }

            // 3. Loaded assemblies (Unordered set -> packageId -> assemblyName -> mvid -> sha256 ordinal sort)
            if (manifest.loadedAssemblies != null)
            {
                manifest.loadedAssemblies.Sort((a, b) =>
                {
                    int c1 = string.CompareOrdinal(a?.packageId ?? "", b?.packageId ?? "");
                    if (c1 != 0) return c1;
                    int c2 = string.CompareOrdinal(a?.assemblyName ?? "", b?.assemblyName ?? "");
                    if (c2 != 0) return c2;
                    int c3 = string.CompareOrdinal(a?.mvid ?? "", b?.mvid ?? "");
                    if (c3 != 0) return c3;
                    return string.CompareOrdinal(a?.sha256 ?? "", b?.sha256 ?? "");
                });
            }

            // 4. Patch/Settings Disposition Summary synchronization
            if (manifest.patchSettingsDisposition != null && manifest.activeMods != null)
            {
                int totalPatches = 0;
                foreach (var m in manifest.activeMods)
                {
                    if (m != null && m.patchCount > 0)
                    {
                        totalPatches += m.patchCount;
                    }
                }
                manifest.patchSettingsDisposition.totalObservedPatches = totalPatches;
            }

            // 5. Def Families
            if (manifest.defFamilies != null)
            {
                // A. ThingDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.thingDefs != null)
                {
                    manifest.defFamilies.thingDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                    foreach (var t in manifest.defFamilies.thingDefs)
                    {
                        if (t == null) continue;
                        if (t.stats != null)
                        {
                            t.stats.Sort((a, b) =>
                            {
                                int c = string.CompareOrdinal(a?.statDef ?? "", b?.statDef ?? "");
                                return c != 0 ? c : (a?.value ?? 0f).CompareTo(b?.value ?? 0f);
                            });
                        }
                        if (t.costList != null)
                        {
                            t.costList.Sort((a, b) =>
                            {
                                int c = string.CompareOrdinal(a?.thingDef ?? "", b?.thingDef ?? "");
                                return c != 0 ? c : (a?.count ?? 0).CompareTo(b?.count ?? 0);
                            });
                        }
                        if (t.stuffCategories != null)
                        {
                            t.stuffCategories.Sort(StringComparer.Ordinal);
                        }
                        // verbs: Material sequence and multiplicity PRESERVED (no sort)
                        // comps: Material sequence PRESERVED (no sort)
                    }
                }

                // B. HediffDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.hediffDefs != null)
                {
                    manifest.defFamilies.hediffDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                    foreach (var h in manifest.defFamilies.hediffDefs)
                    {
                        if (h == null) continue;
                        // stages: minSeverity ordinal sequence PRESERVED
                        // comps: Material sequence PRESERVED
                    }
                }

                // C. JobDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.jobDefs != null)
                {
                    manifest.defFamilies.jobDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // D. SkillDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.skillDefs != null)
                {
                    manifest.defFamilies.skillDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // E. FactionDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.factionDefs != null)
                {
                    manifest.defFamilies.factionDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // F. BiomeDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.biomeDefs != null)
                {
                    manifest.defFamilies.biomeDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // G. WeatherDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.weatherDefs != null)
                {
                    manifest.defFamilies.weatherDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }

                // H. ResearchProjectDefs (Unordered set -> defName ordinal sort)
                if (manifest.defFamilies.researchDefs != null)
                {
                    manifest.defFamilies.researchDefs.Sort((a, b) => string.CompareOrdinal(a?.defName ?? "", b?.defName ?? ""));
                }
            }
        }

        public static string SerializeCanonicalJson(ContentProfileManifest manifest, bool canonicalNormalize = true)
        {
            if (manifest == null) throw new ArgumentNullException(nameof(manifest));

            if (canonicalNormalize)
            {
                CanonicalNormalize(manifest);
            }

            var settings = new JsonSerializerSettings
            {
                Formatting = Newtonsoft.Json.Formatting.None,
                NullValueHandling = NullValueHandling.Include,
                FloatFormatHandling = FloatFormatHandling.String,
                FloatParseHandling = FloatParseHandling.Double
            };
            return JsonConvert.SerializeObject(manifest, settings);
        }

        public static ContentProfileManifest? DeserializeCanonicalJson(string json)
        {
            if (string.IsNullOrEmpty(json)) return null;
            return JsonConvert.DeserializeObject<ContentProfileManifest>(json);
        }

        /// <summary>
        /// Validates the manifest against the explicit supported content contract (MD-130).
        /// Checks required header metadata, supported coverage boundaries, patch/settings boundary status,
        /// mandatory collection and Def family presence, key uniqueness, and required child properties.
        /// </summary>
        public static bool ValidateContract(ContentProfileManifest manifest, out string failureReason)
        {
            failureReason = "";
            if (manifest == null)
            {
                failureReason = "Manifest is null.";
                return false;
            }

            // 1. Header Metadata Validation
            if (string.IsNullOrEmpty(manifest.schemaVersion) || manifest.schemaVersion != MANIFEST_SCHEMA_VERSION)
            {
                failureReason = $"Invalid schemaVersion: '{manifest.schemaVersion}'. Expected '{MANIFEST_SCHEMA_VERSION}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.contentContractVersion) || manifest.contentContractVersion != CONTENT_CONTRACT_VERSION)
            {
                failureReason = $"Invalid contentContractVersion: '{manifest.contentContractVersion}'. Expected '{CONTENT_CONTRACT_VERSION}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.supportedCoverageProfile) || manifest.supportedCoverageProfile != SUPPORTED_COVERAGE_PROFILE)
            {
                failureReason = $"Invalid supportedCoverageProfile: '{manifest.supportedCoverageProfile}'. Expected '{SUPPORTED_COVERAGE_PROFILE}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.modPatchSupportStatus) || manifest.modPatchSupportStatus != MOD_PATCH_SUPPORT_STATUS)
            {
                failureReason = $"Invalid modPatchSupportStatus: '{manifest.modPatchSupportStatus}'. Expected '{MOD_PATCH_SUPPORT_STATUS}'.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.buildIdentity))
            {
                failureReason = "Required buildIdentity is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.assemblyCSharpMvid))
            {
                failureReason = "Required assemblyCSharpMvid is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.assemblyCSharpSha))
            {
                failureReason = "Required assemblyCSharpSha is missing or empty.";
                return false;
            }

            // 2. Capability Flags Validation
            if (manifest.capabilityFlags == null)
            {
                failureReason = "Required capabilityFlags list is null.";
                return false;
            }
            string[] requiredFlags = new string[]
            {
                "TACTICAL_PROBE_V4",
                "READ_ONLY",
                "SIMULATION",
                "GATE05_R8_SUPPORTED_DISPOSITION",
                "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
            };
            foreach (var flag in requiredFlags)
            {
                if (!manifest.capabilityFlags.Contains(flag))
                {
                    failureReason = $"Missing required capabilityFlag: '{flag}'.";
                    return false;
                }
            }

            // 3. Patch/Settings Disposition Validation
            if (manifest.patchSettingsDisposition == null)
            {
                failureReason = "Required patchSettingsDisposition record is null.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.patchSettingsDisposition.patchPolicy))
            {
                failureReason = "Required patchSettingsDisposition.patchPolicy is missing or empty.";
                return false;
            }
            if (string.IsNullOrEmpty(manifest.patchSettingsDisposition.settingsPolicy))
            {
                failureReason = "Required patchSettingsDisposition.settingsPolicy is missing or empty.";
                return false;
            }
            if (manifest.patchSettingsDisposition.totalObservedPatches < 0)
            {
                failureReason = "patchSettingsDisposition.totalObservedPatches cannot be negative.";
                return false;
            }

            // 4. DLC Expansions Validation
            if (manifest.dlcExpansions == null)
            {
                failureReason = "Required dlcExpansions list is null.";
                return false;
            }
            var dlcKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.dlcExpansions)
            {
                if (d == null) { failureReason = "dlcExpansions contains null record."; return false; }
                if (string.IsNullOrEmpty(d.defName)) { failureReason = "DLC expansion has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.status)) { failureReason = $"DLC expansion '{d.defName}' has null or empty status."; return false; }
                if (!dlcKeys.Add(d.defName)) { failureReason = $"Duplicate DLC defName '{d.defName}'."; return false; }
            }

            // 5. Active Mods Validation
            if (manifest.activeMods == null)
            {
                failureReason = "Required activeMods list is null.";
                return false;
            }
            var modPackageIds = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            var modLoadOrders = new HashSet<int>();
            foreach (var m in manifest.activeMods)
            {
                if (m == null) { failureReason = "activeMods contains null record."; return false; }
                if (string.IsNullOrEmpty(m.packageId)) { failureReason = "Active mod has null or empty packageId."; return false; }
                if (string.IsNullOrEmpty(m.name)) { failureReason = $"Active mod '{m.packageId}' has null or empty name."; return false; }
                if (string.IsNullOrEmpty(m.compatibilityVersionRange) && string.IsNullOrEmpty(m.modVersion))
                {
                    failureReason = $"Active mod '{m.packageId}' has neither compatibilityVersionRange nor modVersion.";
                    return false;
                }
                if (m.loadOrder < 0) { failureReason = $"Active mod '{m.packageId}' has negative loadOrder {m.loadOrder}."; return false; }
                if (m.patchCount < 0) { failureReason = $"Active mod '{m.packageId}' has negative patchCount {m.patchCount}."; return false; }
                if (string.IsNullOrEmpty(m.patchDisposition)) { failureReason = $"Active mod '{m.packageId}' has null or empty patchDisposition."; return false; }
                if (string.IsNullOrEmpty(m.settingsDisposition)) { failureReason = $"Active mod '{m.packageId}' has null or empty settingsDisposition."; return false; }
                if (!modPackageIds.Add(m.packageId)) { failureReason = $"Duplicate mod packageId '{m.packageId}'."; return false; }
                if (!modLoadOrders.Add(m.loadOrder)) { failureReason = $"Duplicate mod loadOrder {m.loadOrder} for mod '{m.packageId}'."; return false; }
            }

            // 6. Loaded Assemblies Validation
            if (manifest.loadedAssemblies == null)
            {
                failureReason = "Required loadedAssemblies list is null.";
                return false;
            }
            var asmKeys = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var a in manifest.loadedAssemblies)
            {
                if (a == null) { failureReason = "loadedAssemblies contains null record."; return false; }
                if (string.IsNullOrEmpty(a.packageId)) { failureReason = "Loaded assembly has null or empty packageId."; return false; }
                if (string.IsNullOrEmpty(a.assemblyName)) { failureReason = "Loaded assembly has null or empty assemblyName."; return false; }
                if (string.IsNullOrEmpty(a.mvid)) { failureReason = $"Loaded assembly '{a.assemblyName}' has null or empty mvid."; return false; }
                if (string.IsNullOrEmpty(a.sha256)) { failureReason = $"Loaded assembly '{a.assemblyName}' has null or empty sha256."; return false; }
                if (a.sizeBytes <= 0) { failureReason = $"Loaded assembly '{a.assemblyName}' has non-positive sizeBytes {a.sizeBytes}."; return false; }
                string key = $"{a.packageId}|{a.assemblyName}|{a.mvid}";
                if (!asmKeys.Add(key)) { failureReason = $"Duplicate loaded assembly composite key '{key}'."; return false; }
            }

            // 7. Def Families Validation
            if (manifest.defFamilies == null)
            {
                failureReason = "Required defFamilies record is null.";
                return false;
            }
            if (manifest.defFamilies.thingDefs == null) { failureReason = "defFamilies.thingDefs is null."; return false; }
            if (manifest.defFamilies.hediffDefs == null) { failureReason = "defFamilies.hediffDefs is null."; return false; }
            if (manifest.defFamilies.jobDefs == null) { failureReason = "defFamilies.jobDefs is null."; return false; }
            if (manifest.defFamilies.skillDefs == null) { failureReason = "defFamilies.skillDefs is null."; return false; }
            if (manifest.defFamilies.factionDefs == null) { failureReason = "defFamilies.factionDefs is null."; return false; }
            if (manifest.defFamilies.biomeDefs == null) { failureReason = "defFamilies.biomeDefs is null."; return false; }
            if (manifest.defFamilies.weatherDefs == null) { failureReason = "defFamilies.weatherDefs is null."; return false; }
            if (manifest.defFamilies.researchDefs == null) { failureReason = "defFamilies.researchDefs is null."; return false; }

            // ThingDefs
            var thingKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.thingDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "ThingDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.category)) { failureReason = $"ThingDef '{d.defName}' has null or empty category."; return false; }
                if (!thingKeys.Add(d.defName)) { failureReason = $"Duplicate ThingDef defName '{d.defName}'."; return false; }
                if (d.stats != null)
                {
                    foreach (var s in d.stats)
                    {
                        if (s == null) { failureReason = $"ThingDef '{d.defName}' contains null StatModifierRecord."; return false; }
                        if (string.IsNullOrEmpty(s.statDef)) { failureReason = $"ThingDef '{d.defName}' has null or empty statDef."; return false; }
                    }
                }
                if (d.costList != null)
                {
                    foreach (var c in d.costList)
                    {
                        if (c == null) { failureReason = $"ThingDef '{d.defName}' contains null ThingCostRecord."; return false; }
                        if (string.IsNullOrEmpty(c.thingDef)) { failureReason = $"ThingDef '{d.defName}' has null or empty costList thingDef."; return false; }
                        if (c.count < 0) { failureReason = $"ThingDef '{d.defName}' has negative costList count {c.count}."; return false; }
                    }
                }
                if (d.stuffCategories != null)
                {
                    foreach (var sc in d.stuffCategories)
                    {
                        if (string.IsNullOrEmpty(sc)) { failureReason = $"ThingDef '{d.defName}' contains null or empty stuffCategory."; return false; }
                    }
                }
                if (d.verbs != null)
                {
                    foreach (var v in d.verbs)
                    {
                        if (v == null) { failureReason = $"ThingDef '{d.defName}' contains null VerbPropsRecord."; return false; }
                        if (string.IsNullOrEmpty(v.verbClass)) { failureReason = $"ThingDef '{d.defName}' has null or empty verbClass."; return false; }
                    }
                }
                if (d.comps != null)
                {
                    foreach (var cp in d.comps)
                    {
                        if (string.IsNullOrEmpty(cp)) { failureReason = $"ThingDef '{d.defName}' contains null or empty compClass string."; return false; }
                    }
                }
            }

            // HediffDefs
            var hediffKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.hediffDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "HediffDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.hediffClass)) { failureReason = $"HediffDef '{d.defName}' has null or empty hediffClass."; return false; }
                if (!hediffKeys.Add(d.defName)) { failureReason = $"Duplicate HediffDef defName '{d.defName}'."; return false; }
                if (d.stages != null)
                {
                    foreach (var st in d.stages)
                    {
                        if (st == null) { failureReason = $"HediffDef '{d.defName}' contains null stage record."; return false; }
                    }
                }
                if (d.comps != null)
                {
                    foreach (var cp in d.comps)
                    {
                        if (string.IsNullOrEmpty(cp)) { failureReason = $"HediffDef '{d.defName}' contains null or empty compClass string."; return false; }
                    }
                }
            }

            // JobDefs
            var jobKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.jobDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "JobDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.driverClass)) { failureReason = $"JobDef '{d.defName}' has null or empty driverClass."; return false; }
                if (string.IsNullOrEmpty(d.checkOverrideOnDamage)) { failureReason = $"JobDef '{d.defName}' has null or empty checkOverrideOnDamage."; return false; }
                if (!jobKeys.Add(d.defName)) { failureReason = $"Duplicate JobDef defName '{d.defName}'."; return false; }
            }

            // SkillDefs
            var skillKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.skillDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "SkillDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.disablingWorkTags)) { failureReason = $"SkillDef '{d.defName}' has null or empty disablingWorkTags."; return false; }
                if (!skillKeys.Add(d.defName)) { failureReason = $"Duplicate SkillDef defName '{d.defName}'."; return false; }
            }

            // FactionDefs
            var factionKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.factionDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "FactionDef has null or empty defName."; return false; }
                if (!factionKeys.Add(d.defName)) { failureReason = $"Duplicate FactionDef defName '{d.defName}'."; return false; }
            }

            // BiomeDefs
            var biomeKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.biomeDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "BiomeDef has null or empty defName."; return false; }
                if (!biomeKeys.Add(d.defName)) { failureReason = $"Duplicate BiomeDef defName '{d.defName}'."; return false; }
            }

            // WeatherDefs
            var weatherKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.weatherDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "WeatherDef has null or empty defName."; return false; }
                if (!weatherKeys.Add(d.defName)) { failureReason = $"Duplicate WeatherDef defName '{d.defName}'."; return false; }
            }

            // ResearchProjectDefs
            var researchKeys = new HashSet<string>(StringComparer.Ordinal);
            foreach (var d in manifest.defFamilies.researchDefs)
            {
                if (d == null || string.IsNullOrEmpty(d.defName)) { failureReason = "ResearchProjectDef has null or empty defName."; return false; }
                if (string.IsNullOrEmpty(d.techLevel)) { failureReason = $"ResearchProjectDef '{d.defName}' has null or empty techLevel."; return false; }
                if (!researchKeys.Add(d.defName)) { failureReason = $"Duplicate ResearchProjectDef defName '{d.defName}'."; return false; }
            }

            return true;
        }

        /// <summary>
        /// Explicit admission gate method: validates the manifest against the supported content contract.
        /// If valid, serializes canonically; if invalid, returns false with explicit failureReason.
        /// </summary>
        public static bool TryAdmitManifest(ContentProfileManifest manifest, out string canonicalJson, out string failureReason)
        {
            canonicalJson = "";
            if (!ValidateContract(manifest, out failureReason))
            {
                return false;
            }
            canonicalJson = SerializeCanonicalJson(manifest, canonicalNormalize: true);
            return true;
        }

        public static ContentProfileManifest ComputeActualContentProfileManifest()
        {
            var manifest = new ContentProfileManifest();
            manifest.schemaVersion = MANIFEST_SCHEMA_VERSION;
            manifest.contentContractVersion = CONTENT_CONTRACT_VERSION;
            manifest.supportedCoverageProfile = SUPPORTED_COVERAGE_PROFILE;
            manifest.modPatchSupportStatus = MOD_PATCH_SUPPORT_STATUS;

            // 1. RimWorld build identity (Fail-Closed)
            string buildIdentity = VersionControl.CurrentVersionStringWithRev;
            if (string.IsNullOrEmpty(buildIdentity))
            {
                throw new InvalidOperationException("RimWorld build identity (VersionControl.CurrentVersionStringWithRev) is missing or null; required material is unobserved.");
            }
            manifest.buildIdentity = buildIdentity;

            // 2. Assembly-CSharp SHA-256 and MVID (Fail-Closed)
            var gameAsm = typeof(Verse.Game).Assembly;
            if (gameAsm == null)
            {
                throw new InvalidOperationException("Core game assembly Verse.Game is not loaded; required core identity is unavailable.");
            }
            manifest.assemblyCSharpMvid = gameAsm.ManifestModule.ModuleVersionId.ToString();
            if (!string.IsNullOrEmpty(gameAsm.Location) && File.Exists(gameAsm.Location))
            {
                using (var sha = SHA256.Create())
                using (var fs = File.OpenRead(gameAsm.Location))
                {
                    manifest.assemblyCSharpSha = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                }
            }
            else
            {
                throw new InvalidOperationException("Core game assembly Assembly-CSharp.dll location is unavailable on disk; required core identity SHA256 is unobserved.");
            }

            // 3. DLC Expansions (Fail-Closed)
            try
            {
                var dlcDefs = DefDatabase<ExpansionDef>.AllDefsListForReading;
                if (dlcDefs == null || dlcDefs.Count == 0)
                {
                    throw new InvalidOperationException("DLC ExpansionDefs collection is empty or null; required DLC inventory is unavailable.");
                }
                foreach (var dlc in dlcDefs)
                {
                    if (dlc == null || string.IsNullOrEmpty(dlc.defName))
                    {
                        throw new InvalidOperationException("DLC expansion collection contains null Def or empty defName; required DLC identity is unavailable.");
                    }
                    manifest.dlcExpansions.Add(new DlcExpansionRecord
                    {
                        defName = dlc.defName,
                        status = dlc.Status.ToString(),
                        linkedMod = dlc.linkedMod,
                        statusDescription = dlc.StatusDescription
                    });
                }
                manifest.dlcExpansions.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"DLC Expansions query failed in ContentProfileProvider: {ex.Message}", ex);
            }

            // 4. Active Mods and Loaded Assemblies (Fail-Closed)
            try
            {
                var runningMods = LoadedModManager.RunningModsListForReading;
                if (runningMods == null || runningMods.Count == 0)
                {
                    throw new InvalidOperationException("LoadedModManager.RunningModsListForReading is null or empty; required active mod inventory is unavailable.");
                }

                int loadOrder = 0;
                int totalPatchesSum = 0;
                foreach (var mod in runningMods)
                {
                    if (mod == null || mod.PackageIdPlayerFacing == null)
                    {
                        throw new InvalidOperationException("Active mod entry or PackageId is null; required mod identity is unavailable.");
                    }

                    int patchCount = mod.Patches != null ? mod.Patches.Count() : 0;
                    totalPatchesSum += patchCount;

                    string compatRange = mod.ModMetaData?.SupportedVersionsReadOnly != null
                        ? string.Join(";", mod.ModMetaData.SupportedVersionsReadOnly)
                        : "";

                    manifest.activeMods.Add(new ModContentRecord
                    {
                        loadOrder = loadOrder++,
                        packageId = mod.PackageIdPlayerFacing.ToLowerInvariant(),
                        name = mod.Name ?? "",
                        compatibilityVersionRange = compatRange,
                        modVersion = compatRange,
                        patchCount = patchCount,
                        patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                        settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED"
                    });

                    if (mod.assemblies?.loadedAssemblies != null)
                    {
                        foreach (var asm in mod.assemblies.loadedAssemblies)
                        {
                            if (asm == null)
                            {
                                throw new InvalidOperationException($"Loaded assembly collection for mod '{mod.PackageIdPlayerFacing}' contains null assembly; required assembly identity is unobserved.");
                            }
                            string shaStr = "";
                            long sizeBytes = 0;
                            if (!string.IsNullOrEmpty(asm.Location) && File.Exists(asm.Location))
                            {
                                var fi = new FileInfo(asm.Location);
                                sizeBytes = fi.Length;
                                using (var sha = SHA256.Create())
                                using (var fs = File.OpenRead(asm.Location))
                                {
                                    shaStr = BitConverter.ToString(sha.ComputeHash(fs)).Replace("-", "").ToUpperInvariant();
                                }
                            }
                            manifest.loadedAssemblies.Add(new LoadedAssemblyRecord
                            {
                                packageId = mod.PackageIdPlayerFacing.ToLowerInvariant(),
                                assemblyName = asm.GetName().Name,
                                mvid = asm.ManifestModule.ModuleVersionId.ToString(),
                                sha256 = shaStr,
                                sizeBytes = sizeBytes
                            });
                        }
                    }
                }
                manifest.loadedAssemblies.Sort((a, b) =>
                {
                    int c1 = string.CompareOrdinal(a.packageId, b.packageId);
                    if (c1 != 0) return c1;
                    int c2 = string.CompareOrdinal(a.assemblyName, b.assemblyName);
                    if (c2 != 0) return c2;
                    int c3 = string.CompareOrdinal(a.mvid, b.mvid);
                    if (c3 != 0) return c3;
                    return string.CompareOrdinal(a.sha256, b.sha256);
                });

                manifest.patchSettingsDisposition = new ModPatchSettingsDispositionRecord
                {
                    patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED",
                    settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED",
                    supportedModBoundary = "POC_DECLARED_PACKAGES_ONLY",
                    totalObservedPatches = totalPatchesSum
                };
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException($"Active Mods / Assemblies query failed in ContentProfileProvider: {ex.Message}", ex);
            }

            // 5. Eight Def Families Projection (ADR-006B-v5-R8)
            // A. ThingDef
            if (DefDatabase<ThingDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<ThingDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<ThingDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<ThingDef> contains null Def or empty defName; required Def identity is unavailable.");
                }

                var rec = new ThingDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    category = d.category.ToString(),
                    useHitPoints = d.useHitPoints,
                    costStuffCount = d.costStuffCount
                };

                if (d.statBases != null)
                {
                    foreach (var s in d.statBases)
                    {
                        if (s == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null StatModifier in statBases; required stat reference is unobserved.");
                        }
                        if (s.stat == null || string.IsNullOrEmpty(s.stat.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains StatModifier with null/empty statDef; required stat reference is unobserved.");
                        }
                        rec.stats.Add(new StatModifierRecord { statDef = s.stat.defName, value = s.value });
                    }
                    rec.stats.Sort((a, b) =>
                    {
                        int c = string.CompareOrdinal(a.statDef, b.statDef);
                        return c != 0 ? c : a.value.CompareTo(b.value);
                    });
                }

                if (d.race != null)
                {
                    rec.race = new RacePropsRecord
                    {
                        baseBodySize = d.race.baseBodySize,
                        baseHealthScale = d.race.baseHealthScale,
                        baseHungerRate = d.race.baseHungerRate,
                        humanlike = d.race.Humanlike
                    };
                }

                if (d.building != null)
                {
                    rec.building = new BuildingPropsRecord
                    {
                        isNaturalRock = d.building.isNaturalRock,
                        isEdifice = d.building.isEdifice,
                        bed_healPerDay = d.building.bed_healPerDay
                    };
                }

                if (d.ingestible != null)
                {
                    rec.ingestible = new IngestiblePropsRecord
                    {
                        cachedNutrition = d.ingestible.CachedNutrition,
                        preferability = d.ingestible.preferability.ToString()
                    };
                }

                if (d.costList != null)
                {
                    foreach (var c in d.costList)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null ThingOrderCost in costList; required cost material reference is unobserved.");
                        }
                        if (c.thingDef == null || string.IsNullOrEmpty(c.thingDef.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains ThingOrderCost with null/empty thingDef; required cost material reference is unobserved.");
                        }
                        rec.costList.Add(new ThingCostRecord { thingDef = c.thingDef.defName, count = c.count });
                    }
                    rec.costList.Sort((a, b) =>
                    {
                        int c = string.CompareOrdinal(a.thingDef, b.thingDef);
                        return c != 0 ? c : a.count.CompareTo(b.count);
                    });
                }

                if (d.stuffCategories != null)
                {
                    foreach (var sc in d.stuffCategories)
                    {
                        if (sc == null || string.IsNullOrEmpty(sc.defName))
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null/empty StuffCategoryDef; required category reference is unobserved.");
                        }
                        rec.stuffCategories.Add(sc.defName);
                    }
                    rec.stuffCategories.Sort(StringComparer.Ordinal);
                }

                if (d.Verbs != null)
                {
                    foreach (var v in d.Verbs)
                    {
                        if (v == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null VerbProperties in Verbs; required verb reference is unobserved.");
                        }
                        if (v.verbClass == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains VerbProperties with null verbClass; required verbClass reference is unobserved.");
                        }
                        rec.verbs.Add(new VerbPropsRecord
                        {
                            verbClass = v.verbClass.FullName ?? v.verbClass.Name,
                            range = v.range
                        });
                    }
                }

                if (d.comps != null)
                {
                    foreach (var c in d.comps)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains null CompProperties in comps; required comp reference is unobserved.");
                        }
                        if (c.compClass == null)
                        {
                            throw new InvalidOperationException($"ThingDef '{d.defName}' contains CompProperties with null compClass; required compClass reference is unobserved.");
                        }
                        rec.comps.Add(c.compClass.FullName ?? c.compClass.Name);
                    }
                }

                manifest.defFamilies.thingDefs.Add(rec);
            }
            manifest.defFamilies.thingDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // B. HediffDef
            if (DefDatabase<HediffDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<HediffDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<HediffDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<HediffDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                var rec = new HediffDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    hediffClass = d.hediffClass != null ? (d.hediffClass.FullName ?? d.hediffClass.Name) : "",
                    lethalSeverity = d.lethalSeverity,
                    isBad = d.isBad,
                    tendable = d.tendable
                };
                if (d.stages != null)
                {
                    foreach (var st in d.stages)
                    {
                        if (st == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains null HediffStage in stages; required stage reference is unobserved.");
                        }
                        rec.stages.Add(new HediffStageRecord
                        {
                            minSeverity = st.minSeverity,
                            label = st.label
                        });
                    }
                }
                if (d.comps != null)
                {
                    foreach (var c in d.comps)
                    {
                        if (c == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains null HediffCompProperties in comps; required comp reference is unobserved.");
                        }
                        if (c.compClass == null)
                        {
                            throw new InvalidOperationException($"HediffDef '{d.defName}' contains HediffCompProperties with null compClass; required compClass reference is unobserved.");
                        }
                        rec.comps.Add(c.compClass.FullName ?? c.compClass.Name);
                    }
                }
                manifest.defFamilies.hediffDefs.Add(rec);
            }
            manifest.defFamilies.hediffDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // C. JobDef
            if (DefDatabase<JobDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<JobDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<JobDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<JobDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.jobDefs.Add(new JobDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    driverClass = d.driverClass != null ? (d.driverClass.FullName ?? d.driverClass.Name) : "",
                    reportString = d.reportString,
                    playerInterruptible = d.playerInterruptible,
                    casualInterruptible = d.casualInterruptible,
                    suspendable = d.suspendable,
                    checkOverrideOnDamage = d.checkOverrideOnDamage.ToString(),
                    makeTargetPrisoner = d.makeTargetPrisoner
                });
            }
            manifest.defFamilies.jobDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // D. SkillDef
            if (DefDatabase<SkillDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<SkillDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<SkillDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<SkillDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.skillDefs.Add(new SkillDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    skillLabel = d.skillLabel,
                    disablingWorkTags = d.disablingWorkTags.ToString(),
                    pawnCreatorSummaryVisible = d.pawnCreatorSummaryVisible
                });
            }
            manifest.defFamilies.skillDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // E. FactionDef
            if (DefDatabase<FactionDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<FactionDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<FactionDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<FactionDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.factionDefs.Add(new FactionDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    isPlayer = d.isPlayer,
                    settlementGenerationWeight = d.settlementGenerationWeight,
                    pawnGroupMakersCount = d.pawnGroupMakers != null ? d.pawnGroupMakers.Count : 0
                });
            }
            manifest.defFamilies.factionDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // F. BiomeDef
            if (DefDatabase<BiomeDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<BiomeDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<BiomeDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<BiomeDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.biomeDefs.Add(new BiomeDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    animalDensity = d.animalDensity,
                    plantDensity = d.plantDensity,
                    forageability = d.forageability
                });
            }
            manifest.defFamilies.biomeDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // G. WeatherDef
            if (DefDatabase<WeatherDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<WeatherDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<WeatherDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<WeatherDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.weatherDefs.Add(new WeatherDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    windSpeedFactor = d.windSpeedFactor,
                    rainRate = d.rainRate,
                    snowRate = d.snowRate
                });
            }
            manifest.defFamilies.weatherDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // H. ResearchProjectDef
            if (DefDatabase<ResearchProjectDef>.AllDefsListForReading == null)
            {
                throw new InvalidOperationException("DefDatabase<ResearchProjectDef> is uninitialized (null); content admission requires initialized database.");
            }
            foreach (var d in DefDatabase<ResearchProjectDef>.AllDefsListForReading)
            {
                if (d == null || string.IsNullOrEmpty(d.defName))
                {
                    throw new InvalidOperationException("DefDatabase<ResearchProjectDef> contains null Def or empty defName; required Def identity is unavailable.");
                }
                manifest.defFamilies.researchDefs.Add(new ResearchProjectDefRecord
                {
                    defName = d.defName,
                    label = d.label,
                    baseCost = d.baseCost,
                    techLevel = d.techLevel.ToString(),
                    requiredResearchBuilding = d.requiredResearchBuilding?.defName
                });
            }
            manifest.defFamilies.researchDefs.Sort((a, b) => string.CompareOrdinal(a.defName, b.defName));

            // Capability flags (aligned with semantic V4 scope and ADR-006B-v5-R8)
            manifest.capabilityFlags = new List<string>
            {
                "TACTICAL_PROBE_V4",
                "READ_ONLY",
                "SIMULATION",
                "GATE05_R8_SUPPORTED_DISPOSITION",
                "ADR006B_LOSSLESS_CANONICAL_CONTENT_V5"
            };

            // Enforce Admission Contract on newly computed manifest before release
            if (!ValidateContract(manifest, out string failureReason))
            {
                throw new InvalidOperationException($"ContentProfile admission contract validation failed on computed manifest: {failureReason}");
            }

            return manifest;
        }

        public static string ComputeActualContentProfileFingerprint()
        {
            try
            {
                _lastComputationError = null;
                var manifest = ComputeActualContentProfileManifest();
                string canonicalJson = SerializeCanonicalJson(manifest, canonicalNormalize: true);
                _cachedCanonicalJson = canonicalJson;
                _cachedManifest = manifest;

                using (var sha = SHA256.Create())
                {
                    byte[] jsonBytes = Encoding.UTF8.GetBytes(canonicalJson);
                    return BitConverter.ToString(sha.ComputeHash(jsonBytes)).Replace("-", "").ToUpperInvariant();
                }
            }
            catch (Exception ex)
            {
                _lastComputationError = ex.ToString();
                Log.Error($"[ContentProfileProvider] Failed to compute ContentProfileFingerprint: {ex}");
                throw new InvalidOperationException($"ContentProfile computation failed: {ex.Message}", ex);
            }
        }
    }

    // Supported Typed Canonical Records (ADR-006B-v5-R8)
    public class DlcExpansionRecord
    {
        public string defName = "";
        public string status = "";
        public string? linkedMod = null;
        public string? statusDescription = null;
    }

    public class ModContentRecord
    {
        public int loadOrder = 0;
        public string packageId = "";
        public string name = "";
        public string compatibilityVersionRange = "";
        public string? modVersion = null;
        public int patchCount = 0;
        public string patchDisposition = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
        public string settingsDisposition = "USER_MOD_SETTINGS_EXCLUDED";
    }

    public class ModPatchSettingsDispositionRecord
    {
        public string patchPolicy = "COUNT_OBSERVED_RAW_AST_EXCLUDED";
        public string settingsPolicy = "USER_MOD_SETTINGS_EXCLUDED";
        public string supportedModBoundary = "POC_DECLARED_PACKAGES_ONLY";
        public int totalObservedPatches = 0;
    }

    public class LoadedAssemblyRecord
    {
        public string packageId = "";
        public string assemblyName = "";
        public string mvid = "";
        public string sha256 = "";
        public long sizeBytes = 0;
    }

    public class StatModifierRecord
    {
        public string statDef = "";
        public float value = 0f;
    }

    public class RacePropsRecord
    {
        public float baseBodySize = 0f;
        public float baseHealthScale = 0f;
        public float baseHungerRate = 0f;
        public bool humanlike = false;
    }

    public class BuildingPropsRecord
    {
        public bool isNaturalRock = false;
        public bool isEdifice = false;
        public float bed_healPerDay = 0f;
    }

    public class IngestiblePropsRecord
    {
        public float cachedNutrition = 0f;
        public string preferability = "";
    }

    public class ThingCostRecord
    {
        public string thingDef = "";
        public int count = 0;
    }

    public class VerbPropsRecord
    {
        public string verbClass = "";
        public float range = 0f;
    }

    public class ThingDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string category = "";
        public bool useHitPoints = false;
        public List<StatModifierRecord> stats = new List<StatModifierRecord>();
        public RacePropsRecord? race = null;
        public BuildingPropsRecord? building = null;
        public IngestiblePropsRecord? ingestible = null;
        public List<ThingCostRecord> costList = new List<ThingCostRecord>();
        public List<string> stuffCategories = new List<string>();
        public int costStuffCount = 0;
        public List<VerbPropsRecord> verbs = new List<VerbPropsRecord>();
        public List<string> comps = new List<string>();
    }

    public class HediffStageRecord
    {
        public float minSeverity = 0f;
        public string? label = null;
    }

    public class HediffDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string hediffClass = "";
        public float lethalSeverity = 0f;
        public bool isBad = false;
        public bool tendable = false;
        public List<HediffStageRecord> stages = new List<HediffStageRecord>();
        public List<string> comps = new List<string>();
    }

    public class JobDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string driverClass = "";
        public string? reportString = null;
        public bool playerInterruptible = false;
        public bool casualInterruptible = false;
        public bool suspendable = false;
        public string checkOverrideOnDamage = "";
        public bool makeTargetPrisoner = false;
    }

    public class SkillDefRecord
    {
        public string defName = "";
        public string? label = null;
        public string? skillLabel = null;
        public string disablingWorkTags = "";
        public bool pawnCreatorSummaryVisible = false;
    }

    public class FactionDefRecord
    {
        public string defName = "";
        public string? label = null;
        public bool isPlayer = false;
        public float settlementGenerationWeight = 0f;
        public int pawnGroupMakersCount = 0;
    }

    public class BiomeDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float animalDensity = 0f;
        public float plantDensity = 0f;
        public float forageability = 0f;
    }

    public class WeatherDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float windSpeedFactor = 0f;
        public float rainRate = 0f;
        public float snowRate = 0f;
    }

    public class ResearchProjectDefRecord
    {
        public string defName = "";
        public string? label = null;
        public float baseCost = 0f;
        public string techLevel = "";
        public string? requiredResearchBuilding = null;
    }

    public class SupportedDefFamiliesRecord
    {
        public List<ThingDefRecord> thingDefs = new List<ThingDefRecord>();
        public List<HediffDefRecord> hediffDefs = new List<HediffDefRecord>();
        public List<JobDefRecord> jobDefs = new List<JobDefRecord>();
        public List<SkillDefRecord> skillDefs = new List<SkillDefRecord>();
        public List<FactionDefRecord> factionDefs = new List<FactionDefRecord>();
        public List<BiomeDefRecord> biomeDefs = new List<BiomeDefRecord>();
        public List<WeatherDefRecord> weatherDefs = new List<WeatherDefRecord>();
        public List<ResearchProjectDefRecord> researchDefs = new List<ResearchProjectDefRecord>();
    }

    public class ContentProfileManifest
    {
        public string schemaVersion = ContentProfileProvider.MANIFEST_SCHEMA_VERSION;
        public string contentContractVersion = ContentProfileProvider.CONTENT_CONTRACT_VERSION;
        public string supportedCoverageProfile = ContentProfileProvider.SUPPORTED_COVERAGE_PROFILE;
        public string modPatchSupportStatus = ContentProfileProvider.MOD_PATCH_SUPPORT_STATUS;
        public string buildIdentity = "";
        public string assemblyCSharpMvid = "";
        public string assemblyCSharpSha = "";
        public List<DlcExpansionRecord> dlcExpansions = new List<DlcExpansionRecord>();
        public List<ModContentRecord> activeMods = new List<ModContentRecord>();
        public List<LoadedAssemblyRecord> loadedAssemblies = new List<LoadedAssemblyRecord>();
        public SupportedDefFamiliesRecord defFamilies = new SupportedDefFamiliesRecord();
        public List<string> capabilityFlags = new List<string>();
        public ModPatchSettingsDispositionRecord patchSettingsDisposition = new ModPatchSettingsDispositionRecord();
    }
}
'''

new_content = prefix + suffix_code.encode('utf-8')
with open(census_path, 'wb') as f:
    f.write(new_content)

print('Updated EngineHostCensus.cs, total bytes:', len(new_content))
with open(census_path, 'rb') as f:
    verify = f.read()
assert hashlib.sha256(verify[:72547]).hexdigest().upper() == 'F3C4F865F1E2A898BF240A2D096195870D77A52408CF2D93664FE15092A2A887'
print('Prefix integrity verified after write!')
