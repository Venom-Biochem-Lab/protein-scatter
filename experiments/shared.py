from biopandas.pdb import PandasPdb
import plotly.express as px


def alpha_carbons(pdb_file="../data/test.pdb"):
    ppdb = PandasPdb().read_pdb(pdb_file)
    df = ppdb.df["ATOM"]
    df_ca = df[df["atom_name"] == "CA"].sort_values(by="residue_number")
    return df_ca[["residue_name", "x_coord", "y_coord", "z_coord"]]


def plot_3d(df_ca):
    fig = px.line_3d(df_ca, x="x_coord", y="y_coord", z="z_coord")
    return fig
