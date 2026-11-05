import zipfile, os

zip_path = r'D:\Atrator compactador residual\atrator-compactador-v0.3.zip'
work_dir = r'D:\Atrator compactador residual\_trabalho\atrator-compactador-v0.3'

# Files/dirs to exclude
exclude = {'__pycache__', '.pyc', '.git', '.lake', 'results', 'trace', 'MANIFEST.sha256',
           'atrator-compactador-v0.2.zip', 'atrator-compactador-v0.3.zip'}

# Remove old zip
if os.path.exists(zip_path):
    os.remove(zip_path)

# Create new zip
count = 0
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(work_dir):
        # Filter dirs - skip excluded
        dirs[:] = [d for d in dirs if d not in exclude and not d.startswith('.')]
        
        for file in files:
            # Skip excluded files and large C artifacts
            if file in exclude:
                continue
            if file.endswith(('.c', '.hash', '.ile')):
                continue
            
            full_path = os.path.join(root, file)
            arcname = os.path.relpath(full_path, work_dir)
            
            try:
                zf.write(full_path, arcname)
                count += 1
            except Exception as e:
                print(f'  Skipped: {arcname} ({e})')

print(f'Zip created: {zip_path} ({os.path.getsize(zip_path)} bytes)')
print(f'Files included: {count}')

# Verify key files
with zipfile.ZipFile(zip_path, 'r') as zf:
    entries = zf.namelist()
    print(f'\nSTATUS.md: {"STATUS.md" in entries}')
    print(f'muta_package: {"muta_package" in entries}')
    print(f'Total entries: {len(entries)}')