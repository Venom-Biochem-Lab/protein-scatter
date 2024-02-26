import subprocess
from dataclasses import dataclass
import os
import fire

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
    repr_AA: list[str] | None = None


def db_to_3Di(db, include_amino_acids=False):
    names = parse_names(db)
    repr_3Di = parse_seqs(db + "_ss")
    repr_AA = None
    if include_amino_acids:
        repr_AA = parse_seqs(db)
        assert len(repr_AA) == len(names), "The number of sequences should be the same."
    assert len(repr_3Di) == len(names), "The number of sequences should be the same."
    return Parsed3DiAA(names=names, repr_3Di=repr_3Di, repr_AA=repr_AA)


def create_db(input_dir, db, verbose=False):
    foldseek(f"createdb {input_dir} {db}", verbose=verbose)


def remove_db(db):
    shell(f"rm -f {db}*")


def create_temp_dir(db):
    os.makedirs(TEMP_DIR, exist_ok=True)
    db = os.path.join(TEMP_DIR, db)
    return db


def to3Di(input_dir, db="3DiAA", verbose=False, include_amino_acids=False):
    db = create_temp_dir(db)  # changes db to within the temp directory
    create_db(input_dir=input_dir, db=db, verbose=verbose)
    parsed = db_to_3Di(db, include_amino_acids=include_amino_acids)
    remove_db(db)

    return parsed


def cli(dir, name="3DiAA", verbose=False, amino_acids=False):
    result = to3Di(
        input_dir=dir, db=name, verbose=verbose, include_amino_acids=amino_acids
    )
    print("names")
    print(result.names)
    print("3Di")
    print(result.repr_3Di)
    if amino_acids:
        print("AA")
        print(result.repr_AA)


if __name__ == "__main__":
    fire.Fire(cli)
