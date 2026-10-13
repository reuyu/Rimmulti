from common import *
import uuid
controls();root_stats=ancestry(Q,leaf_dir=True);source_stats=ancestry(S);write(Q/'ROOT_ANCESTRY_OBSERVATION.json',dict(at=now(),root=root_stats,candidate=source_stats,prior_creation_tool='d6e439: six existing parents directory/no reparse observed before new Q creation',ownership='User-authorized owned workspace; protected local owner/no hostile concurrent writer assumption; ACL/TOCTOU not attested'))
audit=load(OLDQ/'RECOVERY_AUTHORITY_AUDIT.json');texts=[]
for r in audit['files']:
    p=Path(r['path']);texts.append(dict(**row(p),full_text=p.read_bytes().decode('utf-8-sig')))
for p in [WP,ADMIT,EXPECTED,PKG/'MASTER_REVIEW_ENGINE_GATE05_R38_INDEPENDENT_STATIC_S1_20261014.md']:
    texts.append(dict(**row(p),full_text=p.read_bytes().decode('utf-8-sig')))
write(Q/'RECOVERY_FULL_TEXT.json',dict(at=now(),files=texts));write(Q/'RECOVERY_AUTHORITY_AUDIT.json',dict(at=now(),files=[{k:v for k,v in r.items() if k!='full_text'} for r in texts],full_reads=len(texts)))
ad=load(ADMIT);check([ad['admitted_candidate'],ad['review'],ad['static_verification'],ad['expected_oracle'],ad['protected_baseline']]);assert ad['new_QA_root']==str(Q) and ad['allowed_candidate_calls']==6
orig=load(ORIGINAL);uprows=[orig['literal_pair'],orig['literal_combined']];check(uprows);up1={c['case_id']:c for c in load(uprows[0]['path'])['prospective_cases']};up2={c['case_id']:c for c in load(uprows[1]['path'])['pair_cases']}
oldcases={c['case_id']:c for c in orig['cases']};ex=load(EXPECTED);assert ex['case_ids']==ad['allowed_case_ids'] and len(ex['cases'])==6
verification=[]
for c in ex['cases']:
    old=oldcases[c['case_id']];assert c['operatorPairId']==old['expected_aux4']['operatorPairId']
    oldbundle=literal(old['expected_bundle']);assert c['original_bundle_literal_identity']['sha256']==old['expected_bundle']['sha256'] and c['original_bundle_literal_identity']['bytes']==len(oldbundle)
    expected=oldbundle
    for inp,oldinp in zip(c['inputs'],old['inputs']):
        b=literal(inp['raw_config']);assert b==literal(oldinp['raw_config_expected']);decoded=json.loads(b.decode('utf-8'));assert decoded==oldinp['config14'];role=inp['role']
        for up in [up1[c['case_id']],up2[c['case_id']]]:assert up['independently_supplied_'+role+'14_7']['raw_config']['utf8_text'].encode('utf-8')==b
        od=inp['original_descriptor7'];nd=inp['prospective_descriptor7'];assert od==oldinp['original_descriptor7'];assert {k:v for k,v in od.items() if k!='expectedConfigPath'}=={k:v for k,v in nd.items() if k!='expectedConfigPath'}
        assert nd['expectedConfigPath']==inp['future_path'];assert Path(inp['future_path']).is_relative_to(Q/c['case_id']/'inputs')
        oldtoken=json.dumps(old['expected_aux4'][role+'Declaration']['expectedConfigPath'],ensure_ascii=False).encode('utf-8');newtoken=json.dumps(inp['future_path'],ensure_ascii=False).encode('utf-8');assert expected.count(oldtoken)==1;expected=expected.replace(oldtoken,newtoken)
        assert decoded['issuedAtUtc']==('2026-10-11T00:00:00.1234567Z' if role=='parent' else '2026-10-11T00:00:01.0000000Z')
    assert expected==literal(c['expected_bundle']) and json.loads(expected)==c['expected_aux4'];assert json.loads(literal(c['spec_literal']))==c['spec'];assert literal(c['expected_sha_sidecar'])==c['expected_bundle']['sha256'].encode('ascii')
    assert c['spec']['outputDir']==c['future_output_root'];assert Path(c['future_output_root'])==Q/c['case_id']/'publication';assert c['publication_calls_admitted']==1
    verification.append(dict(case_id=c['case_id'],raw12_original_match=True,expected_bundle_path_only_substitution_verified=True,expected_bundle_sha=c['expected_bundle']['sha256'],expected_bundle_bytes=c['expected_bundle']['bytes'],spec_sha=c['spec_literal']['sha256'],output_absent=True))
write(Q/'ORACLE_INDEPENDENT_PREFLIGHT_VERIFICATION.json',dict(at=now(),expected_oracle=row(EXPECTED),original_oracle=row(ORIGINAL),two_upstreams=uprows,cases=verification,candidate_observed_to_generate_expectations=False,fixture_files_written=0,candidate_calls=0))
inputs=[row(p) for p,h in PINS]+[row(ORIGINAL)]+check(uprows)+[row(Path(r['frozen_path'])) for r in load(MAN)['files']]
write(Q/'PASSIVE_INPUT_MANIFEST.json',dict(at=now(),files=inputs));before=preservation();write(Q/'PRESERVATION_BEFORE.json',before)
ack=dict(at=now(),delivery_id=DELIVERY,wp='WP_QA_ENGINE_GATE05_R38_PUBLISHER_NORMAL6',stage='S1',result_id='SOL-GATE05-R38-PUBLISHER-NORMAL6-S1-20261014-'+uuid.uuid4().hex,status='INITIAL_ACK_SCOPE_BOUND',candidate=row(S),admission=row(ADMIT),oracle=row(EXPECTED),baseline=row(BASE),freeze=row(MAN),initial_inventory=row(Q/'PRESERVATION_BEFORE.json'),scope='EXACT_ORIGINAL6_NORMAL_CLI_MAX6_NEW_QA_OWNED_ONLY',candidate_calls=0,fixtures_written=0,native_Engine_adverse=0,Master_disposition='PENDING',Foundation='HOLD')
write(Q/'ACK_INITIAL.json',ack);write(Q/'ACK.json',ack)
print(json.dumps(dict(status='BOOTSTRAP_AND_INDEPENDENT_ORACLE_VERIFIED',protected=19785,frozen=42,full_reads=len(texts),candidate_calls=0,fixtures_written=0,ACK=row(Q/'ACK_INITIAL.json'),raw12_child_utc='2026-10-11T00:00:01.0000000Z'),ensure_ascii=False))
