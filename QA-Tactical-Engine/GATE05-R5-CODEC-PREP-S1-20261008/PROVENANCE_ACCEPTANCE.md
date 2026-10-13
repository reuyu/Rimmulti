# Final candidate provenance acceptance matrix

이번 QA에 released R5 candidate 없음/NOT_REVIEWED. 아래는 후속 final candidate admission을 위한 정상 provenance 확인 계획이다. QA는 mutable R5source/bin/obj를 읽거나 build/run하지 않는다. Historical R4 PACKAGING_INDEX.json의 pre-run5 identity mismatch/before7 size mismatch를 구체 기준으로 연결했다.

| Row | 정상 acceptance / 필요한 실제 증거 | R4 교훈 / 현재 상태 |
|---|---|---|
| P01 Final build boundary | 마지막 Debug/Release build 종료 후 source/generated/dependency/content/config 고정, 새 unique run_id; 이후 source/build 변경 시 새 candidate/run/snapshot | R4 before DebugBB32/PDBF862/Worker87CA/Release5E79/PDB3E52가 final4F56/CC79/BA28/7532/53E33과 다름. Final5 identity rows는 pre-run 재사용 불가 |
| P02 Selected/alternate distinction | 각각 absolute path/SHA/actual size/MVID/config/framework; 실제 실행 selected와 대안 Release 구분. Deployed alternate도 별도 role | Raw PROV identity 보고는 인정하되 actual loaded selected proof와 구분 |
| P03 PE/PDB/source graph | exact selected/alternate DLL CodeView/PDB GUID/document checksum, source/generated/manifest identity; original names는 matching frozen source에만 매핑 | R4 source4/4 matching은 유효 metadata evidence; native execution proof 아님 |
| P04 Dependency/tooling | actual build arguments + exact tooling version + admitted dependencies SHA/MVID/size + runner entry/dependencies; loose '8.0+'만 exact snapshot으로 보지 않음 | 최종 assembly를 로드한 환경과 captured metadata 비교. 미관측 항목은 NOT_OBSERVED |
| P05 Content/config/codec | typed contract/version/capabilities/production entry, captured normal input snapshot/actual runtime snapshot 여부와 config identity | synthetic codec inputs와 실제 loaded profile를 별도 roles/labels |
| P06 Pre-run issuance | 마지막 build **뒤 run 전** exact selected/alternate/PDB/source/generated/dependency/tooling/content/config/run_id를 immutable 파일로 기록; hash actual bytes | 사후 파일 생성시각/사후freeze만으로 실행 전 proof 소급 금지. 시간 주장만 아닌 source/build/run raw 순서와 identity 필요 |
| P07 Normal run binding | run_id/argv/cwd/entry/candidate-loaded SHA/MVID/raw/results/inputs/bytes/decoded/digest와 pre-run exact identity를 연결 | codec runner OS process가 게임/native 의미를 자동 증명하지 않음. No candidate execution row는 NOT_OBSERVED |
| P08 Post-run unchanged | 동일 pinned artifacts의 SHA/size/MVID/source/PDB/dependency/content 재대조; 새 build/run이면 이전결과 provenance separate | unchanged bytes와 final report/manifest identity 일치. 검토 후 snapshot이 before-run 대체 아님 |
| P09 Preservation baseline | archive19/prior619/Pipeline206/QA1222 및 manifests/terminal actual path/SHA/**size** 전후. Mutable authorized Engine outputs는 old candidate lineage 아님 | R4 before9 hash 맞음/size7 틀림: csproj2210→actual1774, Debug103936→199168, DebugPDB175616→48620, Release89088→190464, ReleasePDB175616→36860, deployed DLL89088→190464/PDB175616→36860. Producer before 원문 고치지 않고 actual immutable baseline으로 판정 |
| P10 Report/manifest/completion | actual bytes로 tables/roles/absolute paths/SHA/size/MVID/argv/counts 계산. Unique result/timezone/exact delivery/WP/revision/limitations string/list; completion 마지막 발행 | R4 final18 artifact/report9 match 개선 유지. Meaningful object limitation을 missing으로 오인하지 않되 새 표준 형식 준수 |
| P11 Evidence scope | raw 실행 vs source assertion vs synthetic codec vs actual loaded profile vs native issuer/lifecycle를 row별 구분 | count/100%/flag/cryptographic identity를 authority/runtime PASS로 확대 금지 |
| P12 Transport/admission | ACK/완료 direct report tool 반환/unique result/dedupe 저장, Master candidate review/freeze/admission 및 후속 independent 실행 WP | 파일 존재는 전달/실행/closure proof 아님. QA 준비 완료는 R5 검토 완료 아님 |

Known installed incident expected2D64…/observedBB3B…는 기존 OPEN/actor·cause UNKNOWN이다. QA는 원본 installed/UserData를 다시 읽지 않았고 restore/hash normalization도 하지 않는다. QA preparation preservation은 immutable project inventories와 해당 terminal/manifests를 검증한다. 기존 installed baseline이 완전히 보존됐다는 주장은 없다.
