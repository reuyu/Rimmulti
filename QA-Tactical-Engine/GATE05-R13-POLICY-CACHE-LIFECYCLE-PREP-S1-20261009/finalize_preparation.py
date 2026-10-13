from preparation_setup import *
TERMINAL={'EVIDENCE_MANIFEST.json','RESULT_INDEX.json','ACK_COMPLETION_BINDING.json','COMPLETION.json','RETURN_PENDING.json','RETURN_TOOL_PROOF.json','DELIVERY_STATUS.json'}
def link(p,label=None):return '['+(label or p.name)+']('+p.as_posix()+')'
if __name__=='__main__':
    assert not REPORT.exists() and not any((Q/n).exists() for n in TERMINAL)
    ack=load(Q/'ACK_INITIAL.json');assert load(Q/'ACK.json')==ack
    before=load(Q/'PRESERVATION_BEFORE.json');after=preservation()
    def ids(d):return {r['path'].lower():(r['sha256'],r['bytes']) for r in d['files']}
    assert ids(before)==ids(after);write(Q/'PRESERVATION_AFTER.json',dict(after,all_preexisting_sha_size_matched=True))
    oracle=load(Q/'NORMAL_LIFECYCLE_REFERENCE_ORACLE.json');normal=load(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json');static=load(Q/'STATIC_REVIEW_CRITERIA.json');pack=load(Q/'PER_PROCESS_PACKAGING_ACCEPTANCE_CHECKLIST.json')
    assert len(normal['rows'])==18 and len(static['rows'])==15 and len(pack['criteria'])==18 and len(oracle['reference_files'])==10
    for r in oracle['reference_files']:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes']
    for name,p in oracle['policies'].items():
        ref=Path(p['canonical_policy_file']['path']);assert sha(ref)==p['expected_digest'] and load(ref)==p['expected_canonical_declaration']
        full=Path(oracle['manifests'][name]['historical_r12_content_reference']['path']);assert sha(full)==oracle['manifests'][name]['expected_historical_r12_fingerprint']
    report=f'''# Gate05 R13 policy/cache lifecycle — QA preparation S1

판정 **PREPARATION_COMPLETE_R13_NOT_REVIEWED**. 동결 R12 자료를 읽고 향후 R13의 정상 정책/캐시 lifecycle·ownership·실행별 증거 보관 기준을 준비했다. 후보 build/assemblyload/run/configuration/cache/provider/native/game/operator/controls는 모두0이다. R13 구현/API/epoch는 관측하지 않았으며 후보 PASS·runtime E2·closure를 주장하지 않는다. Engine002/006·Pipeline007/current schema·G-Q1 OPEN, Foundation HOLD. Dedicated Server final runtime Domain Authority, Master release/closure governance를 유지한다.

Producer Sol / WP `{ack['wp_id']}` S1 / delivery `{ack['delivery_id']}` / result `{ack['result_id']}`. 완료 시각 {now()}. {link(WP,'준비 WP')} SHA `3DDA11D7B4B7D9117947BB8ADC8A5C861CC51522E842158F1D96D2993EE74989` 및 {link(PKG/'WP_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE.md','A 작업 목표')}/{link(PKG/'RELEASE_ENGINE_GATE05_R13_POLICY_CACHE_LIFECYCLE_20261009.md','개발 release 범위')}를 읽었다. A 목표는 구현 관측 증거가 아니다. Mutable R13 source/bin/obj/runner/ACK/completion/실제 producer release manifest는 읽지 않았다. 표준 JSON/hash 처리와 새 QA 문서 생성만 수행했다.

| 준비 산출물 | 실제 수량·상태 |
|---|---|
| 보호 baseline | 5,901 unique path 전후 SHA/size 일치; baseline873F3E2F715A0A52B58E80198A5A7DDD07672498B944DF7A667319C04196ECD7 |
| 정상 lifecycle/회귀 acceptance criteria | 18개, 실행0 |
| 방어적 static criteria | 15개, adverse 실행0 |
| 실행별 immutable evidence acceptance criteria | 18개, 실제 process 관측0 |
| 동결 R12 source anchor/snippet | 10개 |
| 독립 정책·전체 content reference 파일 | 10개, 정책 A/B 각5개 |
| fulltyped reference | 179leaf/template ×2 =358 rows, 실제 candidate 비교0 |
| R13 generation/type/epoch/API/header/clone/formatter | UNOBSERVED, 동결 후 finalbuild/calls 전에 reconcile |

읽은 동결 후보는 R12 source SHA `5E9A4DE9A6280A887E3659CE2D80A8029C2BEF41DC615BB3F6F1BB859B1F020E`와 POST_COMPLETION72-file manifest SHA `824747638CC2B71EB42CB778CBA90F8EA4DB3A9C388306AA6D3BC48D868F2A18`다. {link(Q/'FROZEN_R12_STATIC_ANCHORS.json')}에 실제 line/snippet을 남겼다. 기존 설치 incident를 reread/restore하지 않았고 Production/A/governance/scheduler를 수정하지 않았다. 최초 ACK 및 기존 QA/후보 증거를 보존했다.

R12 source는 Configure가 `_policyLock` 안에서 정책 snapshot만 바꾸고 Clear는 정책만 null로 만들며, fingerprint/JSON/manifest 캐시 무효화는 함께 수행하지 않는다. GetActual은 기존 fingerprint를 즉시 반환하고 세대 바인딩을 검사하지 않는다. CachedManifest는 저장된 mutable instance를 그대로 반환하며, 실제 Compute의 JSON/manifest store도 별도 필드다. 이 **정적 관측**이 R13 lifecycle 수정의 근거다. 옛 provider/cache를 호출하거나 stale/mismatch/race 상황을 재현하지 않았다. 새 구현에서 하나의 동기화/state 해석·current stamp guard·owned coherententry로 이 문제를 어떻게 해결했는지는 아직 UNOBSERVED다.

{link(Q/'NORMAL_LIFECYCLE_REFERENCE_ORACLE.json')}은 정상 정책 A/B를 독립적으로 선언한다. 같은 valid unique0-based package inventory에서 opaque ID/revision을 별도로 바꿨다. current-v1 canonical policy digest는 A `{oracle['policies']['A']['expected_digest']}`, B `{oracle['policies']['B']['expected_digest']}`다. 기대 정책을 실제 inventory/후보 출력에서 생성하지 않았다. normal package spelling과 invariantlowercase declaration, exact whitespace/tab/Unicode/quote/backslash/newline/string007 의미를 보존한다.

전체 manifest/JSON/fingerprint reference는 **역사 R12 형식의 독립 literal template**다. R12 실행 전 own reference encoder로 정의했던 bytes에 별도 선언 A/B 정책 문자열·digest/boundary만 표준 JSON escaping으로 치환했고, 전체179leaf의 float32 exact bits/정수/문자열/list 의미를 확인했다. 새 후보 Serialize를 기준 생성에 사용하지 않았다. 이 JSON·SHA를 R13 실제 canonical fingerprint로 가정하지 않는다. 미래 R13 header/capability/API/type/formatter를 동결 후 build/calls 전에 고정하고 기대 bytes를 새로 준비해야 한다. shared primitive Json.NET/vendor 한계는 그대로 유지한다. {link(Q/'TYPED_ENTRY_REFERENCE_PLAN.json')} 참조.

Normal flow는 standalone 순수 instance의 초기 emptydiagnostic → ConfigureA(record) → input/returnedpolicy caller ownership → matchingA coherententry publication → 반복query/manifest ownership → legitimate ConfigureB(declaration)의 Aentry 제거 → matchingB publication/query → explicitInvalidate → samepolicy reconfigure → Clear 및 새 instance declaration parity로 나눴다. fullpolicyID/revision/digest/list, fullmanifest/orderedmods-version association, JSON/UTF8 SHA, current generation/context, caller 상태를 각각 비교하도록 명시했다. nonempty/count/status만으로 PASS를 판정하지 않는다. 세대 초기값·증가 폭·typewidth·samepolicy/Clear/Invalidate의 policygeneration/cacheepoch 관계는 **UNOBSERVED**이며 숫자나 helper 이름을 발명하지 않았다. Operational generation은 canonical revision/WorldTick/fencing/domain authority가 아니다.

입력·반환 정책/list 및 manifest/nestedchild의 평범한 caller edits는 standalone instance의 소유권만 검증한다. 편집된 data를 mismatch/stale stamp로 재제출하거나 global profile에 주입하지 않는다. 별도 instance core는 globalprovider/canonicalstate에 도달하지 않아야 한다. Globalprovider의 real entry는 내부에서 실제 loaded-content를 계산하고 current policy/context stamp를 검사하여 publish한 것만 허용한다. Public static Seed/Install/Override fingerprint/cache, private reflection mutation, test bypass, caller-authorized actual-profile publication은 금지다. 이 boundary는 static 검토하고, standaloneunit PASS는 native actual-cachehit/loadedprofile/operator authority를 증명하지 않는다. {link(Q/'OWNERSHIP_AND_AUTHORITY_BOUNDARY_PLAN.json')} 참조.

Global future R13 검증은 새 exact freeze/admission에서 별도 허용될 valid Configure A/B, Configured snapshot, Clear, Invalidate 및 pureempty cached diagnostics만 계획했다. Native Compute/GetActual/Worker/game/operator/control-plane/promotion은 분리한다. Clear 뒤 emptystate에서 actual admission/Compute를 호출해 rejection test를 만들지 않는다. Stale/mismatched stamps, race/negative/adverse fixture 역시 만들거나 실행하지 않는다. {link(Q/'FUTURE_API_RECONCILIATION_REQUIREMENTS.json')}은 실제 API/field/clone/current-generation publication reachability/header/byteformatter를 최종 runner build 전에 채택하도록 요구한다.

회귀 계획은 새 R13 후보에서 R12 full9Checkfields/rawphysical/effective/expected spelling/wholecaller immutability/twoadmission/fullpackage-version association, policy-bearing fresh-originaltrue BEFORE external Normalize, current-v1 encoding과 R9 optionalunknown/null/empty/known/distinct/reverse/genericversion 의미를 독립 기준으로 재검증하는 것이다. Float32 bits/Int32/largeInt64/exactUnicode/orderedverbs-stages-Comps multiplicity/normal distinctsets도 포함한다. 과거65leaf·R12 PASS는 native wholegraph coverage 또는 R13 PASS로 승계하지 않는다. General schema/guardparity/patchsettings/material/operator/native/all-contentdrift completeness는 별도 OPEN이다.

{link(Q/'IMMUTABLE_PER_PROCESS_OUTPUT_CONTRACT.md')}와 {link(Q/'PER_PROCESS_PACKAGING_ACCEPTANCE_CHECKLIST.json')}는 **process마다 고유 immutable output directory**를 요구한다. 모든 hidden/nested/generated file을 재귀 열거하고 absolute/relative path·bytes·SHA를 저장한다. 옛 central filename/prefix 목록으로 골라 복사하지 않는다. 원본 input/reference copies, 모든 결과와 caller/entry/generation/context sidecar, actual loaded observation, fullstdoutstderr, numericexit/tool proof를 포함해야 한다. Inventory 자체의 self-cycle 제외는 enclosing index의 hash로 결속하며 sidecar 제외는 허용하지 않는다. 실제 pathset/count를 별도 재귀 enumeration으로 확인하고 RUN1 inventory를 RUN2 시작 **전에** 완료한 뒤 RUN2 전후로 재확인한다. 실제 process context 원본과 로그로부터의 derived summary를 구분한다.

향후 execution graph는 actual finalbuild → resolved toolchain/source/runner/candidate/oracle prepin → 실제 argv/cwd/runID/PID/culture/원문/calls → 실제 numericexit/loadedidentity/post → full immutable inventory → 문화권 간 fulltyped/canonical 비교 순서다. 같은 최종 runner/originalinput을 freshen-US/de-DE에 사용하고, normal FAIL은 원본 candidate/oracle/runner/raw를 유지해 보고한다. 결과를 본 후 기준 수정·재빌드·rerun-to-pass하지 않는다. 완성된 증거/report/manifest/index/ACKbinding 뒤 COMPLETION을 last로 만들고 실제 Master 전송은 별도 저장한다. 준비 단계에는 실행 graph 관측이 없다.

{link(Q/'HISTORICAL_R12_QUALIFICATIONS_PRESERVED.json')}에서 Master의 R12 scoped PASS를 reference credit으로 유지한다. RUN1 ACTUAL_PROCESS_CONTEXT/REFERENCE_BYTE_STAGE/ORDER_POLICY_RESULTS3sidecar 원본 미보관과 derived raw/tool context qualification, shared primitiveJson.NET 한계, producer validJSON/primaryrunID partial correction 및 incomplete compiler/input/culture/numericexit graph는 그대로 보존한다. 원본 누락 file을 복구한 것처럼 작성하거나 재실행하지 않는다. OldR11 invalidJSON/R8 FAIL/R9 좁은 historical closure도 변경하지 않는다.

준비 작업은 완료됐으며 exact 새 R13 후보에 대한 Master freeze/admission과 fresh independent WP를 기다린다. R13 A terminal 존재에 관한 통신을 구현 완료·admission·runtime PASS로 해석하지 않았다. 본 보고서는 새 A 지시·자동화·closure/release를 생성하지 않는다. 결과 graph와 한 번의 직접 Master 완료 보고를 별도로 결속한다.
'''
    REPORT.write_text(report,encoding='utf-8')
    common=dict(schema_version=1,producer='Sol',report_kind='QA_PREPARATION_S1',wp_id=ack['wp_id'],wp_revision=ack['wp_revision'],delivery_id=ack['delivery_id'],result_id=ack['result_id'],status='COMPLETED',verdict='PREPARATION_COMPLETE_R13_NOT_REVIEWED',r13_candidate_verdict='NOT_REVIEWED',timezone='Asia/Seoul',normal_criteria=18,static_criteria=15,packaging_criteria=18,reference_files=10,frozen_source_anchors=10,typed_template_leaves_per_policy=179,typed_template_rows=358,protected_unique_paths=5901,preservation_matched=True,qa_runner_builds=0,assembly_loads=0,candidate_runner_processes=0,controls_executed=0,configuration_cache_provider_game_native_operator_old_stale_mismatch_rejection_race_negative_adverse=0,production_governance_scheduler_a_changes=0,runtime_e2_released=False,closure_changed=False,foundation='HOLD',limitations=['FrozenR12 read-only preparation;R13 implementation/APIs/generation/epoch/header/formatter/clone semantics unobserved','Fullcontent byte/FP references are historical R12 templates only,futureR13expectedbytes reconcile BEFOREfinalbuildcalls','No candidate build/load/run/normal controls;reference processing not runtimePASS','Standalonecore unitcoverage doesnotprove nativeactualprofile/cachehit/operatorauthority/globalprofilecontext','R12three-sidecar/sharedprimitiveJSON/vendor/producerpartialgraph qualifications preserved;no restoration/rerun','General schema/guardparity/cache-all-contentdrift/patchsettings/operator/native/currentgates remain separateOPEN'])
    files=[row(p) for p in sorted(Q.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and not (p.parent==Q and p.name in TERMINAL)];files.append(row(REPORT));assert len({r['path'].lower() for r in files})==len(files)
    write(Q/'EVIDENCE_MANIFEST.json',dict(common,at=now(),file_count=len(files),files=files,excluded='Root terminal/transport and __pycache__ avoid cycles;terminalexternallybinds manifest'))
    write(Q/'RESULT_INDEX.json',dict(common,at=now(),artifact_count=len(files),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),normal_oracle=row(Q/'NORMAL_LIFECYCLE_REFERENCE_ORACLE.json'),normal_matrix=row(Q/'POSITIVE_NORMAL_ACCEPTANCE_MATRIX.json'),static_criteria_file=row(Q/'STATIC_REVIEW_CRITERIA.json'),packaging_checklist=row(Q/'PER_PROCESS_PACKAGING_ACCEPTANCE_CHECKLIST.json'),preservation_before=row(Q/'PRESERVATION_BEFORE.json'),preservation_after=row(Q/'PRESERVATION_AFTER.json'),report_delivery='PENDING_DIRECT_MASTER_RETURN',destination='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local'))
    write(Q/'ACK_COMPLETION_BINDING.json',dict(common,at=now(),ack_initial=row(Q/'ACK_INITIAL.json'),ack=row(Q/'ACK.json'),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),result_index=row(Q/'RESULT_INDEX.json'),initial_ack_preserved=True))
    comp=dict(common,completed_at=now(),artifact_count=len(files),report=row(REPORT),evidence_manifest=row(Q/'EVIDENCE_MANIFEST.json'),result_index=row(Q/'RESULT_INDEX.json'),ack_completion_binding=row(Q/'ACK_COMPLETION_BINDING.json'),primary_graph_complete=True,report_delivery='PENDING_DIRECT_MASTER_RETURN');write(Q/'COMPLETION.json',comp)
    for r in files+[comp[k] for k in ['report','evidence_manifest','result_index','ack_completion_binding']]:
        p=Path(r['path']);assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes']
    write(Q/'RETURN_PENDING.json',dict(at=now(),result_id=ack['result_id'],status='PENDING_ONE_AUTHORIZED_TERMINAL_SEND',destination='01a1156b-97ec-7ce0-9e4a-dfc4a3acb174/local',report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json')))
    print(json.dumps(dict(result_id=ack['result_id'],artifact_count=len(files),protected_unique_paths=5901,report=row(REPORT),manifest=row(Q/'EVIDENCE_MANIFEST.json'),index=row(Q/'RESULT_INDEX.json'),completion=row(Q/'COMPLETION.json')),indent=2))
