import os, shutil

dir_path = r"c:\Users\user\Desktop\RimMulti\scratch\replace_test"
os.makedirs(dir_path, exist_ok=True)
src = os.path.join(dir_path, "source.txt")
dst = os.path.join(dir_path, "dest.txt")
bak = os.path.join(dir_path, "dest.txt.bak")

with open(dst, "w", encoding="utf-8") as f:
    f.write("OLD_DEST")
with open(src, "w", encoding="utf-8") as f:
    f.write("NEW_SOURCE")

# Normal replacement:
shutil.copy2(dst, bak)
shutil.copy2(src, dst)
os.remove(src)

with open(dst, "r", encoding="utf-8") as f:
    print("Dest Content:", f.read())
with open(bak, "r", encoding="utf-8") as f:
    print("Bak Content:", f.read())

# Locked destination test:
with open(src, "w", encoding="utf-8") as f:
    f.write("NEW_SOURCE_2")

# Hold exclusive lock on dst
f_lock = open(dst, "r+", encoding="utf-8")
try:
    shutil.copy2(dst, bak)
    shutil.copy2(src, dst)
    print("UNEXPECTED: Replace succeeded while locked")
except Exception as e:
    print("Lock caught correctly:", type(e).__name__, e)
finally:
    f_lock.close()

with open(dst, "r", encoding="utf-8") as f:
    print("Dest Content after locked attempt:", f.read())

shutil.rmtree(dir_path)
