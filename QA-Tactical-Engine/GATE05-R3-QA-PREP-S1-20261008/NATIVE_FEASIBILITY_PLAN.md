# Native 정상 실행 준비 — 실행하지 않은 계획

현재 R3 candidate admission/release가 없으므로 game/process 시작0, runtime copy 생성0, candidate 실행0, runner/Production 재빌드0이다. R2 NAT03의 DRM/redirect 설명은 SOURCE/RAW로 입증되지 않았고 원인은 UNKNOWN이다. 이 계획도 standalone 성공 또는 실패를 미리 선언하지 않는다.

## 별도 release 뒤 최소 preflight

1. Master가 admit/freeze한 새 R3 selected/alternate SHA/MVID, matching PDB/source/generated source, operator config, supported semantic/content version, immutable task 발급·protected channel 정책을 먼저 읽는다. 현재 R2/R1/old installed bytes를 substitute하지 않는다.
2. 승인된 licensed project runtime copy의 **명시 executable + 대응 game data/native libraries/Managed assemblies/mod content** inventory를 묶는다. working directory와 로더 탐색 위치도 그 copy 안인지 확인한다. Steam 원본/Workshop 설정/게임 core/ProbeMod/사용자 실제 save는 수정하지 않는다. 라이선스/보호를 우회하지 않는다. 필요한 파일이나 정상 사용 권한이 없으면 구체적인 제약으로 UNTESTED를 기록한다.
3. isolated save-data/profile/mod/config/task/stage/log/result paths를 project QA root에 준비하는 권한이 별도 WP에 있는지 확인한다. 원본 save는 승인된 입력 copy만 사용한다. 실제 game이 default user save-data를 쓰지 않는지 초기 startup log로 확인하며 모호하면 stop/UNOBSERVED로 처리한다.
4. operator가 선택한 고정 executable/config에서만 fresh worker/validator를 시작한다. CLI flags/quoting은 실제 admitted launcher와 로컬 runtime의 지원 동작을 확인한 뒤 확정한다. 현재 단계에서 실행 가능한 launch command나 새 launcher/harness를 만들지 않는다. process handle/PID/argv/cwd/start/end/exit, stdout/stderr 가능 여부, Unity/game log path, DLL/Core/mod 실제 loaded paths+SHA/MVID, profile canonical manifest/digest를 같은 run/task에 기록한다.
5. 최초 정상 startup/admission이 실제 관측돼야 staged A→B→C를 진행한다. 실제 staged bytes를 fresh loader가 읽은 경로/SHA와 target native map/census를 record한다. operator-issued expected context·actual validator context·result channel origin·consume·internal receipt·approved promotion을 matrix와 대조한다. display path/PID/파일 존재만으로 native semantic PASS를 선언하지 않는다.
6. 종료·timeout·취소는 자신이 생성한 정확한 handle/PID만 관리한다. 자연 native failure는 원문 error/loader log/exit를 그대로 수집하고 stage마다 UNOBSERVED/UNSUPPORTED/UNTESTED를 구분한다. DRM 등 원인 추정은 실제 observed evidence가 있을 때만 한다. 정상 승인된 lifecycle 재-admission controls를 수행하되 공격/위조 payload나 native protection 우회는 설계하지 않는다.

## 최소 로그 묶음

| 단계 | 필수 데이터 |
|---|---|
| before run | release/freeze/result IDs; candidate/core/mod/save-copy/dependency SHA+MVID; source/PDB match; config/approved profile/capabilities/version; protected-original hashes |
| process startup | exact handle/PID/start/cwd/argv/owner role; executable identity; isolated save-data/log/mod paths; loader errors |
| loaded admission | actual loaded WorkerBridge/core/mod inventories; Worker independently computed typed profile; target scope/map identity; current authority/grant/generation/incarnation/base lineage |
| fresh validation | validator process identity; actual staged path/bytes SHA read; independently computed profile; supported native census/manifest/hash; closed task/result context |
| operator acceptance | owned channel result observation/consume/cleanup; full context comparison; internal receipt origin; promotion primitive and final/backup SHA |
| terminal | exact owned process exits; evidence index/report hashes; preserved artifacts after hashes; partial coverage/untested fields; no automatic closure |

## Multiplayer 참조의 의미

읽은 local `Multiplayer-master/Multiplayer-master/Source/Client/Networking/HostUtil.cs:214..253`는 현재 executable에서 arbiter child를 시작하고 save-data/log/network arguments 및 start exception을 다룬다. 이 런처 형태는 참고할 수 있지만 MP arbiter의 의미는 lockstep 비교 참가자이며 우리 staged fresh semantic validator가 아니다. source를 읽은 것이 실행 PASS가 아니다. headless flags가 모든 Unity/Def loader 성공이나 zero drift를 보장하지 않는다. 프로젝트의 REFERENCE_MOD_REUSE_ANALYSIS는 검증된 adapter가 아니라 참고 분석이다. 이번에는 참조 모드를 설치/빌드/실행하거나 코드를 옮기지 않았다.

이 정상 준비는 G-Q1 independent simultaneous clocks나 exact PlayerGlobal schema/owner/physical split을 결정하지 않는다. Weather/Storyteller/Tales/PlayLog differences를 discardable로 승인하지 않는다. clock/resume 비교는 허용된 같은 schedule control과 supported manifest의 원칙을 따른다.
