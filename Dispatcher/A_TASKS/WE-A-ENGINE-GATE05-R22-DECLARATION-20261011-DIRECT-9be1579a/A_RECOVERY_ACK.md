# A Recovery ACK - R22

- Dispatch ID: `WE-A-ENGINE-GATE05-R22-DECLARATION-20261011-DIRECT-9be1579a`
- WP ID: `WP_ENGINE_GATE05_R22_EXPLICIT_DECLARATION`
- WP Revision: `GATE05-R22-DECLARATION`
- Envelope: 25
- Receiver: Antigravity Development Agent A
- Status: ACKNOWLEDGED / IN_PROGRESS
- Acknowledged At: 2026-10-11T07:34:00+09:00

## Scope Boundary
1. Narrow M01 repair ONLY: Remove default/optional checks in bootstrap CLI declaration, require all 7 explicit fields (`originId`, `launchPlanId`, `expectedConfigId`, `expectedRole`, `expectedCapabilityBoundary`, `expectedConfigPath`, `expectedConfigSha256`) before receipt issuance.
2. In receipt factory entry: clone caller descriptor once, validate complete 7-field copy before file/bytes admission, only use validated copy thereafter.
3. In `OperatorStartupAdmissionReceipt`: capture approved 7-field declaration privately, validate captured values in `ValidateAdmissionReceipt`.
4. Only modify the four allowed byte regions in `WorkerBridge.cs`:
   - Region 1 [1126, 5126]: `BOOTSTRAP_DECLARATION_ONLY`
   - Region 2 [176897, 177881]: `DESCRIPTOR_DEFAULTS_HELPER_CLONE`
   - Region 3 [178553, 179597]: `PRIVATE_CAPTURE_AND_CONSTRUCTOR_ONLY`
   - Region 4 [189890, 199521]: `RECEIPT_FACTORY_AND_VALIDATION_ONLY`
5. The 5 fixed binary segments must match 100% byte-for-byte.
6. `EngineHostCensus.cs` and `WorkerBridge.csproj` remain 100% immutable.
7. Pure positive normal managed runner only; ZERO C# Process APIs, ZERO live VerifyProcessIdentity, ZERO invalid/rejection probes, ZERO global state/Awake/native execution.
