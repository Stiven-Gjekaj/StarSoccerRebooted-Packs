#!/usr/bin/env python3
# Checks index.txt, the list of the data packs of Star Soccer Rebooted.
# Usage: tools/check_index.py [index file]
# For each row it downloads the zip file of the pack and checks:
#   - the id: 1 to 47 small letters, digits, "-", and "_", one row only;
#   - the url: https only;
#   - the size and the SHA-256 of the zip file;
#   - pack.txt in the zip: the same id, version, and format;
#   - the files: only .txt, .png, .jpg, .uis, .uih, and .patch, each of
#     16 MB or less, and no name that goes out of the pack.
# It prints each fault and exits with 1 when there is a fault.
import hashlib, io, re, sys, urllib.request, zipfile

COLUMNS = ['id', 'name', 'author', 'version', 'format', 'size', 'sha256', 'url']
KINDS = ('.txt', '.png', '.jpg', '.uis', '.uih', '.patch')
MAX_FILE = 16 * 1024 * 1024
MAX_FORMAT = 1


def pack_info(text):
    info = {}
    for line in text.splitlines():
        if '=' in line:
            key, value = line.split('=', 1)
            info[key.strip()] = value.strip()
    return info


def check_zip(row, data, faults):
    pid = row['id']
    try:
        archive = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        faults.append(f'{pid}: the file is not a zip file')
        return
    names = [n for n in archive.namelist() if not n.endswith('/')]
    tops = [n for n in names if n.split('/')[-1] == 'pack.txt' and n.count('/') <= 1]
    if not tops:
        faults.append(f'{pid}: the zip file has no pack.txt')
        return
    for item in archive.infolist():
        name = item.filename
        if name.endswith('/'):
            continue
        if name.startswith('/') or '..' in name.split('/') or '\\' in name:
            faults.append(f'{pid}: the name {name} goes out of the pack')
        if not name.lower().endswith(KINDS):
            faults.append(f'{pid}: the kind of {name} is not a data kind')
        if item.file_size > MAX_FILE:
            faults.append(f'{pid}: {name} is more than 16 MB')
    info = pack_info(archive.read(tops[0]).decode('utf-8', 'replace'))
    for key in ('id', 'version', 'format'):
        if info.get(key, '') != row[key]:
            faults.append(f'{pid}: pack.txt has {key}={info.get(key, "")}, the index has {row[key]}')


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else 'index.txt'
    lines = [l for l in open(path, encoding='utf-8').read().splitlines() if l.strip()]
    faults = []
    if not lines or lines[0].split('\t') != COLUMNS:
        print('index.txt: the first row must be the names of the columns: ' + ' '.join(COLUMNS))
        return 1
    seen = set()
    for number, line in enumerate(lines[1:], start=2):
        cells = line.split('\t')
        if len(cells) != len(COLUMNS):
            faults.append(f'row {number}: {len(cells)} cells, not {len(COLUMNS)}')
            continue
        row = dict(zip(COLUMNS, cells))
        pid = row['id']
        if not re.fullmatch(r'[a-z0-9_-]{1,47}', pid):
            faults.append(f'row {number}: the id {pid} is not correct')
        if pid in seen:
            faults.append(f'row {number}: the id {pid} is there two times')
        seen.add(pid)
        if not row['format'].isdigit() or int(row['format']) > MAX_FORMAT:
            faults.append(f'{pid}: the format {row["format"]} is not one that the app reads')
        if not row['url'].startswith('https://'):
            faults.append(f'{pid}: the url must start with https://')
            continue
        if not re.fullmatch(r'[0-9a-f]{64}', row['sha256']):
            faults.append(f'{pid}: the sha256 must be 64 small hex digits')
        try:
            with urllib.request.urlopen(row['url'], timeout=60) as response:
                data = response.read()
        except Exception as error:
            faults.append(f'{pid}: the download failed: {error}')
            continue
        if str(len(data)) != row['size']:
            faults.append(f'{pid}: the size is {len(data)}, the index has {row["size"]}')
        if hashlib.sha256(data).hexdigest() != row['sha256']:
            faults.append(f'{pid}: the SHA-256 of the download is not the SHA-256 of the index')
        check_zip(row, data, faults)
    for fault in faults:
        print(fault)
    print(f'{len(lines) - 1} packs, {len(faults)} faults')
    return 1 if faults else 0


if __name__ == '__main__':
    sys.exit(main())
