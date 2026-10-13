from common import *
import difflib,re
AUTH=PKG/'MASTER_R35_STATIC_PASSIVE_LOCATOR_R1_RESUME_AUTHORIZATION_20261013.md';PARTIAL=PKG/'coordination/MASTER_R35_STATIC_LOCATOR_STOP_PARTIAL_PRESERVATION_20261013.json'
assert sha(AUTH)=='EE4579C7E7587E1C142BA75CF1AF97482CF16BD5CCC4FFC7A85583263B890986';assert sha(PARTIAL)=='78B6FF784E48AE8AE73BD1B63C1E212C9A749587E1A672C0C24CE4686703DFEA'
print(AUTH.read_bytes().decode('utf-8-sig'));parts=check(load(PARTIAL)['files']);assert len(parts)==16
CENSUS=SOURCE.with_name('EngineHostCensus.cs');assert sha(CENSUS)=='391F9645A519CA86B69856B09A564F16B1DCEB5E9E6E92126827E18A069A2EB1'
docs=[]
for p in [SOURCE,CENSUS]:
    s=p.read_bytes().decode('utf-8-sig');lines=s.splitlines();matches=[]
    for i,line in enumerate(lines):
        if any(token in line for token in ['GetExpectedPackagePolicyRecord','ExpectedPackagePolicyDeclaration','ExpectedPackagePolicyRecord','SerializePackagePolicy','ComputePackagePolicyDigest','PackagePolicyService']):matches.append(dict(line=i+1,text=line,context='\n'.join(lines[max(0,i-4):i+9])))
    docs.append(dict(**row(p),raw_utf8=s,actual_symbol_matches=matches,PackagePolicyService='SOURCE_SYMBOL_NOT_FOUND' if 'PackagePolicyService' not in s else 'PRESENT'))
write(Q/'PASSIVE_R1_WHOLE_SOURCE_AND_SYMBOL_READ.json',dict(at=now(),files=docs,no_guessed_index_span=True,actual_rg_tool_transcript='Conversation command20ff63 explicit two paths actualexit0; this owned reader independently scans whole UTF8 source.',original_failure='Conversation df9195 complete actualtool exit1; no fabricated byte-complete stderr from excerpt',publisher_Engine_execution=0))
old=(Q/'log.py').read_bytes().decode('utf-8');new=(Q/'log_r1.py').read_bytes().decode('utf-8');(Q/'LOGGER_R1_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=str(Q/'log.py'),tofile=str(Q/'log_r1.py'))).encode('utf-8'))
write(Q/'PASSIVE_LOCATOR_R1_RECOVERY_DIFF.json',dict(at=now(),failed_locator="Guess PackagePolicyService class -> substring ValueError; complete original conversation df9195 preserved",new_discovery='Explicit rg actual symbols then wholefile UTF8 scanning; GetExpectedPackagePolicyDeclaration().ToRecord() -> ContentProfileProvider.ComputePackagePolicyDigest/SerializePackagePolicy',old_STOP=row(Q/'STOP_PASSIVE_LOCATOR_NOTICE.json'),new_reader=row(Path(__file__)),logger_diff=row(Q/'LOGGER_R1_EXACT_DIFF.txt'),same_result_id=load(Q/'ACK_INITIAL.json')['result_id'],candidate_source_or_oracle_changes=0,partial16_unchanged=True))
write(Q/'PASSIVE_R1_INPUT_MANIFEST.json',dict(at=now(),files=[row(AUTH),row(PARTIAL),row(CENSUS)],metadata_only=True))
ack=dict(at=now(),delivery_id=DELIVERY,result_id=load(Q/'ACK_INITIAL.json')['result_id'],resume='BOUNDED_PASSIVE_R1',status='ACKNOWLEDGED_MASTER_SAME_WP_RECOVERY',authorization=row(AUTH),partial_manifest=row(PARTIAL),partial_files=parts,source_reader=row(Path(__file__)),initial_ACK=row(Q/'ACK_INITIAL.json'),source_data=row(Q/'PASSIVE_R1_WHOLE_SOURCE_AND_SYMBOL_READ.json'),source_and_candidate_changes=0,execution_admission=False,publisher_Engine_compiler_fixture_native_adverse=0)
write(Q/'RESUME_R1_ACK.json',ack);print(json.dumps(dict(partial_preserved=16,same_result=ack['result_id'],ACK=row(Q/'RESUME_R1_ACK.json'),PackagePolicyService='SOURCE_SYMBOL_NOT_FOUND',real_policy_route='Snapshot.GetExpectedPackagePolicyDeclaration().ToRecord -> ContentProfileProvider.ComputePackagePolicyDigest',all_execution=0)))
