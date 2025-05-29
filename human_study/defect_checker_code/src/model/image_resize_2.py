from torchvision import datasets, transforms


def get_dataloaders(batch_size=32):
# 이미지 전처리
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ])

    train_dataset = datasets.ImageFolder('./dataset/train/', transform=transform)
    val_dataset = datasets.ImageFolder('./dataset/val/', transform=transform)

    from torch.utils.data import DataLoader

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)

    return train_loader, val_loader, train_dataset