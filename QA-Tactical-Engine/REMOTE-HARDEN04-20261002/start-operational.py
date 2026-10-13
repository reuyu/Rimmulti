from harness import *
write('before-gui-client.json',send(31801,'SNAP'));write('before-gui-worker.json',send(31800,'SNAP'))
print(send(29901,'SET_REPLICATION 1')['response']);print(control(cmd('SET_PROGRESSION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',CustomData='1'))['parsed'])
