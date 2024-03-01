import pandas as pd
from to3Di import to3Di
import torch

# from 5.ipynb

ALPHABET_3Di = [
    "A",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "K",
    "L",
    "M",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "V",
    "W",
    "Y",
]
assert len(ALPHABET_3Di) == 20
TOKENS = [
    *ALPHABET_3Di,
]

to_index = {letter: i for i, letter in enumerate(TOKENS)}
to_3Di = {i: letter for i, letter in enumerate(TOKENS)}


def encode(repr_3Di: str):
    return [to_index[letter.upper()] for letter in repr_3Di]


def decode(encoded: list):
    return "".join([to_3Di[i] for i in encoded])


def pdb_to_3Di_csv(dir, out_file="default.csv"):
    parsed = to3Di(dir)
    pd.DataFrame({"name": parsed.names, "3Di": parsed.repr_3Di}).to_csv(
        out_file, index=False
    )


def get_block_xy(repr_3Di, block_size):
    protein_idx = torch.randint(len(repr_3Di), (1,)).item()
    protein_3Di = repr_3Di[protein_idx]
    block_idx = torch.randint(len(protein_3Di) - block_size, (1,)).item()
    X = protein_3Di[block_idx : block_idx + block_size]
    Y = protein_3Di[block_idx + 1 : block_idx + block_size + 1]
    return X, Y


def get_train_val_split(repr_3Di, ratio=0.9):
    split = int(ratio * len(repr_3Di))
    train = [encode(i) for i in repr_3Di[:split]]
    val = [encode(i) for i in repr_3Di[split:]]
    return train, val


def get_batch(split, batch_size=8, block_size=64, device="cpu"):
    xs = []
    ys = []
    for b in range(batch_size):
        x, y = get_block_xy(split, block_size)
        xs.append(x)
        ys.append(y)
    xs = torch.tensor(xs, dtype=torch.long, device=device)
    ys = torch.tensor(ys, dtype=torch.long, device=device)
    return xs, ys
