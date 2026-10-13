from harness import *
write('scheduled-resume-time.json',{'utc_epoch':time.time()+30})
time.sleep(30)
write('scheduled-resume-result.json',control(cmd('SET_PROGRESSION',Token='QA_CONTROL_SURFACE_KEY_PRIVILEGED',CustomData='1')))
for i in range(30):
 write('render-native-'+str(i)+'.json',dict(utc=time.time(),client=send(31801,'SNAP'),worker=send(31800,'SNAP')));time.sleep(.25)
