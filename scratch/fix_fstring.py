with open(r'C:\Users\user\Desktop\RimMulti\scratch\generate_runner.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("'{expectedChildDesc.expectedRole}'", "'{{expectedChildDesc.expectedRole}}'")
text = text.replace("'{desc.expectedRole}'", "'{{desc.expectedRole}}'")
text = text.replace("'{expectedChildDesc.expectedCapabilityBoundary}'", "'{{expectedChildDesc.expectedCapabilityBoundary}}'")
text = text.replace("'{desc.expectedCapabilityBoundary}'", "'{{desc.expectedCapabilityBoundary}}'")
text = text.replace("'{optVals[5]}'", "'{{optVals[5]}}'")
text = text.replace("'{optVals[6]}'", "'{{optVals[6]}}'")

with open(r'C:\Users\user\Desktop\RimMulti\scratch\generate_runner.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('fix_fstring executed successfully.')
