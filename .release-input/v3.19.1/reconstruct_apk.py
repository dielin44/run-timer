"""Reconstruct the already signed release exactly; no signing secret is required."""
from pathlib import Path
import base64,gzip,hashlib,json,sys,zipfile
root=Path(__file__).resolve().parent
base=Path(sys.argv[1]).read_bytes()
patch=gzip.decompress(b''.join(p.read_bytes() for p in sorted((root/'delta-parts').glob('part*.bin'))))
recipe=json.loads(patch)
assert hashlib.sha256(base).hexdigest()==recipe['base_sha256'], 'Base release differs'
chunks=[]
for op in recipe['operations']:
 if op[0]==0:
  assert 0<=op[1]<=op[1]+op[2]<=len(base)
  chunks.append(base[op[1]:op[1]+op[2]])
 elif op[0]==1:chunks.append(base64.b64decode(op[1],validate=True))
 else:raise ValueError('Invalid delta operation')
result=b''.join(chunks)
assert len(result)==recipe['target_size']
assert hashlib.sha256(result).hexdigest()==recipe['target_sha256'], 'Release checksum mismatch'
target=Path(sys.argv[2]);target.write_bytes(result)
with zipfile.ZipFile(target) as z:assert z.testzip() is None
print(json.dumps({'file':target.name,'size_bytes':len(result),'sha256':recipe['target_sha256']}))
