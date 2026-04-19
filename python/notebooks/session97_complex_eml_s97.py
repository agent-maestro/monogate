import subprocess, sys
r = subprocess.run([sys.executable, "-X", "utf8", "python/experiments/complex_eml_s97.py"], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd="D:/monogate")
print(r.stdout[:3000])
if r.returncode != 0: print(r.stderr[:400])
