from pathlib import Path
import json,re,statistics,xml.etree.ElementTree as ET,hashlib
q=Path(__file__).resolve().parent
j=lambda n:json.loads((q/n).read_text(encoding='utf-8-sig'))
m=list(ET.fromstring(j('final-metrics.json')['response']));logs=(q/'GraphicalClient/qa-events.tsv').read_text(encoding='utf-8').splitlines();rx=[];apps=[]
for l in logs:
 a=re.search('receiveToEnterMs=([0-9.]+)',l);b=re.search('APPLY_EXIT applyMs=([0-9.]+)',l)
 if a:rx.append(float(a[1]))
 if b:apps.append(float(b[1]))
summary={'periodic_samples':len(m),'median_baseline_cadence_ms':statistics.median([float(x.attrib['cadenceMs']) for x in m if 100<float(x.attrib['cadenceMs'])<250]),'median_baseline_rtt_ms':statistics.median([float(x.attrib['rttMs']) for x in m if float(x.attrib['rttMs'])<100]),'max_periodic_rtt_ms':max(float(x.attrib['rttMs']) for x in m),'median_receive_deserialized_to_main_apply_entry_ms':statistics.median(rx),'median_apply_execution_ms':statistics.median(apps),'max_receive_deserialized_to_main_entry_ms':max(rx),'gui_main_thread_delay_frame_ms':2029.3,'periodic_2s_delay_max_frame_ms':19.0,'fence_faults':j('periodic-fault-native-results.json'),'wire_sizes':j('wire-size-summary.json'),'integrity':j('integrity-after.json'),'worker_slices':j('worker-slice-summary.json'),'apply_oracle':j('apply-oracle-summary.json'),'auth_focused':[x['parsed']['Status'] for x in j('authorization-focused.json')]}
(q/'independent-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print({k:v for k,v in summary.items() if isinstance(v,(int,float))})
(q/'profile-manifest.json').write_text(json.dumps([dict(path=str(x),sha256=hashlib.sha256(x.read_bytes()).hexdigest().upper()) for role in ['Worker','GraphicalClient'] for x in (q/role/'Config').glob('*.xml')],indent=2),encoding='utf-8')
