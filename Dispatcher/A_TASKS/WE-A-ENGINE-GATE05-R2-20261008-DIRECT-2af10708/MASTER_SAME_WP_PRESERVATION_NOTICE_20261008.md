# 동일 R2 WP 보존 확인 — 새 WP 아님

작성 2026-10-08T10:07:25.447698+09:00; dispatch WE-A-ENGINE-GATE05-R2-20261008-DIRECT-2af10708 / WP_ENGINE_GATE05_R2 / GATE05-R2. 현재 구현 범위/번호는 유지하고 중복 작업을 시작하지 않는다.

Master는 새 ACK와 복구 보고서를 읽었다. 아래 실제 보존 불일치를 현재 작업의 A_WORK_LOG.md에 기록하고 원인·변경 작업·배포 경로·실제 로딩 identity를 근거로 설명한다.

- 기존 Steam 설치 DLL: C:\Program Files (x86)\Steam\steamapps\common\RimWorld\Mods\WarEconomy.WorkerBridge.PoC\1.6\Assemblies\WarEconomy.WorkerBridge.PoC.dll
- 기대 SHA256: 2D64FF9C56E4F5CB5E3395D10FCFDB1E56B6767F00CC351FBA93F9F132254A4C
- 실제 SHA256: BB3B52F39F7B53B70BC9FB4CE039E7455D08B24B17B8DABB8295E0FF4584DD61
- last-write metadata UTC: 2026-10-07T23:57:40.244423+00:00 (변경 주체/시각의 확정 증거 아님)
- archive19/Pipeline206/R1 frozen147은 Master 전체 파일 검사에서 보존됨.

이 기존 설치 경로는 승인 변경 목록에 없다. 추가 Steam 설치/core/ProbeMod 쓰기를 중단하고 자동 복구/덮어쓰기도 하지 않는다. 기존 증거/기대 해시는 수정하지 않는다. R2 native 작업은 승인된 프로젝트 내부 별도 licensed runtime copy에서 수행한다. 변경된 설치 DLL을 old Gate05 identity로 취급하거나 old E2를 재사용하지 않는다. 테스트 중이라면 먼저 읽기 전용으로 실제 candidate SHA/MVID/source/PDB/loaded profile을 기록한다. 알 수 없는 부분은 UNKNOWN으로 남긴다. 이 notice 때문에 새 구현 WP/재빌드/게임 종료를 임의로 만들지 않는다.

복구 보고서 정정: .git 부재는 Git clean 상태를 증명하지 않는다. 허용 경로는 task preservation_policy의 정확한 9개 파일이다. manifest SHA 일치와 manifest 내부 전체 파일 일치는 다르다. ACK/계획은 실행/PASS/closure 증거가 아니다.

완료 전 이 incident에 대한 답을 A_WORK_LOG.md 및 최종 report limitation에 넣는다. 보존 제약으로 진행 불가능하면 이유를 BLOCKED로 정직하게 보고한다. Master의 fresh candidate review/freeze 이후 독립 Sol E2는 별도다.
