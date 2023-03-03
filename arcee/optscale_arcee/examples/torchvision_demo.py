import torch
from torch import nn
from torch.utils.data import DataLoader
from torchvision import datasets
from torchvision.transforms import ToTensor

import optscale_arcee as arcee


filename = "torchvision.pth"

# init arcee
arcee.init("test", "torchvision")

arcee.tag("project", "torchvision demo")

# Download training data
arcee.milestone("Download training data")
arcee.stage("preparing")
training_data = datasets.FashionMNIST(
    root="data",
    train=True,
    download=True,
    transform=ToTensor(),
)

# Download test data
arcee.milestone("Download test data")
test_data = datasets.FashionMNIST(
    root="data",
    train=False,
    download=True,
    transform=ToTensor(),
)
batch_size = 64


# Define model
class NeuralNetwork(nn.Module):
    def __init__(self):
        super().__init__()
        self.flatten = nn.Flatten()
        self.linear_relu_stack = nn.Sequential(
            nn.Linear(28 * 28, 512),
            nn.ReLU(),
            nn.Linear(512, 512),
            nn.ReLU(),
            nn.Linear(512, 10),
        )

    def forward(self, x):
        x = self.flatten(x)
        logits = self.linear_relu_stack(x)
        return logits


def train(dataloader, model, loss_fn, optimizer, epoch):
    size = len(dataloader.dataset)
    model.train()
    for batch, (x, y) in enumerate(dataloader):
        x, y = x.to(device), y.to(device)

        # prediction error
        pred = model(x)
        loss = loss_fn(pred, y)

        # backpropagation
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        if batch % 100 == 0:
            loss, current = loss.item(), batch * len(x)
            arcee.send({"loss": loss, "iter": current, "epoch": epoch})
            print(f"loss: {loss:>7f}  [{current:>5d}/{size:>5d}]")


def test(dataloader, model, loss_fn):
    size = len(dataloader.dataset)
    num_batches = len(dataloader)
    model.eval()
    test_loss, correct = 0, 0
    with torch.no_grad():
        for x, y in dataloader:
            x, y = x.to(device), y.to(device)
            pred = model(x)
            test_loss += loss_fn(pred, y).item()
            correct += (pred.argmax(1) == y).type(torch.float).sum().item()
    test_loss /= num_batches
    correct /= size
    arcee.send({"accuracy": 100 * correct})
    print(
        f"Error: \n Accuracy: {(100*correct):>0.1f}%," f"Avg loss: {test_loss:>8f} \n"
    )


if __name__ == "__main__":
    arcee.milestone("create data loaders")
    # Create data loaders
    train_dataloader = DataLoader(training_data, batch_size=batch_size)
    test_dataloader = DataLoader(test_data, batch_size=batch_size)

    for x, y in test_dataloader:
        print(f"Shape of x [N, C, H, W]: {x.shape}")
        print(f"Shape of y: {y.shape} {y.dtype}")
        break

    # detect CUDA /  cpu or gpu device for training.
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using {device} device")
    arcee.milestone("define model")
    model = NeuralNetwork().to(device)
    print(model)
    loss_fn = nn.CrossEntropyLoss()
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)

    epochs = 5
    arcee.stage("calculation")
    for e in range(epochs):
        epoch = e + 1
        arcee.milestone("Entering epoch %d" % epoch)
        print(f"+Epoch {epoch}\n-------------------------------")
        train(train_dataloader, model, loss_fn, optimizer, epoch)
        test(test_dataloader, model, loss_fn)
    arcee.milestone("Finish training")
    print("+Task Done!")
    arcee.milestone("saving model")
    torch.save(model.state_dict(), filename)
    print(f"+Saved PyTorch Model State to {filename}")
    arcee.finish()
