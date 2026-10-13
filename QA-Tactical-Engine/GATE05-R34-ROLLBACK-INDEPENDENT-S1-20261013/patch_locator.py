from common import *
import difflib,sys,traceback
out=Q/'PATCH_LOCATOR.STDOUT.txt';err=Q/'PATCH_LOCATOR.STDERR.txt';assert not out.exists() and not err.exists();code=0
with out.open('w',encoding='utf-8') as o,err.open('w',encoding='utf-8') as e:
    try:
        a=(Q/'static.py').read_bytes().decode('utf-8');b=a.replace("n.index('            catch (Exception ex)\\n')","n.index('\\n            catch (Exception ex)\\n')")
        assert b!=a and a.count("n.index('            catch (Exception ex)\\n')")==2
        b=b.replace('SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON.json','SOURCE_WHOLE_AWAKE_OUTSIDE_COMPARISON_R1.json')
        b=b.replace("if r['original_path'].lower().endswith('.py')","if r['original_path'].lower().endswith('.py') and 'enginegate05r34rollback-a4d6866c' in r['original_path'].lower()")
        (Q/'static_r1.py').write_bytes(b.encode('utf-8'));(Q/'STATIC_R1_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='static.py',tofile='static_r1.py')).encode('utf-8'))
        la=(Q/'log.py').read_text(encoding='utf-8');lb=la.replace("'static.py',","'static.py','static_r1.py',");assert lb!=la;(Q/'log_r1.py').write_bytes(lb.encode('utf-8'));(Q/'LOGGER_R1_EXACT_DIFF.txt').write_bytes(''.join(difflib.unified_diff(la.splitlines(True),lb.splitlines(True),fromfile='log.py',tofile='log_r1.py')).encode('utf-8'))
        write(Q/'STATIC_R1_LOCATOR_CORRECTION.json',dict(at=now(),original=row(Q/'static.py'),failed_tool=row(Q/'static.TOOL.json'),failed_stdout=row(Q/'static.STDOUT.txt'),failed_stderr=row(Q/'static.STDERR.txt'),new=row(Q/'static_r1.py'),diff=row(Q/'STATIC_R1_EXACT_DIFF.txt'),logger_diff=row(Q/'LOGGER_R1_EXACT_DIFF.txt'),reason='Anchor needs newline to select twelve-space outer catch rather than sixteen-space earlier owner catch; owned helper manifest filter excludes fixed publisher .py outside ownedroot. Additive witness name only.',candidate_oracle_changes=0,original_bytes_preserved=True))
        o.write('New unique outer-catch locator + owned-root helper filter; failed original/first witness unchanged; candidate executions0.\n')
    except BaseException:code=1;traceback.print_exc(file=e)
write(Q/'PATCH_LOCATOR.TOOL.json',dict(script=row(Path(__file__)),exit_code=code,stdout=row(out),stderr=row(err),first_streams_complete=True))
print(json.dumps(dict(exit_code=code,stdout=row(out),stderr=row(err))));sys.exit(code)
