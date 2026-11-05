import zipfile, os

zip_path = r'D:\Atrator compactador residual\atrator-compactador-v0.3.zip'

with zipfile.ZipFile(zip_path, 'r') as zf:
    entries = zf.namelist()
    print(f'Zip status: {os.path.getsize(zip_path)} bytes, {len(entries)} files')
    print()
    # Key files
    key_patterns = ['STATUS.md', 'muta_package', 'python', 'rust', 'lean']
    for pattern in key_patterns:
        matches = [e for e in entries if pattern in e]
        print(f'  {pattern}: {len(matches)} entries')
    print()
    # Show muta_package modules
    muta = [e for e in entries if 'muta_package/muta' in e]
    print(f'MUTA package modules:')
    for m in sorted(muta):
        print(f'  - {m}')