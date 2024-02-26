import subprocess
from dataclasses import dataclass
import os

TEMP_DIR = ".temp"
FOLDSEEK_EXECUTABLE = "foldseek"


def shell(cmd: str):
    return subprocess.check_output(cmd, shell=True).decode()


def foldseek(cmd: str, verbose=False):
    logs = shell(f"{FOLDSEEK_EXECUTABLE} {cmd}")
    if verbose:
        print(logs)


def parse_seq(line):
    return line.rstrip("\n").strip("\x00")


def parse_names(db):
    # read the order of files
    with open(db + ".lookup", "r") as infile:
        return [d[1] for d in [line.split("\t") for line in infile.readlines()]]


def parse_seqs(db):
    with open(db, "r") as infile:
        data = [parse_seq(line) for line in infile.readlines()[:-1]]
        return data


@dataclass
class Parsed3DiAA:
    names: list[str]
    repr_3Di: list[str]


def db_to_3Di(db):
    names = parse_names(db)
    repr_3Di = parse_seqs(db + "_ss")
    # repr_AA = parse_seqs(db)
    assert len(repr_3Di) == len(names), "The number of sequences should be the same."
    return Parsed3DiAA(names=names, repr_3Di=repr_3Di)


def create_db(input_dir, db, verbose=False):
    foldseek(f"createdb {input_dir} {db}", verbose=verbose)


def remove_db(db):
    shell(f"rm -f {db}*")


def create_temp_dir(db):
    os.makedirs(TEMP_DIR, exist_ok=True)
    db = os.path.join(TEMP_DIR, db)
    return db


def to3Di(dir="~/Desktop/proteins", db="3DiAA", verbose=False):
    db = create_temp_dir(db)  # changes db to within the temp directory
    create_db(input_dir=dir, db=db, verbose=verbose)
    parsed = db_to_3Di(db)
    remove_db(db)

    return parsed


if __name__ == "__main__":
    print(to3Di(verbose=True))
