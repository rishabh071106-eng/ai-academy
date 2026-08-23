"""Render every formula referenced in the content modules; report any mathtext failures."""
import re, sys, importlib
import mathsvg

bad = []
for mod in sys.argv[1:]:
    src = open(mod + '.py').read()
    for m in re.finditer(r'\b(?:M|E)\(\s*r"((?:[^"\\]|\\.)*)"', src):
        tex = m.group(1)
        try:
            mathsvg._svg(tex, 17)
        except Exception as e:
            bad.append((mod, tex, str(e).strip().split('\n')[-1][:110]))
for mod, tex, err in bad:
    print(f'FAIL [{mod}] {tex[:70]}\n     {err}')
print('formulas checked, failures:', len(bad))
