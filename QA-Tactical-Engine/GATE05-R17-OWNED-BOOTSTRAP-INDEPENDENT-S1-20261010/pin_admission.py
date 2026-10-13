from review_setup import *
import re
if __name__=='__main__':
    assert not (Q/'runner/QaPureRunner.exe').exists()
    clarification=PKG/'MASTER_R17_QA_HOST_LAUNCHER_TELEMETRY_SCOPE_CLARIFICATION_20261010.md';assert sha(clarification)=='B35BF9836E70B162571730D301CF2452F7E01F080568F80C69D0FD47414BAB59'
    program=(Q/'Program.cs').read_text(encoding='utf-8-sig');assert not re.search(r'\bProcess\s*\.|GetCurrentProcess\s*\(|MainModule|VerifyProcessIdentity\s*\(|DllImport|WorkerBridgeComponent\s*\.|WorkerBridgeBootstrapper\s*\.',program)
    oracle=load(Q/'INPUT_EXPECTED_SEMANTICS.json');assert all(len(c['expected_snapshot'])==14 and len(c['expected_redacted'])==13 for c in oracle['config_cases'].values()) and all(len(c['expected_redacted'])==25 for c in oracle['validator_results'].values())
    admission=dict(at=now(),WP=row(PKG/'WP_QA_ENGINE_GATE05_R17_OWNED_BOOTSTRAP_INDEPENDENT_S1.md'),host_telemetry_clarification=row(clarification),same_WP_ACK_unchanged=True,source=row(Q/'Program.cs'),oracle=row(Q/'INPUT_EXPECTED_SEMANTICS.json'),new_runner_build_execute_scope='PUREpositiveonly;externalhostownsQAchildPID+numericexit;allCSharp/candidateProcessidentityqueries0',host_game_Worker_validator_native_producer_oldrunner_launches=0,fulltyped_snapshot14_redacted13_result25=True,normal_source_config_only_edits_no_protectedglobal_or_nestedgetter_edits=True,prebuild_candidate_calls=0)
    write(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json',admission)
    d=load(Q/'ORACLE_BEFORE_BUILD.json');d['host_scope_clarification']=row(clarification);d['execution_admission']=row(Q/'EXECUTION_ADMISSION_BEFORE_BUILD.json');write(Q/'ORACLE_BEFORE_BUILD.json',d)
    print('Actualhost scope sidecar pinned beforebuild/candidatecalls;fulltypedprospectiveoracle checked')
