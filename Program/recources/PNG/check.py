import os

out_dir = 'sprites'
if os.access(out_dir, os.W_OK):
    print(f"You have write permission for folder: {out_dir}")
else:
    print(f"NO write permission for folder: {out_dir}")