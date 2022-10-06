# analyze two files and print the differences

import difflib

with open('broker.py') as f1, open('test.py') as f2:
    diff = difflib.unified_diff(
        f1.readlines(),
        f2.readlines(),
        fromfile='broker.py',
        tofile='test.py',
    )
    print(''.join(diff))

    