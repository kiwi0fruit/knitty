import os.path as p
from knitty.api import knitty_preprosess

def test_pre_knitty():
    doc = p.join(p.dirname(__file__), 'doc')
    with open(doc + '.py', 'r', encoding='utf-8') as pyf:
        with open(doc + '.md', 'r', encoding='utf-8') as mdf:
            assert mdf.read() == knitty_preprosess(pyf.read(), 'py')
