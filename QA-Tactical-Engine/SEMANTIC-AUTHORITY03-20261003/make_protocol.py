from pathlib import Path
Q=Path(__file__).resolve().parent;R=Q.parent.parent
s=(R/'QA-Tactical-Engine/SEMANTIC-GATE02-20261003/run_qa.py').read_text(encoding='utf-8').split('def main():')[0]
s=s.replace('QA.SemanticGate.Observer.dll','QA.SemanticAuthority.Observer.dll').replace('sgqaport','agqaport').replace('33200+index','34200+index').replace('33300+index','34300+index').replace('33400+index','34400+index')
s=s.replace('shutil.copy2(Q/\'Frozen/Developer-A/Config/ModsConfig.xml\',self.profile/\'Config/ModsConfig.xml\')','shutil.copy2(Q/\'Frozen/Developer-A/Config/ModsConfig.xml\',self.profile/\'Config/ModsConfig.xml\')')
(Q/'protocol.py').write_text(s,encoding='utf-8')
