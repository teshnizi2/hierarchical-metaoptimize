D=/data1/salehkaleybars/metaopt/data/tinystories
cd $D
while pgrep -f 'tar -xzf TinyStories' >/dev/null; do sleep 30; done
mkdir -p TinyStories_all_data
mv data*.json TinyStories_all_data/ 2>/dev/null
echo "shards_in_place=$(ls TinyStories_all_data/*.json 2>/dev/null | wc -l)" > $D/STAGED.txt
echo "bytes=$(du -sb TinyStories_all_data | cut -f1)" >> $D/STAGED.txt
date >> $D/STAGED.txt
