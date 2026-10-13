import re,json
from pathlib import Path
import setup as f
p=f.R/'QA_EngineHost_Semantic_Authority_Gate_03.md';lines=p.read_text(encoding='utf-8').splitlines()
translations={
243:'ContentProfile은 A/B bundle의 `PROFILE-SETTLEMENT-B`이며 실제 ModsConfig SHA는 §2.3에 기록했다. C도 동일 실제 profile에서 `ChainInputC`를 등록했다. 전체 source/profile/seal/epoch/staged/final 정보는 independent-chain.json에 있다. A/B stage/promote 성공을 authority gate의 유효한 승격으로 인정하지 않는다. C는 승격 후 transport regression이며 필수 승격 전 validator를 대신하지 못한다. 기대 sealed hash는 QA harness가 다음 프로세스로 전달했으므로 외부 durable canonical authority source를 증명한 것도 아니다.',
249:'아래 G03 번호는 이 보고서 안의 finding 식별자다. 공식 QDL 번호를 임의로 만들지 않고 기존 QA-ENGINE-002/006에 연결한다.',
253:'- Severity: **Critical** — authority gate가 잘못된 persisted state를 approved outcome으로 공개한다.',
255:'- Reproduction / Expected / Actual: §7의 3건. sealed ResultManifest에 대한 exact staged bytes의 fresh semantic validation이 필요하지만 XML envelope와 잘못된 SHA capture만으로 승인됐다.',
257:'- Required fix: 승격 전에 exact staged SHA를 fresh engine validator에 전달하고, 기대값을 sealed ResultManifest에서 받아 실제 로드된 supported manifest와 완전히 비교한다. source/context/profile/generation/epoch/grant와 validation receipt를 결합하고 candidate/staged self-census를 기대 authority로 쓰지 않는다.',
263:'- Reproduction: §8. stage 미실행·wrong skill file·empty lastStagedSha 상태에서 승인됐다.',
264:'- Required fix: 성공한 stage-validation receipt를 필수로 요구하고 path/exactSHA/sealedResult/generation/epoch에 binding한다. RESULT_SEALED 또는 빈 SHA만으로 승격하지 않는다. caller가 지정한 path를 authority proof로 쓰지 않는다.',
270:'- Reproduction: unregistered/stale-labelled/foreign-labelled/blank grant 모두 seal됐다. READ_ONLY에서 step/seal이 가능했고 direct native skill change → arbitrary self-seal → approved가 재현됐다.',
271:'- Required fix: control-plane authorized grant registry/receipt에 AuthorityId·scope/context·generation·operation permission·execution/result lineage를 binding하고 unknown/stale/foreign grant를 거절한다. seal이 label 입력만으로 simulation outcome의 정당성을 선언해서는 안 된다.',
277:'- Reproduction: registry overwrite, 로드 이후 wrong source/profile 수락, wrong gen/map validation error 이후에도 STEP 허용. wrong map에서는 SEAL도 허용됐다.',
278:'- Required fix: loaded artifact provenance와 실제 profile/context를 immutable authority binding에 포함한다. authority 변경 및 모든 validation 실패 경로에서 readiness/seal/staging approval을 무효화하며 STEP/SEAL/PROMOTE에서도 current authority를 검사한다. 누락된 scope/store/base lineage를 directory명으로 대체하지 않고 unused expectedSourceSha alias의 의미를 통일한다.',
284:'- Reproduction: private epoch increment 이후에도 승인됐고 native protocol reseal epoch19→20에서 old stage가 승인됐다.',
285:'- Required fix: staged receipt에 resultEpoch와 sealed authority/result identity를 고정하고 current epoch/result와 완전히 일치해야 한다. reseal에서 old staging validation을 무효화한다. 동일 live hash가 다른 grant/epoch를 대체하지 못하게 한다.',
291:'- Observation: 63/97 unequal hash test에서 helper는 PASS였다. 다만 current gate는 전체 hash를 사용하므로 실제 stage는 거절됐다. JobDef만으로 active job ID/target을 검증하지 못한다.',
292:'- Required fix: 개선된 current gate를 유지하고 future fresh validator가 partial helper만을 equality predicate로 사용하지 않게 한다. supported graph와 unsupported job/controller fields를 명시하고 scope 확장을 이미 인증한 것으로 주장하지 않는다.',
294:'정상 replacement 성공/backup의 환경 제한은 별도의 evidence limitation이며 G03-01..05의 semantic/authority 결함을 대신하지 않는다.'}
for n,text in translations.items():
 assert re.search('[\u3040-\u30ff]',lines[n-1]),n
 lines[n-1]=text
s='\n'.join(lines)+'\n'
assert not re.search('[\u3040-\u30ff]',s)
assert not any(ord(x)<32 and x not in '\n\r\t' for x in s)
for target in re.findall(r'\]\(([^)]+)\)',s):assert Path(re.sub(r':\d+$','',target)).exists(),target
p.write_text(s,encoding='utf-8')
manifest={str(x):{'sha256':f.sha(x),'bytes':x.stat().st_size} for x in f.Q.rglob('*') if x.is_file() and x.name!='evidence_manifest.json' and '__pycache__' not in x.parts}
manifest[str(p)]={'sha256':f.sha(p),'bytes':p.stat().st_size}
f.write(f.Q/'Evidence/evidence_manifest.json',manifest)
print(json.dumps({'report':str(p),'sha':f.sha(p),'lines':len(lines),'evidenceFiles':len(manifest)}))
