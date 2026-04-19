import subprocess, sys
result = subprocess.run([sys.executable, 'python/monogate/frontiers/shimura_varieties_eml.py'], capture_output=True, text=True, encoding='utf-8', errors='replace', cwd='D:/monogate')
print(result.stdout[:3000])
if result.returncode != 0: print(result.stderr[:500])
