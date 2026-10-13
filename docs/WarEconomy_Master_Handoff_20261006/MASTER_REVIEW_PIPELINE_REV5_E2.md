# Master Review — Pipeline REV5 E2
Source: source_reports/QA_Production_Transaction_Pipeline_01_REV5.md
Master verdict: FAIL — TARGETED REV6 REQUIRED.

## Accepted independent progress
Five prior typed input errors now INVALID_REQUEST/durable rows 0.
Natural mixed COMMITTED/ABORTED restart and principal-scoped identities recover.
Actual writer/final Shutdown/Dispose/Main and UNKNOWN query/retry pass tested scope.
Concurrency/CAS/idempotency, hard-kill/terminal/incarnation/WAL regressions retained.
Current exact REV5 release manifest exists and entries match.

## Blockers
Plausible historical observed-revision rewrite reaches READY/LISTEN.
ABORTED status/reason/FailureReason/required typed-key omissions pass.
COMMITTED audit event/parent/scope/revision fields are incompletely checked.
Current V6 descriptor ignores identity collation, merging case-distinct keys.

## Expected report-verified provenance
Server DLL SHA: 1143AE62FD74F0C93F0504B48C1501D5153F40C2E903BD4D69BA9BE1E6983479
Server MVID: a5cba4c3-1e2f-4a19-a35c-0241ccf12e81
Common DLL SHA: 2711A366D3108DE42EB5CD07EE4874DB6B332B86A63F38B36E79611CFE110BCB
Manifest: RELEASE_MANIFEST_PIPELINE_REV5.json
Manifest SHA: D609795D8B50ED98850B8C73E951EA7F8E9B21B6193E815CF4890B9E2BB7D9E6
V6 signature: 64BDB62037D70303D7F2AE15D39FC7E7DFD9F01021B5E0AA0709A51FA507E721

These are expected values from report, not current local inspection by migration Master.

## Documentation
A sample DDL differs from frozen DDL. Actual report: history PK=(ProbeScopeId,ProbeRevision); audit PK=AuditId; composite principal/op FKs.
E1 named OS-process/hard-kill/package batteries do not all execute claimed categories. Correct actual coverage in REV6.
001/013 narrow CLOSED. 007/current schema OPEN. Foundation HOLD.
