p = "/data1/salehkaleybars/metaopt/MetaOptimize/codes/Supervised_tasks/MetaOptimize/cifar10/load_data.py"
src = open(p).read()
old = '''    elif dataset_name == "CIFAR10":
        transform = transforms.Compose([transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        trainset = datasets.CIFAR10(root='./data', train=True,download=True, transform=transform)
        testset = datasets.CIFAR10(root='./data', train=False, download=True, transform=transform)'''
new = '''    elif dataset_name == "CIFAR10":
        import os
        norm = transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
        test_transform = transforms.Compose([transforms.ToTensor(), norm])
        if os.environ.get("AUGMENT", "0") == "1":
            train_transform = transforms.Compose([transforms.RandomCrop(32, padding=4), transforms.RandomHorizontalFlip(), transforms.ToTensor(), norm])
        else:
            train_transform = test_transform
        trainset = datasets.CIFAR10(root='./data', train=True, download=True, transform=train_transform)
        testset = datasets.CIFAR10(root='./data', train=False, download=True, transform=test_transform)'''
if old in src:
    open(p + ".bak", "w").write(src)
    open(p, "w").write(src.replace(old, new, 1))
    print("PATCHED_OK (backup at load_data.py.bak); AUGMENT=1 enables RandomCrop+Flip")
else:
    i = src.find("CIFAR10")
    print("NO_MATCH; current block:\n" + src[max(0, i - 60):i + 420])
