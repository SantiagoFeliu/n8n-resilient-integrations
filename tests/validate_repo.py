import json, pathlib, re, sys
root = pathlib.Path(__file__).parents[1]
files = sorted((root/'workflows').glob('*.json'))
assert len(files) >= 2
for f in files:
    d=json.loads(f.read_text())
    names={n['name'] for n in d['nodes']}
    assert d['active'] is False and d['connections']
    for src, outputs in d['connections'].items():
        assert src in names
        for branches in outputs.values():
            for branch in branches:
                for edge in branch:
                    assert edge['node'] in names
text='\n'.join(p.read_text(errors='ignore') for p in root.rglob('*') if p.is_file() and p.name != 'validate_repo.py' and '.git' not in p.parts)
for bad in ['sk-ant-', 'AIza', 'ghp_', 'BEGIN PRIVATE KEY', 'password=', 'secret=']:
    assert bad.lower() not in text.lower(), bad
assert 'example.com' in (root/'README.md').read_text()
print(f'PASS: {len(files)} workflow JSON files parsed; connections and public-safety markers checked')
