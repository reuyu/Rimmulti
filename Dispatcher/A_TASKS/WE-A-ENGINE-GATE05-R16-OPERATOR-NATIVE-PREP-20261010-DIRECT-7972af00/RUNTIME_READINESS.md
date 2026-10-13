# RUNTIME_READINESS

- **Dispatch ID**: `WE-A-ENGINE-GATE05-R16-OPERATOR-NATIVE-PREP-20261010-DIRECT-7972af00`
- **Work Package**: `WP_ENGINE_GATE05_R16_OPERATOR_NATIVE_PREPARATION`
- **Revision**: `GATE05-R16-OPERATOR-NATIVE-PREPARATION` (Envelope 19)
- **Status**: Read-Only Runtime Readiness Analysis / Zero Asset Copying / Zero Installation
- **Inspected Directory**: `C:\Users\user\Desktop\RimMulti\scratch\EngineGate05R4\RuntimeCopy`

---

## 1. Executive Summary

A critical prerequisite for executing genuine native semantic validation in Gate05 is having a complete, operational, and isolated RimWorld runtime environment. Historical Gate05-R4 developer testing reported a child process launch that hung and was terminated by the parent harness after a timeout.

This investigation conducted a full recursive audit of `scratch\EngineGate05R4\RuntimeCopy`. The investigation reveals that the directory contains **only 7 files** totaling **33,030,151 bytes**, consisting strictly of top-level executable binaries, version stamps, and historical R4 mod assemblies. The entire Unity engine data directory (`RimWorldWin64_Data/`), the Mono CLR embedding runtime, all core managed libraries (`Assembly-CSharp.dll`, `UnityEngine.dll`), and all core XML definitions (`Data/Core/`) are **completely absent**.

Consequently, the historical Gate05-R4 child process failure was not caused by OS permission issues, anti-virus interference, or DRM blocks: **the Unity standalone player executable was launched without its required engine assets and runtime data, rendering engine initialization physically impossible**.

---

## 2. Recursive File Inventory of `RuntimeCopy`

| Relative Path | Size (Bytes) | SHA256 Hash | File Classification |
|---|---|---|---|
| `RimWorldWin64.exe` | 666,624 | `4C30E2105B49F2D0130F5D861947FBE82B866042299DA48EF1C8CF6979A8564D` | PE32+ (x86-64) Executable |
| `steam_appid.txt` | 6 | `127E5A12E4BEEAC49D6FAEA428A003E76ACE71A2B23CBB17F17DD00991DD60D3` | ASCII text (`294100`) |
| `UnityCrashHandler64.exe` | 1,112,768 | `6DA75361F0EDDBE3492DF3C495AF7A1BA90FA6AE8C91D30BC857930F7DF63726` | PE32+ (x86-64) Executable |
| `UnityPlayer.dll` | 30,996,672 | `E0C489F1683609247FEDE45EA049D30BAA4F4542060E308E25C0EC87F6C0FB96` | PE32+ (x86-64) Dynamic Link Library |
| `Version.txt` | 17 | `0EC56B267649FAA48E8CD6BD767B14BAFE3D1359AF44434711105DBDC4597BE3` | ASCII text (`1.6.4871 rev590`) |
| `Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll` | 204,800 | `4F5663FDBBFA09A8B2BE460D09950FD22B9567459F7116E69D0B1C558F189B9E` | CLR .NET Assembly (Old R4 Candidate) |
| `Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.pdb` | 49,264 | `CC796E68C592C94345DF41D64609B5D207933B8F5FE805146875D9E61B8D12C4` | MSF Symbol Database (Old R4 PDB) |
| **Total** | **33,030,151** | — | **7 Files Across 4 Directories** |

*Note: Directory `UserData` exists within `RuntimeCopy` as an empty directory with 0 files.*

---

## 3. Root Cause Analysis: The R4 Killed Child Process

In the Gate05-R4 E1 report, test case execution reported an OS child process launch where the child failed to respond and was killed by the parent harness after a timeout (`PARENT_TIMEOUT_KILLED_CHILD`). Master review classified the root cause as `UNKNOWN`.

Based on our static audit of the exact disk contents in `RuntimeCopy`, the physical cause is now completely diagnosed:

1. **Unity Standalone Architecture**:
   - Unity Standalone Windows builds rely on a strict filesystem convention: an executable named `<Name>.exe` requires an adjacent directory named `<Name>_Data/`.
   - For `RimWorldWin64.exe`, the runtime strictly expects `RimWorldWin64_Data/` to be located in the exact same directory.
2. **Missing Initialization Assets**:
   - `RimWorldWin64_Data/boot.config` defines player initialization flags (e.g. `wait-for-native-debugger`, `player-connection-debug`).
   - `RimWorldWin64_Data/globalgamemanagers` and `resources.assets` contain the serialized Unity engine configuration and root scene definitions.
   - Without these files, `UnityPlayer.dll` cannot complete early engine initialization (`UnityMain` entry point).
3. **Headless Failure Mode**:
   - In windowed mode, Unity presents a dialog stating *"Failed to load player data"*.
   - In batchmode (`-batchmode -nographics`), standard GUI dialogs are suppressed. The executable halts early or hangs waiting on uninitialized subsystem handles without writing a log file.
4. **Conclusion**:
   - Launching `RimWorldWin64.exe` inside `scratch\EngineGate05R4\RuntimeCopy` can **never succeed** in its current state. The killed child in R4 was the direct, reproducible consequence of missing engine assets.

---

## 4. Comprehensive Inventory of Critical Missing Assets

To transition from pure static analysis to genuine native execution, the following asset groups must be staged from a licensed local installation under explicit Master approval:

### Group 1: Unity Engine Data Package (`RimWorldWin64_Data`)
- `boot.config`: Boot configuration directives.
- `globalgamemanagers`: Root engine configuration.
- `resources.assets`, `sharedassets*.assets`, `level*`: Compiled Unity game assets and scenes.

### Group 2: Mono Embedding CLR Runtime (`RimWorldWin64_Data\MonoBleedingEdge`)
- `EmbedRuntime\mono-2.0-bdwgc.dll`: Mono embedding virtual machine.
- `etc\mono\config` and machine configuration mappings: Required for .NET BCL assembly resolution.

### Group 3: Core Managed Libraries (`RimWorldWin64_Data\Managed`)
- `Assembly-CSharp.dll`: RimWorld gameplay logic, Verse, RimWorld, and Scribe subsystems.
- `UnityEngine.dll`, `UnityEngine.CoreModule.dll`, `UnityEngine.IMGUIModule.dll`: Unity engine managed wrappers.
- `mscorlib.dll`, `System.dll`, `System.Core.dll`, `System.Xml.dll`: .NET Framework 4.7.2 Base Class Libraries.

### Group 4: Core XML Game Definitions (`Data\Core`)
- `Defs\`: All vanilla XML definitions (ThingDefs, PawnKindDefs, JobDefs, HediffDefs, FactionDefs, BiomeDefs, WeatherDefs).
- `Languages\English\`: Translation dictionaries required by Verse initialization.
- `Patches\`: Core patch operations.

### Group 5: Official Expansions (`Data\<Expansion>`)
- Required if active ContentProfile specifies DLC expansions (`Data\Royalty`, `Data\Ideology`, `Data\Biotech`, `Data\Anomaly`).

### Group 6: Mod Loader Discovery Metadata
- `Mods\WarEconomy.WorkerBridge.PoC\About\About.xml`: Required by RimWorld's mod loader to recognize package ID `WarEconomy.WorkerBridge.PoC` and load the mod into the active mod list.
- Note: Current `RuntimeCopy` has only `1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll`, with no `About/` directory.

### Group 7: Isolated Configuration Files
- `UserData\Config\ModsConfig.xml`: Must explicitly list `<li>Core</li>` and `<li>WarEconomy.WorkerBridge.PoC</li>` as active mods to ensure the engine boots with the WorkerBridge mod enabled.
- `UserData\Config\Prefs.xml`: Ensures sound and graphics settings are disabled.

---

## 5. Licensing, Provenance, and Reference Code Boundaries

1. **Commercial Game Assets (Ludeon Studios EULA)**:
   - All RimWorld binaries (`RimWorldWin64.exe`, `UnityPlayer.dll`, `Assembly-CSharp.dll`) and game XML data (`Data/Core`) are commercial intellectual property owned by Ludeon Studios.
   - They cannot be redistributed, downloaded from external third parties, or modified in place.
   - Staging must occur exclusively as a read-only local copy from the user's licensed RimWorld installation into an isolated project directory.
2. **Reference Multiplayer Mod (MIT License)**:
   - Root: `Multiplayer-master\Multiplayer-master` (Copyright (c) 2018 Zetrith).
   - Serves as an architectural reference for `-batchmode -nographics` process launching (`HostUtil.StartArbiter`).
   - Lockstep desync trace hashing, peer synchronization, or disabled standalone map streaming are **not adopted** as WarEconomy authority contracts.
3. **Reference Rimworld-Together (CC BY-NC-ND 4.0)**:
   - Root: `Rimworld-Together-development\Rimworld-Together-development`.
   - §2(a)(1) prohibits public redistribution of adapted material.
   - Code from Rimworld-Together must not be copied directly into production WarEconomy assemblies. Concepts of server-client communication remain independent reference only.
4. **Installed Steam DLL Incident (`ENGINE-INSTALLED-IDENTITY-20261008-01`)**:
   - Baseline Expected SHA256: `2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C`
   - Observed Dispatch SHA256: `BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61`
   - Status: **OPEN / Actor UNKNOWN**. Developer A does not restore or normalize baseline hashes in Steam installation. Staging must rely strictly on project-controlled candidates.

---

## 6. Execution Isolation Specifications for Future Native Slice

When Master authorizes runtime staging and execution in a future slice, the following parameters must be strictly applied:

1. **Process Working Directory (`Cwd`)**:
   - Must be set explicitly to the root of the isolated runtime copy directory.
2. **CLI Arguments (`argv`)**:
   - `-batchmode`: Suppresses graphics window and main display initialization.
   - `-nographics`: Disables DirectX/OpenGL rendering pipeline and GPU context creation.
   - `-savedatafolder="<isolated_path>\UserData"`: Completely redirects all mod configs, saves, and caches away from `%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\`.
   - `-logfile="<isolated_path>\UserData\Logs\Player.log"`: Redirects Unity engine log output to ensure full evidence capture without overwriting user logs.
3. **Process Lifetime & Exit Verification**:
   - Operator process launcher must hold process handles, enforce timeouts, monitor standard numeric exit codes (`proc.ExitCode == 0`), and cleanly dispose process resources.
