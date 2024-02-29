import torch
import data_process as dp
from model import GPT
import pandas as pd
import os

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 16
block_size = 64
vocab_size = 20
max_iters = 2000
eval_interval = 100
eval_iters = 200
learning_rate = 1e-3
vocab_size = 20
n_embd = 64
n_head = 4
n_layer = 4
bias = False
dropout = 0.0
always_save_checkpoint = True
model_args = {
    "vocab_size": vocab_size,
    "n_embd": n_embd,
    "n_head": n_head,
    "bias": bias,
    "n_layer": n_layer,
    "dropout": dropout,
    "block_size": block_size,
}
optim_args = {"lr": learning_rate}
load_from_checkpoint = True


@torch.no_grad()
def estimate_loss(model, train, val):
    out = {}
    model.eval()
    for split in ["train", "val"]:
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            X, Y = dp.get_batch(
                train if split == "train" else val,
                batch_size=batch_size,
                block_size=block_size,
                device=device,
            )
            logits, loss, _ = model(X, Y)
            losses[k] = loss.item()
        out[split] = losses.mean()
    model.train()
    return out


def save_checkpoint(
    out_dir: str,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    iter_num,
    val_loss,
):
    checkpoint = {
        "model": model.state_dict(),
        "optim": optimizer.state_dict(),
        "model_args": model_args,
        "iter_num": iter_num,
        "val_loss": val_loss,
        "optim_args": optim_args,
    }
    print(f"saving checkpoint to {out_dir}")
    torch.save(checkpoint, os.path.join(out_dir, "checkpoint.pt"))


def load_checkpoint(dir: str):
    global model_args
    global optim_args

    checkpoint = torch.load(os.path.join(dir, "checkpoint.pt"), map_location=device)
    model_args = checkpoint["model_args"]
    optim_args = checkpoint["optim_args"]

    model = GPT(**checkpoint["model_args"])
    model.to(device)
    model.load_state_dict(checkpoint["model"])

    optim = torch.optim.AdamW(model.parameters(), **checkpoint["optim_args"])
    optim.load_state_dict(checkpoint["optim"])

    return model, optim


def train(model: torch.nn.Module, optimizer: torch.optim.Optimizer):
    for iter in range(max_iters):
        # every once in a while evaluate the loss on train and val sets
        if iter % eval_interval == 0 or iter == max_iters - 1:
            losses = estimate_loss(model, train, val)
            print(
                f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}"
            )

        # sample a batch of data
        xb, yb = dp.get_batch(
            train, batch_size=batch_size, block_size=block_size, device=device
        )

        # evaluate the loss
        logits, loss, _ = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


if __name__ == "__main__":
    df = pd.read_csv("./data.csv")
    train, val = dp.get_train_val_split(df["3Di"].tolist())

    if load_from_checkpoint:
        model, optimizer = load_checkpoint("./")
    else:
        model = GPT(**model_args)
        model.to(device)
        optimizer = torch.optim.AdamW(model.parameters(), **optim_args)

    print(sum(p.numel() for p in model.parameters()) / 1e6, "M params")
    context = torch.zeros((1, 1), dtype=torch.long, device=device)
    print(dp.decode(model.generate(context, max_new_tokens=10)[0].tolist()))
