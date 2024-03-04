from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.routing import APIRoute
from pydantic import BaseModel, ConfigDict
import pandas as pd
from to3Di import to3Di
from embed import repr_3Di_to_embed, load_model
import numpy as np


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


class VectorDB:
    def __init__(self, df):
        self.index = np.vstack(df["embed"].values)

    @property
    def shape(self):
        return self.index.shape

    def query(self, query_embed: np.ndarray) -> np.ndarray:
        diff = self.index - query_embed
        dists = np.linalg.norm(diff, axis=1)
        return dists


df = pd.read_parquet("./data/embed2D-large-3.parquet")
print("data downloaded")
index = VectorDB(df)
print("index constructed", index.shape)
model = load_model("./data/models/checkpoint-large-3.pt", "cpu")
print("model downloaded")

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


def data_to_embed():
    converted = to3Di("./data")
    repr_3Di = converted.repr_3Di[0]
    embed = repr_3Di_to_embed(model, repr_3Di)
    avg_embed = embed.mean(0).reshape(1, -1)
    return avg_embed


@app.get("/similar", response_model=list[float])
def get_similar():
    global model
    global index
    embed = data_to_embed().numpy()
    similarity_scores = index.query(embed)
    return similarity_scores.tolist()


@app.get("/data", response_model=DataResponse)
def get_data():
    global df
    return DataResponse(
        x=df["x"].tolist(), y=df["y"].tolist(), names=df["name"].tolist()
    )
