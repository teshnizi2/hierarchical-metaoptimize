import sys, glob, os
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator

base = sys.argv[1]
rows = []
for d in sorted(glob.glob(os.path.join(base, 'Tensorboard_outputs', '*'))):
    ea = EventAccumulator(d, size_guidance={'scalars': 10000}); ea.Reload()
    tags = ea.Tags().get('scalars', [])
    def series(tag):
        return [s.value for s in ea.Scalars(tag)] if tag in tags else []
    tl = series('Performance/train_loss')
    ta = series('Performance/test_accuracy')
    name = os.path.basename(d)
    if not tl:
        print(f"{name}: NO train_loss (tags={tags})"); continue
    # train loss at milestones + min; convergence speed = epochs to reach loss<=0.1
    def at(e): return tl[e] if e < len(tl) else float('nan')
    reach = next((i for i,v in enumerate(tl) if v <= 0.1), None)
    print(f"{name}: tl@5={at(5):.4f} tl@10={at(10):.4f} tl@20={at(20):.4f} "
          f"min_tl={min(tl):.4f} ep->tl<=0.1={reach} best_test={max(ta):.2f}")
