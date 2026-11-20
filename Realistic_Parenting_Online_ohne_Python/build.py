"""Build Realistic Parenting .ts4script with Python 3.7 only."""
import os
import sys
import py_compile
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SOURCES = ['rp_core.py', 'realistic_parenting.py']
OUTPUT = os.path.join(ROOT, 'RealisticParenting_v0_1_1.ts4script')

if sys.version_info[:2] != (3, 7):
    print('FEHLER: Python 3.7 erforderlich. Gefunden: {}'.format(sys.version))
    sys.exit(1)

with tempfile.TemporaryDirectory() as temp:
    with zipfile.ZipFile(OUTPUT, 'w', zipfile.ZIP_DEFLATED) as archive:
        for filename in SOURCES:
            source = os.path.join(ROOT, 'source', filename)
            compiled = os.path.join(temp, filename + 'c')
            py_compile.compile(source, cfile=compiled, doraise=True)
            archive.write(compiled, filename + 'c')
with zipfile.ZipFile(OUTPUT, 'r') as archive:
    assert archive.namelist() == ['rp_core.pyc', 'realistic_parenting.pyc']
print('FERTIG: ' + OUTPUT)
print('Kopiere diese Datei in den Mods-Ordner. Alte v0_1 entfernen.')
