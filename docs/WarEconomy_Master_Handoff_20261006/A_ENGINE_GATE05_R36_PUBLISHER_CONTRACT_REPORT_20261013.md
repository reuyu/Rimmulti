# Agent A 작업 완료 보고서: Gate05 R36 Publisher Contract 보완 및 AST 검증

**작업 패키지**: `WP_ENGINE_GATE05_R36_PUBLISHER_CONTRACT` / `GATE05-R36-PUBLISHER-CONTRACT` (Envelope 39)  
**디스패치 ID**: `WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-20261013-DIRECT-d2d6556b`  
**보고 일시**: `2026-10-13T14:40:23.550380+00:00`  
**작성자**: Agent A  
**결과 ID**: `WE-A-ENGINE-GATE05-R36-PUBLISHER-CONTRACT-RESULT-01`  
**E1 판정**: `SOURCE_SYNTAX_ONLY_PUBLICATION_NOT_EXECUTED`

---

## 1. 작업 개요

Master 지시 및 계약 문서([`MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md`](file:///C:/Users/user/Desktop/RimMulti/docs/WarEconomy_Master_Handoff_20261006/MASTER_R36_PUBLISHER_CONTRACT_SUPPORTED_DOMAIN_20261013.md))에 따라, 단일 변경 허용 대상 파일인 독립 publisher 스크립트([`scratch/OperatorStartupPairR29/publish_operator_pair.py`](file:///C:/Users/user/Desktop/RimMulti/scratch/OperatorStartupPairR29/publish_operator_pair.py))의 계약 안전성 보완을 완료하였습니다.

본 작업은 Engine 재빌드 금지, publisher 실행 금지, 단위/네이티브 테스트 실행 금지, 1.7 마이그레이션 금지 경계를 엄격히 준수하였으며, 표준 라이브러리 AST 파서(`ast.parse`)를 통한 구문 무결성 검증(`SYNTAX_PASS`, 종료 코드 0)만을 수행하였습니다.

---

## 2. 주요 구현 및 수정 사항 (8대 기술 요건 반영)

1. **스키마 버전 엄격 일치**: `schemaVersion == "WE-OPERATOR-BOOTSTRAP-V1"` 엄격 검증 구현.
2. **원시 역할(Role) 엄격 일치**: 부모 `"SIMULATION"`, 자식 `"READ_ONLY"`에 대해 strip/대소문자 변환 없는 원시 문자열 엄격 일치 검증.
3. **configId 비어있지 않음 및 서수 일치**: `configId`가 공백이 아님을 검증하고, 원시 서수 일치 및 스냅샷 trim 서수 일치 적용.
4. **디스크립터 SHA-256 서식 엄격화**: 디스크립터의 `expectedConfigSha256`이 공백/패딩 없는 정확한 64자리 ASCII 16진수인지 검증. 실행 파일 SHA-256은 trimmed 64자리 16진수 검증.
5. **로컬 DOS 경로 검증 및 UserData 격리**: 완전 경로 DOS 루트 검증, 제어 문자/ADS/예약 장치명 거부, 정규화된 worker와 validator UserData 경로가 상호 상이함을 보장.
6. **expectedContentProfileFingerprint 비어있지 않은 문자열 허용**: 64자리 16진수 제약을 완화하고 비어있지 않은 문자열로 검증.
7. **패키지 정책 리비전 불리언 제외**: `policyRevision`이 문자열 또는 정수임을 허용하되, 불리언(`bool`) 타입을 명시적으로 거부(`not isinstance(val, bool)`). 패키지 ID 순서 보존.
8. **ISO 8601 타임스탬프 1..7자리 소수점 원본 보존**: 그레고리력 UTC ISO 8601 형식 검증 및 원본 소수점 자릿수(1..7자리)를 6자리로 반올림하거나 자르지 않고 그대로 보존.
9. **재사용 가능한 전체 조상(Ancestry) 경로 검사기**: `os.lstat`을 사용하여 심볼릭 링크나 정션(reparse point)을 따라가지 않고 모든 조상 디렉터리의 안전성을 재귀 검사하며, 검사 실패 시 fail-closed 처리.
10. **엄격한 `--spec` CLI 호출 모드**: 명령행 인자를 정확히 3개(`publish_operator_pair.py --spec <spec_path>`)로 제한하고 인라인 플래그 모드를 fail-closed 처리.

---

## 3. 검증 결과

1. **Publisher 구문 검증**:
   - 도구: `scratch/EngineGate05R36PublisherContract-d2d6556b/ast_checker.py`
   - 프로세스 PID: `19052`, 종료 코드: `0`
   - 판정: `SYNTAX_PASS`
   - raw stdout: 861 bytes, raw stderr: 0 bytes
2. **Engine 9개 기준 파일 무결성 보존**:
   - `WorkerBridge.cs`, `EngineHostCensus.cs`, `WorkerBridge.csproj`, Debug/Release DLL+PDB, 1.6 Assemblies DLL+PDB 모두 기준 해시 및 바이트 수와 100% 일치 (빌드 0회).
3. **불변 경계 준수**:
   - Publisher 런타임 실행 0회, 게임/엔진 런타임 실행 0회, 네이티브 실행 0회.

---

## 4. 거버넌스 및 권한 원칙

- **Dedicated Server Authority**: Dedicated Server가 최종 Domain Authority이며, Engine/Client는 제한된 시뮬레이션 제안만을 생성합니다.
- **Foundation HOLD**: Pipeline 독립 E2 PASS 전까지 Foundation은 HOLD 상태를 유지합니다.
- **Steam 설치본 불일치**: 원인 미상의 기존 Steam 설치본 불일치 이슈는 OPEN 상태로 보존됩니다.
