# Measures the ImageNet-489 input pipeline ALONE (no GPU, no model): ImageFolder
# scan + RandomResizedCrop(224) + flip + ToTensor + Normalize, at the harness's
# batch size.  This is the hard ceiling on images/sec that any GPU can be fed.
import sys, time
import torch, torchvision.datasets as D, torchvision.transforms as T
root=sys.argv[1]; bs=int(sys.argv[2]); nw=int(sys.argv[3]); nb=int(sys.argv[4])
norm=T.Normalize(mean=[0.485,0.456,0.406],std=[0.229,0.224,0.225])
t0=time.time()
ds=D.ImageFolder(root+'/train', T.Compose([T.RandomResizedCrop(224),T.RandomHorizontalFlip(),T.ToTensor(),norm]))
scan=time.time()-t0
print("SCAN_SEC %.1f  IMAGES %d  CLASSES %d"%(scan,len(ds),len(ds.classes)),flush=True)
dl=torch.utils.data.DataLoader(ds,batch_size=bs,shuffle=True,num_workers=nw,pin_memory=True,drop_last=True,persistent_workers=True)
it=iter(dl)
for _ in range(10): next(it)          # warm the workers
t=time.time(); n=0
for _ in range(nb):
    x,y=next(it); n+=x.size(0)
d=time.time()-t
print("DATALOADER workers=%d batch=%d batches=%d images=%d sec=%.1f IMG_PER_SEC %.1f"%(nw,bs,nb,n,d,n/d),flush=True)
print("FULL_EPOCH_MIN_dataonly %.1f"%(len(ds)/(n/d)/60.0),flush=True)
