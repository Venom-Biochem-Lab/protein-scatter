import subprocess
from dataclasses import dataclass
import os


def c(cmd: str | list[str]) -> str:
    return subprocess.check_output(cmd, shell=True).decode()


def createdb(dir="~/Desktop/proteins", db="./.temp/3DiAA"):
    """Returns True if the database was created successfully, False otherwise."""
    print(c(f"foldseek createdb {dir} {db}"))


def parse_seq(line):
    return line.rstrip("\n").strip("\x00")


def parse_names(db):
    # read the order of files
    with open(db + ".lookup", "r") as infile:
        idxs = []
        names = []
        for line in infile.readlines():
            [index, name, _] = line.split("\t")
            idxs.append(int(index))
            names.append(name)
        return idxs, names


def parse_3Di(db):
    with open(db + "_ss", "r") as infile:
        data = [parse_seq(line) for line in infile.readlines()]
        return data


def parse_AA(db):
    with open(db, "r") as infile:
        data = [parse_seq(line) for line in infile.readlines()[:-1]]
        return data


@dataclass
class Parsed3DiAA:
    names: list[str]
    repr_amino_acids: list[str]
    repr_3Di: list[str]


def to_3DiAA(dir="~/Desktop/proteins", db="./.temp/3DiAA"):
    os.makedirs(".temp", exist_ok=True)
    try:
        createdb(dir, db)
    except Exception as e:
        print(e)
        return

    _, names = parse_names(db)
    repr_3Di = parse_3Di(db)
    repr_AA = parse_AA(db)

    return Parsed3DiAA(names=names, repr_amino_acids=repr_AA, repr_3Di=repr_3Di)


if __name__ == "__main__":
    to_3DiAA()
