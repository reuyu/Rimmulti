from harness import *
time.sleep(5)
write('capture-resume.json',control(cmd('SET_PROGRESSION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',CustomData='1')))
for i in range(22):
 write('capture-native-'+str(i)+'.json',dict(utc=time.time(),client=send(31801,'SNAP'),worker=send(31800,'SNAP')));time.sleep(.4)
