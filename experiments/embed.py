import os
import pandas as pd
import torch
import data_process as dp
from model import GPT
from tqdm import tqdm

def to_avg_embeddings(df, model, embedding_dim, device):
    with torch.no_grad():
        res = torch.zeros((len(df["3Di"]), embedding_dim))
        for i, (repr, name) in tqdm(enumerate(zip(df["3Di"], df["name"])), total=len(df["3Di"])):
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
        for i, (repr, name) in tqdm(enumerate(zip(df["3Di"], df["name"])), total=len(df["3Di"])):
            seq = torch.tensor([dp.encode(repr)], dtype=torch.long, device=device)
            embeddings = model.seq_embeddings(seq).detach().cpu()
            if len(embeddings.shape) == 1:
                embeddings = embeddings.reshape(1, embedding_dim)
            res.extend(embeddings.tolist())
            names.extend([name]*embeddings.shape[0])
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

def arr_to_batches(arr, max_batch=32):
    batches = []
    if len(arr) - max_batch <= 0:
        return [arr]
    for i in range(0, len(arr), max_batch):
        batches.append(arr[i:i+max_batch])
    return batches
        
    
def to_batches(df, max_batch=32):
    name_batches = []
    Di_batches = []
    df["len"] = df["3Di"].apply(lambda x: len(x))
    lengths = sorted(list(set(df["len"].tolist())))
    for l in lengths:
        same_length_batch = df[df["len"] == l]
        Di = arr_to_batches(same_length_batch["3Di"].tolist(), max_batch)
        names = arr_to_batches(same_length_batch["name"].tolist(), max_batch)
        name_batches.extend(names)
        Di_batches.extend(Di)
    return name_batches, Di_batches

def encode_tensor(batch_3Di):
    total = []
    for sub in batch_3Di:
        total.append(dp.encode(sub))
    return torch.tensor(total, dtype=torch.long)

def to_embeddings_fast(df, model, embedding_dim, device):
    names, reprs = to_batches(df)
    names_all = []
    embeddings_all = []
    with torch.no_grad():
        for repr, name in tqdm(zip(reprs, names), total=len(reprs)):            
            batch_input = encode_tensor(repr).to(device)
            embeddings = model.seq_embeddings_batch(batch_input).detach().cpu()
            for i, subname in enumerate(name):
                per_batch_embed = embeddings[i].tolist()
                embeddings_all.extend(per_batch_embed)
                names_all.extend([subname]*len(per_batch_embed))
        return embeddings_all, names_all

def to_avg_embeddings_fast(df, model, embedding_dim, device):
    names, reprs = to_batches(df)
    embeddings_all = []
    with torch.no_grad():
        for repr, name in tqdm(zip(reprs, names), total=len(reprs)):            
            batch_input = encode_tensor(repr).to(device)
            embeddings = model.seq_embeddings_batch(batch_input).detach().cpu()
            for i, subname in enumerate(name):
                per_batch_embed = embeddings[i].mean(0, keepdim=True)
                embeddings_all.extend(per_batch_embed)
        return torch.tensor(embeddings_all)