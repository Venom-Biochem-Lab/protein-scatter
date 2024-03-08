from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict
import pandas as pd
from fastapi.responses import FileResponse
from align import venome_pdb_align


# https://github.com/zeno-ml/zeno-hub/blob/9d2f8b5841d99aeba9ec405b0bc6a5b1272b276f/backend/zeno_backend/classes/base.py#L20
def to_camel(string: str) -> str:
    """Converter for variables from snake_case to camelCase.

    Args:
        string (str): the variable to convert to camelCase.

    Returns:
        str: camelCase representation of the variable.
    """
    components = string.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


# https://github.com/zeno-ml/zeno-hub/blob/9d2f8b5841d99aeba9ec405b0bc6a5b1272b276f/backend/zeno_backend/classes/base.py#L20
class CamelModel(BaseModel):
    """Converting snake_case pydantic models to camelCase models."""

    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)  # type: ignore


def disable_cors(app: FastAPI, origins=["*"]):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


# https://github.com/zeno-ml/zeno/blob/main/zeno/server.py#L52
def custom_generate_unique_id(route: APIRoute):
    return route.name


def init_fastapi_app() -> FastAPI:
    app = FastAPI(
        title="protein-map backend",
        generate_unique_id_function=custom_generate_unique_id,
    )
    return app


df = pd.read_parquet("./data/embed-sub-venome-2D-8.parquet")
info_venome = pd.read_parquet("./data/all-venome.parquet")
print("data downloaded")

app = init_fastapi_app()
disable_cors(app, origins=["*"])


class TestResponse(BaseModel):
    nice: int


@app.get("/", response_model=TestResponse)
def test():
    return TestResponse(nice=1)


class DataResponse(BaseModel):
    names: list[str]
    x: list[float]
    y: list[float]


class InfoVenomeResponse(BaseModel):
    names: list[str]


@app.get("/align/{venome:str}/{pdb:str}")
def get_align(venome: str, pdb: str):
    outpath = venome_pdb_align(venome, pdb)
    return FileResponse(outpath, filename=f"{venome}-{pdb}-superimposed.pdb")


@app.get("/file/{filename:str}")
def get_pdb_file(filename: str):
    return FileResponse(f"../../master_venom_galaxy/{filename}", filename=filename)


@app.get("/info/venome", response_model=InfoVenomeResponse)
def get_info_venome():
    global info_venome
    return InfoVenomeResponse(names=info_venome["name"].tolist())


@app.get("/data", response_model=DataResponse)
def get_data():
    global df
    return DataResponse(
        x=df["x"].tolist(), y=df["y"].tolist(), names=df["name"].tolist()
    )
