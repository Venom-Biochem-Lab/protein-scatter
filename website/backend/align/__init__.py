import subprocess


def bash_cmd(cmd: str | list[str]) -> str:
    return subprocess.check_output(cmd, shell=True).decode()


def venome_pdb_align(venome: str, pdb: str):
    # first move our data from the massive pdb folder I downloaded
    bash_cmd("rm -f align/temp/*")
    bash_cmd(f"cp ~/datasets/pdb/{pdb} align/temp/{pdb}")
    bash_cmd(f"gunzip align/temp/{pdb}")
    pdb = pdb.replace(".gz", "")  # since unzipped

    # then run USalign
    cmd = f"./align/USalign ../../master_venom_galaxy/{venome} align/temp/{pdb} -rasmol align/temp/d -mol prot"
    bash_cmd(cmd)
    return "align/temp/d_all_atm"
