from review_setup import *
import copy,json
if __name__=='__main__':
    old=ROOT/'QA-Tactical-Engine/GATE05-R25-ROLE_USERDATA-INDEPENDENT-S1-20261011';assert not (Q/'NORMAL_EXPECTED_ORACLE.json').exists()
    original=load(old/'NORMAL_EXPECTED_ORACLE.json');o=copy.deepcopy(original);diff=[]
    for n,c in o['cases'].items():
        independent=json.dumps(c['expected_redacted'],ensure_ascii=False,indent=2);assert independent==original['cases'][n]['expected_redacted_utf8_text']
        newtext=independent.replace('\n','\r\n');c['expected_redacted_utf8_text']=newtext;assert json.loads(newtext)==c['expected_redacted']
        a=copy.deepcopy(original['cases'][n]);b=copy.deepcopy(c);a.pop('expected_redacted_utf8_text');b.pop('expected_redacted_utf8_text');assert a==b and list(a)==list(b)
        diff.append(dict(case_id=n,only_changed_field='expected_redacted_utf8_text',S1_LF_SHA256=hashlib.sha256(independent.encode()).hexdigest().upper(),S2_CRLF_SHA256=hashlib.sha256(newtext.encode()).hexdigest().upper(),S1_bytes=len(independent.encode()),S2_bytes=len(newtext.encode()),formatting_newlines=independent.count('\n'),all_other_values_types_keyorder_originalstrings_identical=True,expected_from_prospective_graph_not_actual_output=True))
    # Preserve descriptiveattoo;only changedfourprettytext fields, no actualoutputread.
    write(Q/'NORMAL_EXPECTED_ORACLE.json',o);assert (Q/'Program.cs').read_bytes()==(old/'Program.cs').read_bytes() and sha(Q/'Program.cs')=='6614E455D316F046BC9072171B4A39F676148E61395AEF889C2E95974E6A615C'
    write(Q/'S1_PROGRAM_EXACT_COPY.json',dict(original=row(old/'Program.cs'),new=row(Q/'Program.cs'),exactbytes=True,newinputfromargs=True,no_runner_logic_or_assertionchanges=True))
    write(Q/'ORACLE_FIELD_DIFF_BEFORE_BUILD.json',dict(at=now(),S1_original_oracle=row(old/'NORMAL_EXPECTED_ORACLE.json'),S2_oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),changed_leaf_paths=[f'cases.{n}.expected_redacted_utf8_text' for n in o['cases']],rows=diff,no_other_input_or_typed_graph_literal_root_changes=True,S1_original_bytes_unchanged=True,actual_output_read_or_normalized=False,candidate_calls=0,qa_builds=0))
    cfg=load(old/'QA_RUNNER_CONFIG.json');write(Q/'QA_RUNNER_CONFIG.json',cfg)
    fw=Path(r'C:\Program Files (x86)\Reference Assemblies\Microsoft\Framework\.NETFramework\v4.7.2');candidate=Path(cfg['selected']['path']);newton=Path(cfg['allowed_managed'][1]['path']);args=['-noconfig','-nostdlib+','-target:exe','-langversion:latest','-nullable:enable','-deterministic+','-debug:portable','-out:"'+str(Q/'runner/QaPureRunner.exe')+'"','-pdb:"'+str(Q/'runner/QaPureRunner.pdb')+'"']+['-r:"'+str(p)+'"' for p in [fw/'mscorlib.dll',fw/'System.dll',fw/'System.Core.dll',candidate,newton]]+['"'+str(Q/'Program.cs')+'"'];(Q/'build.rsp').write_text('\n'.join(args)+'\n',encoding='utf-8')
    allocations=[]
    for stage,culture in [(1,'en-US'),(2,'de-DE')]:
        rid='R25S2-'+uuid.uuid4().hex[:16];out=Q/'runs'/rid;out.mkdir(parents=True);allocations.append(dict(stage=stage,run_id=rid,culture=culture,output_root=str(out)))
    write(Q/'RUN_ALLOCATION_PLAN.json',dict(allocations=allocations));write(Q/'ORACLE_BEFORE_BUILD.json',dict(source=row(Q/'Program.cs'),oracle=row(Q/'NORMAL_EXPECTED_ORACLE.json'),explicit_calls=dict(ToSnapshot=4,SelectUserData=8),candidate_calls=0,builds=0,source_exactS1_bytes=True,onlypreapprovedWindowsformattingCRLFcorrection=True,actual_byteassertions_unchanged=True))
    print('S2 prospectivefourtextCRLF correctionfromorderedexpected13 only;allinputsgraphsroots/S1source exact unchanged beforeonlybuild/calls')
