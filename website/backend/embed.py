import os
import pandas as pd
import torch
import data_process as dp
from model import GPT
from tqdm import tqdm


def to_avg_embeddings(df, model, embedding_dim, device):
    with torch.no_grad():
        res = torch.zeros((len(df["3Di"]), embedding_dim))
        for i, (repr, name) in tqdm(
            enumerate(zip(df["3Di"], df["name"])), total=len(df["3Di"])
        ):
            seq = torch.tensor([dp.encode(repr)], dtype=torch.long, device=device)
            embeddings = model.seq_embeddings(seq).detach().cpu()
            if len(embeddings.shape) > 1:
                embeddings = embeddings.mean(0)
            res[i, :] = embeddings
        return res


def to_embeddings(df, model, embedding_dim, device):
    with torch.no_grad():
        res = []
        names = []
        for i, (repr, name) in tqdm(
            enumerate(zip(df["3Di"], df["name"])), total=len(df["3Di"])
        ):
            seq = torch.tensor([dp.encode(repr)], dtype=torch.long, device=device)
            embeddings = model.seq_embeddings(seq).detach().cpu()
            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, embedding_dim)
            res.extend(embeddings.tolist())
            names.extend([name] * embeddings.shape[0])
        return res, names


def load_model(path: str, device):
    checkpoint = torch.load(path, map_location=device)
    model = GPT(**checkpoint["model_args"])
    model.load_state_dict(checkpoint["model"])
    return model


def export(df, embed2D, path: str):
    df["x"] = embed2D[:, 0]
    df["y"] = embed2D[:, 1]
    df.to_parquet(path, index=False)


def repr_3Di_to_embed(model: GPT, repr_3Di: str):
    tok = dp.encode(repr_3Di)
    seq = torch.tensor([tok], dtype=torch.long)
    embeddings = model.seq_embeddings(seq).detach().cpu()
    return embeddings.squeeze()
