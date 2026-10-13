# WarEconomy / RimMulti

RimWorld 1.6용 WarEconomy 모드 개발 저장소입니다. 현재 개발·검증 중이며 릴리스 승인을 의미하지 않습니다.

- 요구사항: [docs/요구사항_명세서.md](docs/요구사항_명세서.md)
- 최신 운영·판정: [docs/MASTER_GOVERNANCE_CURRENT.md](docs/MASTER_GOVERNANCE_CURRENT.md)
- 에이전트 지침: [AGENTS.md](AGENTS.md)
- 모드 소스: `WarEconomyMod/Source`
- Engine bridge 소스: `scratch/WorkerBridgeMod/Source`
- Operator publisher: `scratch/OperatorStartupPairR29/publish_operator_pair.py`
- Master 작업·통신 기록: `Dispatcher` 및 `docs/WarEconomy_Master_Handoff_20261006`

게임의 원본 DLL은 포함하지 않습니다. 빌드 시 본인 소유의 RimWorld 1.6 설치 경로를 각 프로젝트의 `RimWorldManagedDir` 등 참조 설정에 지정해야 합니다. 프로젝트별 대상 프레임워크·참조와 승인된 작업 범위를 확인하세요.

대용량 QA raw evidence, 저장 게임, frozen candidate 복사본, 빌드 산출물 및 로컬 실행 잠금은 로컬에 보존하고 Git에서 제외합니다. 문서의 절대 경로와 SHA/MVID는 기존 로컬 검증 기록이며, 이 저장소 clone만으로 모든 증거 파일이 복구되지는 않습니다.

참고한 별도 프로젝트의 로컬 checkout은 업로드하지 않습니다. 원본과 라이선스는 [RimWorld Multiplayer](https://github.com/rwmt/Multiplayer) 및 [RimWorld Together](https://github.com/RimworldTogether/Rimworld-Together)에서 별도로 확인하세요.
