# A Recovery Acknowledgment — R25 Role UserData Selection
- **Dispatch ID**: `WE-A-ENGINE-GATE05-R25-ROLE-USERDATA-20261011-DIRECT-dd341868`
- **Work Package**: `WP_ENGINE_GATE05_R25_ROLE_USERDATA_SELECTION`
- **Revision**: `GATE05-R25-ROLE-USERDATA` (Envelope 28)
- **Timestamp**: 2026-10-11T21:32:00+09:00
- **Receiver**: Antigravity Development Agent A
- **Controlling Review**: `MASTER_REVIEW_ENGINE_GATE05_R24_DUAL_M04_PREPARATION_20261011.md` (SHA `BE20FB28...`)
- **Scope Baseline**: `MASTER_R25_SCOPE_BASELINE.json` (SHA `371E4B39...`)

## Scope Boundary & Invariants
1. **Master R24 Corrections Acknowledged & Adopted**:
   - R24 non-adopted proposals (invented operator CLI flags, native child frontend assertions, cryptographic capability signature requirements, null/fallback oracle tests, Span C launcher modifications) are strictly excluded.
   - Launcher, cwd, child process registration, ProcessStartInfo, schema definitions remain 100% BYTE FIXED.
2. **Authorized Modifications (3 Spans, 4 Fixed Segments)**:
   - Span 1 (15691..16046): Replace active admitted config branch in `SafeSaveDataFolderPath` with `OperatorRolePathSelector.SelectUserData(_activeStartupConfig)`.
   - Span 2 (22390..22654): Update Awake log line to display `DeclaredRoleUserData`.
   - Span 3 (166282..166282): Insert pure `OperatorRolePathSelector` class immediately before Gate05-R18 region.
   - Segments 0, 1, 2, 3 in `WorkerBridge.cs` verified against master binary fixtures.
3. **Immutability Commitments**:
   - `EngineHostCensus.cs` and `WorkerBridge.csproj` remain strictly immutable.
   - 6 project DLL/PDB files to be recompiled under Debug and Release configurations.
   - 4-case pure normal unit runner (2 fresh child runs in en-US and de-DE) without C# Process APIs, VerifyProcessIdentity, global WorkerBridge component, or negative/rejection probes.
