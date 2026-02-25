from pathlib import Path
p = Path('uploads')
files = [f for f in p.iterdir() if f.name.endswith('test_img.png')]
print('found', len(files), 'files')
for f in files:
    b = f.read_bytes()
    print('file', f.name)
    print('size', len(b))
    print('first16', b[:16])
    print('last16', b[-16:])
