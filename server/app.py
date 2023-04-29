from pathlib import Path
from typing import Literal

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .driver import Controller


class Instructions(BaseModel):
    start: float
    end: float


static_path = Path(__file__).parent.parent / "app"
ctrl = Controller({"y": 100, "x": 170, "rotate": 90, "grab": 0}, debug=True)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/pet")
def pet(data: Instructions) -> None:
    ctrl.set("rotate", int(45 + data.start * 90))  # rotate to start position
    ctrl.move("y", -40)  # lower arm
    ctrl.move("rotate", int(data.end * 90))  # rotate to end position
    ctrl.move("y", 40)  # move arm back up


@app.get("/health")
def health() -> Literal[True]:
    return True


app.mount("/", StaticFiles(directory=static_path, html=True), name="static")
