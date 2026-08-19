# Dataset status and scope decisions

## CIFAR-10 — in use, complete
Staged at `.../cifar10/data/cifar-10-python.tar.gz` (170,498,071 bytes, verified) on **both**
accounts. Compute nodes have no internet, so datasets must be staged from a login node.
`AUGMENT=1` enables RandomCrop(32, pad=4) + RandomHorizontalFlip; without it ResNet-18 reaches
~0 train loss in epoch 1 and there is no optimisation headroom (the shipped code has no
augmentation, and the parent paper never mentions any).

## ImageNet — INCOMPLETE, scoped OUT of the project

Measured at `/data1/salehkaleybars/imagenet_data/ILSVRC/Data/CLS-LOC`:

| | found | expected |
|---|---|---|
| train class directories | **489** | 1000 |
| images per present class (sampled) | 1300 | ~1300 ✓ |
| val files | 50,000 | 50,000 ✓ |
| train size on disk | **68 GB** | ~148 GB |

So it is a **partial download, not a corrupt one** — the classes that are present are complete.

**Decision: scope full ImageNet-1k out.** Completing the download requires ImageNet credentials
and acceptance of the ImageNet Terms of Access, which are the account holder's to give, not
something to automate. A 489-class subset cannot support a comparison with published ImageNet-1k
numbers, and silently training on half the classes while calling it "ImageNet" would be worse
than not running it.

**Consequence for the paper — this is acceptable, and here is why.** ImageNet was originally
wanted for the *scale* axis, to explain why the parent paper's blockwise advantage vanished
there (§7.3). That question now has a mechanism from CIFAR-10 alone: granularity buys
convergence *speed*, and a long budget lets the coarse arm catch up, so the advantage stops
converting into a final-accuracy difference. The prediction is testable without ImageNet by
varying the budget directly, which is cheap.

**Substitutes for the scale/difficulty axis** (both free, no credentials, torchvision-native):
1. **CIFAR-100** — same input size and architecture, 10x the classes, harder. Isolates task
   difficulty from image resolution.
2. **Budget sweep on CIFAR-10** — 25 / 50 / 100 / 300 epochs. This is the *direct* test of the
   budget mechanism and does not need a new dataset at all.

If ImageNet is wanted later, the honest options are (a) the account holder completes the
download, or (b) report the 489-class subset explicitly as "ImageNet-489", never as ImageNet.

## TinyStories — not yet staged
Needed only for the language-model arm (parent paper §7.4). Lower priority than the budget
sweep and CIFAR-100, both of which bear directly on the current claim.
