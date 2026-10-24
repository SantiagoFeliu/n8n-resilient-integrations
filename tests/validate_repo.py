import json, pathlib, re, sys
root = pathlib.Path(__file__).parents[1]
files = sorted((root/'workflows').glob('*.json'))
if len(files) < 2:
    raise ValueError('Expected at least two workflow JSON files')
for f in files:
    d=json.loads(f.read_text())
    names={n['name'] for n in d['nodes']}
    if d.get('active') is not False or not d.get('connections'):
        raise ValueError(f'{f.name}: workflow must be inactive and connected')
    for src, outputs in d['connections'].items():
        if src not in names:
            raise ValueError(f'{f.name}: unknown source node {src}')
        for branches in outputs.values():
            for branch in branches:
                for edge in branch:
                    if edge['node'] not in names:
                        raise ValueError(f"{f.name}: unknown target node {edge['node']}")
text='\n'.join(p.read_text(errors='ignore') for p in root.rglob('*') if p.is_file() and p.name != 'validate_repo.py' and '.git' not in p.parts)
for bad in ['sk-ant-', 'AIza', 'ghp_', 'BEGIN PRIVATE KEY', 'password=', 'secret=']:
    if bad.lower() in text.lower():
        raise ValueError(f'Potential secret marker: {bad}')
if 'example.com' not in (root/'README.md').read_text():
    raise ValueError('README must document synthetic endpoint')
print(f'PASS: {len(files)} workflow JSON files parsed; connections and public-safety markers checked')
