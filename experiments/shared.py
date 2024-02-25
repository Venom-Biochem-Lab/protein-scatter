import matplotlib.pyplot as plt
from biopandas.pdb import PandasPdb


def carbon_alphas(pdb_file="../data/test.pdb"):
    ppdb = PandasPdb().read_pdb(pdb_file)
    df = ppdb.df["ATOM"]
    df_ca = df[df["atom_name"] == "CA"].sort_values(by="residue_number")
    return df_ca[["residue_name", "x_coord", "y_coord", "z_coord"]]


def plot_3d(df_ca):
    ax = plt.figure().add_subplot(projection="3d")
    x = df_ca["x_coord"].tolist()
    y = df_ca["y_coord"].tolist()
    z = df_ca["z_coord"].tolist()
    return ax.plot(x, y, z)
