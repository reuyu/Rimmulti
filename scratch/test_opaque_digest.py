import hashlib

s = '{"schemaVersion":"WE-PACKAGE-POLICY-V1","policyId":"  qa.R18 정책 Ω  ","revision":"  007 café Ω  ","admittedPackageIds":["ludeon.rimworld","example.qa.normal"]}'
h = hashlib.sha256(s.encode('utf-8')).hexdigest().upper()
print('Calculated:', h)
print('Expected:  ', '8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF')
print('Matches:   ', h == '8A9C3381A041F79F300710D6EA93A5D8E08564C692AA5059337853825E1749BF')

# If trimmed:
s_trim = '{"schemaVersion":"WE-PACKAGE-POLICY-V1","policyId":"qa.R18 정책 Ω","revision":"007 café Ω","admittedPackageIds":["ludeon.rimworld","example.qa.normal"]}'
h_trim = hashlib.sha256(s_trim.encode('utf-8')).hexdigest().upper()
print('Trimmed:   ', h_trim)
print('Expected Trimmed: 68E6181212BE28EB928FBBB6AE79FD6D0CACFA91DEBF0F7E6D0B89BAB9EB3983')
print('Matches Trimmed:', h_trim == '68E6181212BE28EB928FBBB6AE79FD6D0CACFA91DEBF0F7E6D0B89BAB9EB3983')
