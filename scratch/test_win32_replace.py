import os, ctypes
from ctypes import wintypes

dir_path = r"c:\Users\user\Desktop\RimMulti\scratch\replace_test_win32"
os.makedirs(dir_path, exist_ok=True)
src = os.path.join(dir_path, "src.rws")
dst = os.path.join(dir_path, "dst.rws")
bak = os.path.join(dir_path, "dst.rws.bak")

with open(dst, "w", encoding="utf-8") as f:
    f.write("ORIGINAL")
with open(src, "w", encoding="utf-8") as f:
    f.write("NEW")

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
ReplaceFileW = kernel32.ReplaceFileW
ReplaceFileW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD, wintypes.LPVOID, wintypes.LPVOID]
ReplaceFileW.restype = wintypes.BOOL

res = ReplaceFileW(dst, src, bak, 0, None, None)
err = ctypes.get_last_error()
print(f"ReplaceFileW result: {res}, last error: {err}")

# Now test on Saves directory!
saves_dir = os.path.expandvars(r"%USERPROFILE%\AppData\LocalLow\Ludeon Studios\RimWorld by Ludeon Studios\Saves")
src2 = os.path.join(saves_dir, "test_src.rws")
dst2 = os.path.join(saves_dir, "test_dst.rws")
bak2 = os.path.join(saves_dir, "test_dst.rws.bak")

with open(dst2, "w", encoding="utf-8") as f:
    f.write("ORIGINAL_SAVE")
with open(src2, "w", encoding="utf-8") as f:
    f.write("NEW_SAVE")

res2 = ReplaceFileW(dst2, src2, bak2, 0, None, None)
err2 = ctypes.get_last_error()
print(f"ReplaceFileW on Saves directory: {res2}, last error: {err2}")

for p in [src, dst, bak, src2, dst2, bak2]:
    if os.path.exists(p):
        os.remove(p)
os.rmdir(dir_path)
