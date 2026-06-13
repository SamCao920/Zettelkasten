import os
import re

FOLDER = r"C:\Users\samca\OneDrive\Documents\Obsidian\Learning\.obsidian"
DRY_RUN = False

pattern = re.compile(r'^workspace.*\.json$')

files = [
    (os.path.getmtime(os.path.join(FOLDER, f)), os.path.join(FOLDER, f), f)
    for f in os.listdir(FOLDER)
    if pattern.match(f)
]

files.sort(reverse=True)  # newest first

print(f"Keeping:  {files[0][2]}")
for _, fpath, fname in files[1:]:
    print(f"  Delete: {fname}")
    if not DRY_RUN:
        os.remove(fpath)

print("Done.")