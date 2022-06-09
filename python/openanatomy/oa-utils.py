import json
from pyld import jsonld
import sys
import typer
from typing import List, Optional

app = typer.Typer()

@app.command()
def dummy():
    pass

@app.command()
def merge_contexts(filenames: List[str]):
    subcontexts = []

    for filename in filenames:
        with open(filename) as fp:
            subcontexts.append(json.load(fp))

    print(json.dumps({
        "@context": subcontexts
    }, indent=2))

@app.command()
def merge_files(filenames: List[str], context: str = typer.Option(None)):
    con = {}
    if context:
        with open(context) as fp:
            con = json.load(fp)

    graphs = []
    for filename in filenames:
        with open(filename) as fp:
            ld = json.load(fp)
            expanded = jsonld.expand(ld, {"expandContext": con, "compactArrays": False})
            graphs.append(expanded)

    accum = sum(graphs, [])
    flat = jsonld.flatten(accum, {}, {"compactArrays": False})
    print(json.dumps(flat, indent=2))


if __name__ == '__main__':
    app()

