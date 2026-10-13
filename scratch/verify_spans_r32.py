import hashlib

with open(r'scratch\apply_r32_patch.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract chunks using split
c1_str = content.split('chunk1_text = """')[1].split('"""')[0]
c2_str = content.split('chunk2_text = """')[1].split('"""')[0]
c3_str = content.split('chunk3_text = """')[1].split('"""')[0]
c4_str = content.split('chunk4_text = """')[1].split('"""')[0]

c1 = c1_str.encode('utf-8')
c2 = c2_str.encode('utf-8')
c3 = c3_str.encode('utf-8')
c4 = c4_str.encode('utf-8')

st1 = 27259
en1 = st1 + len(c1)

s1_len = 38131 - 33326
st2 = en1 + s1_len
en2 = st2 + len(c2)

s2_len = 41273 - 39339
st3 = en2 + s2_len
en3 = st3 + len(c3)

s3_len = 185129 - 42068
st4 = en3 + s3_len
en4 = st4 + len(c4)

s4_len = 272607 - 185705
final_len = en4 + s4_len

with open(r'scratch\WorkerBridgeMod\Source\WorkerBridge.cs', 'rb') as f:
    patched = f.read()

assert final_len == len(patched)
assert patched[st1:en1] == c1
assert patched[st2:en2] == c2
assert patched[st3:en3] == c3
assert patched[st4:en4] == c4

print(f"Span 1: [{st1}, {en1}], len={len(c1)}, sha={hashlib.sha256(c1).hexdigest().upper()}")
print(f"Span 2: [{st2}, {en2}], len={len(c2)}, sha={hashlib.sha256(c2).hexdigest().upper()}")
print(f"Span 3: [{st3}, {en3}], len={len(c3)}, sha={hashlib.sha256(c3).hexdigest().upper()}")
print(f"Span 4: [{st4}, {en4}], len={len(c4)}, sha={hashlib.sha256(c4).hexdigest().upper()}")
print("Total outside bytes:", 27259 + s1_len + s2_len + s3_len + s4_len)
print("File length:", len(patched), "SHA:", hashlib.sha256(patched).hexdigest().upper())
