import subprocess
from dataclasses import dataclass
import shutil
import os


def foldseek(cmd: str, verbose=False):
    logs = subprocess.check_output(f"foldseek {cmd}", shell=True).decode()
    if verbose:
        print(logs)


def parse_seq(line):
    return line.rstrip("\n").strip("\x00")


def parse_names(db):
    # read the order of files
    with open(db + ".lookup", "r") as infile:
        return [d[0] for d in [line.split("\t") for line in infile.readlines()]]


def parse_seqs(db):
    with open(db, "r") as infile:
        data = [parse_seq(line) for line in infile.readlines()[:-1]]
        return data


@dataclass
class Parsed3DiAA:
    names: list[str]
    repr_amino_acids: list[str]
    repr_3Di: list[str]


def parse_foldseekdb_for_3Di(db):
    names = parse_names(db)
    repr_3Di = parse_seqs(db + "_ss")
    repr_AA = parse_seqs(db)
    assert (
        len(repr_3Di) == len(repr_AA) == len(names)
    ), "The number of sequences should be the same."
    return Parsed3DiAA(names=names, repr_amino_acids=repr_AA, repr_3Di=repr_3Di)


def to3Di(dir="~/Desktop/proteins", db="./.temp/3DiAA", verbose=False):
    # create db
    os.makedirs(".temp", exist_ok=True)
    try:
        foldseek(f"createdb {dir} {db}", verbose=verbose)
    except Exception as e:
        print(e)
        return

    # parse db
    parsed = parse_foldseekdb_for_3Di(db)

    # remove db
    shutil.rmtree(".temp")

    return parsed


if __name__ == "__main__":
    print(to3Di())
