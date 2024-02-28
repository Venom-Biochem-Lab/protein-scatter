import pandas as pd
from to3Di import to3Di

# from 5.ipynb

START_TOKEN = "["
END_TOKEN = "]"
TOKENS = [
    # 3Di alphabet (20 codes)
    "A",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "L",
    "N",
    "P",
    "Q",
    "R",
    "S",
    "V",
    "W",
    "Y",
    # special characters
    START_TOKEN,
    END_TOKEN,
]


to_index = {letter: i for i, letter in enumerate(TOKENS)}
to_3Di = {i: letter for i, letter in enumerate(TOKENS)}


def encode(repr_3Di: str):
    return [to_index[letter] for letter in repr_3Di]


def decode(encoded: list):
    return "".join([to_3Di[i] for i in encoded])


def pdb_to_3Di_csv(dir, out_file="default.csv"):
    parsed = to3Di(dir)
    with_start_and_stop_tokens = [
        f"{START_TOKEN}{_repr}{END_TOKEN}" for _repr in parsed.repr_3Di
    ]
    pd.DataFrame({"name": parsed.names, "3Di": with_start_and_stop_tokens}).to_csv(
        out_file, index=False
    )
