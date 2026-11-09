#!/usr/bin/env python3
"""Compare every historical asset/tool blob with the immutable accepted milestone."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
ACCEPTED='e0e442295eaccfa5484aaa3a751bb926243e2e99'
def validate():
    entries=subprocess.check_output(['git','ls-tree','-rz',ACCEPTED,'--','assets','tools'],cwd=ROOT).split(b'\0')
    checked=[];errors=[]
    for entry in entries:
        if not entry:continue
        meta,name=entry.split(b'\t');mode,kind,expected=meta.split();name=name.decode();path=ROOT/name
        if kind!=b'blob':continue
        if not path.is_file():errors.append(name+' missing');continue
        data=path.read_bytes();actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=expected.decode():errors.append(name+' modified')
        checked.append({'path':name,'sha256':hashlib.sha256(data).hexdigest()})
    return {'accepted_commit':ACCEPTED,'historical_files_checked':len(checked),'pass':not errors,'errors':errors,'files':checked}
if __name__=='__main__':
    r=validate();print(json.dumps(r,indent=2));raise SystemExit(0 if r['pass'] else 1)
