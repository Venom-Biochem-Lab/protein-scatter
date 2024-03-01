import torch
import data_process as dp
from model import GPT
import pandas as pd
import os
import wandb
import time

device = "cuda" if torch.cuda.is_available() else "cpu"
batch_size = 64
block_size = 63
vocab_size = 20
max_iters = 1_000
eval_interval = 100
eval_iters = 200
learning_rate = 5e-4
vocab_size = 20
n_embd = 256
n_head = 8
n_layer = 8
bias = False
dropout = 0.0
beta1 = 0.9
beta2 = 0.95
always_save_checkpoint = True
never_save_checkpoint = (
    False  # has priority and also disables saving on lowest loss checkpoint saving
)
model_args = {
    "vocab_size": vocab_size,
    "n_embd": n_embd,
    "n_head": n_head,
    "bias": bias,
    "n_layer": n_layer,
    "dropout": dropout,
    "block_size": block_size,
}
optim_args = {
    "lr": learning_rate,
    "betas": (beta1, beta2),
}
load_from_checkpoint = False
wandb_project_name = "protein-map-pdb"
wandb_run_name = "gpt" + str(time.time())

# should be populated in the main func
train = None
val = None
wandb_sweep = False


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


def train_gpt(model: torch.nn.Module, optimizer: torch.optim.Optimizer):
    global train
    global val

    best_val_loss = float(13420666)
    for iter in range(max_iters):
        # every once in a while evaluate the loss on train and val sets
        if iter % eval_interval == 0 or iter == max_iters - 1:
            losses = estimate_loss(model, train, val)
            print(
                f"step {iter}: train loss {losses['train']:.4f}, val loss {losses['val']:.4f}"
            )
            wandb.log(
                {
                    "iter": iter,
                    "val_loss": losses["val"],
                    "train_loss": losses["train"],
                }
            )
            if not never_save_checkpoint and (
                iter > 0 and losses["val"] < best_val_loss or always_save_checkpoint
            ):
                best_val_loss = losses["val"]
                save_checkpoint("./", model, optimizer, iter, best_val_loss)

        # sample a batch of data
        xb, yb = dp.get_batch(
            train, batch_size=batch_size, block_size=block_size, device=device
        )

        # evaluate the loss
        logits, loss, _ = model(xb, yb)
        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        optimizer.step()


def num_params(m):
    print(sum(p.numel() for p in m.parameters()) / 1e6, "M parameters")


def sweep_train_api(config=None):
    global model_args
    global optim_args
    global never_save_checkpoint

    with wandb.init(project=wandb_project_name, name=wandb_run_name, config=config):
        config = wandb.config
        model_args["n_embd"] = config.n_embd
        model_args["n_head"] = config.n_head
        model_args["n_layer"] = config.n_layer
        model_args["dropout"] = config.dropout
        optim_args["lr"] = config.lr
        never_save_checkpoint = True

        model = GPT(**model_args)
        model.to(device)
        optimizer = torch.optim.AdamW(model.parameters(), **optim_args)

        train_gpt(model, optimizer)


if __name__ == "__main__":
    df = pd.read_parquet("./datasets/pdb-no-model-no-asm-64-2048.parquet")
    train, val = dp.get_train_val_split(df["3Di"].tolist())
    print("Loaded dataset")

    if not wandb_sweep:
        if load_from_checkpoint:
            model, optimizer = load_checkpoint("./")
            print("Loaded model from checkpoint")
            num_params(model)
        else:
            model = GPT(**model_args)
            model.to(device)
            optimizer = torch.optim.AdamW(model.parameters(), **optim_args)
            print("Created model")
            num_params(model)

        wandb.login()
        with wandb.init(
            project=wandb_project_name,
            name=wandb_run_name,
            config={"batch_size": batch_size, **model_args},
        ):
            train_gpt(model, optimizer)
    else:
        sweep_config = {
            "method": "random",
            "metric": {"name": "val_loss", "goal": "minimize"},
            "parameters": {
                "lr": {"max": 0.1, "min": 0.0001},
                "n_embd": {"values": [128, 256, 512, 1024]},
                "n_head": {"values": [4, 8, 16]},
                "n_layer": {"values": [4, 8, 16]},
                "dropout": {"values": [0.0, 0.1]},
            },
        }
        sweep_id = wandb.sweep(sweep_config, project=wandb_project_name)
        wandb.agent(sweep_id, sweep_train_api, count=10)
