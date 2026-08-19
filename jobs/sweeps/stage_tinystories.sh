set -e
T=/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/tinystories
DEST=/data1/salehkaleybars/metaopt/data/tinystories
mkdir -p $DEST

# Defect: DATA_CACHE_DIR is hard-coded to the authors' Compute Canada path, which does not
# exist here. Make it environment-overridable rather than swapping one hard-coded path
# for another.
python3 - "$T/tinystories.py" <<'PY'
import sys, re
p = sys.argv[1]; t = open(p).read()
if "TINYSTORIES_DATA" in t:
    print("tinystories.py already env-overridable"); raise SystemExit
old = re.search(r'^DATA_CACHE_DIR = ".*"$', t, re.M).group(0)
new = ('DATA_CACHE_DIR = os.environ.get("TINYSTORIES_DATA",\n'
       '    "/data1/salehkaleybars/metaopt/data/tinystories")  # was a hard-coded Compute Canada path')
t = t.replace(old, new, 1)
open(p, "w").write(t)
print("PATCHED:", old.split("=")[0].strip())
PY
grep -n 'DATA_CACHE_DIR =' $T/tinystories.py

cd $DEST
URL=https://huggingface.co/datasets/roneneldan/TinyStories/resolve/main/TinyStories_all_data.tar.gz
if [ -s TinyStories_all_data.tar.gz ]; then echo "archive already present"; else
  nohup curl -L -C - -o TinyStories_all_data.tar.gz "$URL" > $DEST/download.log 2>&1 &
  echo "DOWNLOAD_STARTED pid=$!"
fi
