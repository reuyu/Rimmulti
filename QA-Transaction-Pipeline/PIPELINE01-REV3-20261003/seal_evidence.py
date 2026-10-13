import setup as f
import json
Q=f.Q;R=f.R
before=json.loads((Q/'freeze-before.json').read_text(encoding='utf-8'));after=f.tree();changes=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
assert not changes,changes
f.write(Q/'freeze-after.json',after)
expected={
'Pipeline/Models/PipelineProbeModels.cs':'E4D0A914EDB7712A1F8ED4A4E0BB2BD1751DCDF523B11F2799FC60DA574DABB3',
'Pipeline/Data/SqliteDatabaseContext.cs':'AD83A9747ADE1D078B2D672EFDDF34E60F5B5A902DD672BF567500215977B903',
'Pipeline/Data/Migrations/PipelineSchemaMigration.cs':'3F05A85A4E9EA0F2A41C2A32A12C76666E56FDA83E33039CC2F9724F48D1E06C',
'Pipeline/Storage/ProbeAggregateStore.cs':'45D9B256A1E6ADF46BA2077D8D35148BC81E5F402FAF448A08DA665DFF661B86',
'Pipeline/Coordinator/PipelineTransactionCoordinator.cs':'1CD4FBFDDBE6FDCE33E6CF546FD8A38228F51399E4289C9B7832CC8BE5FCB1E7',
'Pipeline/Recovery/RecoveryReconciler.cs':'89993EB4D6431615CD02056078C0790AE1ACB0803CF824326D68FC0376D3ED4E'}
sources=[]
for name,expectedSha in expected.items():
 p=f.PROD/'Source/Server'/name;actual=f.sha(p);assert actual==expectedSha;assert f.sha(Q/'FrozenSource/Server'/name)==actual;sources.append({'path':str(p),'sha256':actual})
for n in ['Production_Transaction_Pipeline_Slice_01_REV3.md','RELEASE_MANIFEST_PIPELINE_REV3.json','scratch/pipeline_e1_rev3_results.json']:
 assert f.sha(R/n)==f.sha(Q/'FrozenSource'/n)
d=json.loads((Q/'Evidence/results.json').read_text(encoding='utf-8'))
assert d['metadata-final']['rows'][-1]['sha']=='8F140D23F8D1BD90A00F3F5B9000C1E01EA0D3CD5AB0615A967635E7668F0209'
assert d['fingerprint-complete']['rows'][-1]['status']=='FINGERPRINTS'
assert d['cas-summary']['outcomes']=={'SUCCESS':1,'STALE_REVISION':24}
assert d['same-id-summary']['outcomes']=={'SUCCESS':1,'ALREADY_COMMITTED':11}
assert d['terminal-native-truth']['unchanged']
assert all(x['match'] for x in d['release-provenance']['files'])
assert not d['release-provenance']['residues']
manifest={'ProductionFreeze':{'count':len(after),'changes':changes},'Sources':sources,'EvidenceFiles':{str(p.relative_to(Q)):{'sha256':f.sha(p),'bytes':p.stat().st_size} for p in sorted(Q.rglob('*')) if p.is_file() and p.name!='qa-evidence-manifest.json' and 'obj' not in p.parts},'Report':{'path':str(R/'QA_Production_Transaction_Pipeline_01_REV3.md'),'sha256':f.sha(R/'QA_Production_Transaction_Pipeline_01_REV3.md')}}
f.write(Q/'qa-evidence-manifest.json',manifest)
print('Sealed:',len(after),'unchanged Production files;',len(manifest['EvidenceFiles']),'QA evidence files;',len(d),'result entries; report',manifest['Report']['sha256'])
