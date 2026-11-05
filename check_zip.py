import zipfile

zip_path = r'D:\Atrator compactador residual\atrator-compactador-v0.3.zip'

with zipfile.ZipFile(zip_path, 'r') as zf:
    entries = zf.namelist()
    # Check for muta_package entries
    muta_entries = [e for e in entries if 'muta_package' in e]
    print(f'Entries with muta_package: {len(muta_entries)}')
    for e in muta_entries[:5]:
        print(f'  - {e}')