import calc_supply
from pathlib import Path
print('OUTPUTS_DIR que setea calc_supply:', str(Path(calc_supply.__file__).parent))
# Ver cómo se arma el ZIP — de dónde toma el HTML
import inspect
src = inspect.getsource(calc_supply)
import re
for m in re.finditer(r'reports.week|SUPPLY.*html|shutil|copy|zip', src):
    i = m.start()
    ls = src.rfind(chr(10),0,i)+1
    le = src.find(chr(10),i)
    print(repr(src[ls:le].strip()))
