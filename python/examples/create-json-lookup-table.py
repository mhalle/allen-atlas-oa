import os
import sys
import json
from urllib.parse import urljoin


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

topdir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

from openanatomy import parse_atlas

SampleAtlas = urljoin(topdir, "atlases/ccf-2017/atlas.oa.json")
Context = urljoin(topdir, "contexts/openanatomy-context.jsonld")

if __name__ == "__main__":
    atlas = parse_atlas(SampleAtlas, [Context])
    result = [
        {
            "labelValue": actor.getprop("structure.shape.labelValue").value,
            "name": actor.getprop("structure.annotation.name").value,
            "acronym": actor.getprop("structure.annotation.acronym").value,
            "parentName": actor.getprop(
                "structure.annotation.parent_structure.name"
            ).value if actor.hasprop("structure.annotation.parent_structure") else None,
            "color": actor.getprop("style.color").value,
        }
        for actor in atlas.nodes.filter(type="StructureActor")
    ]
    print(json.dumps(sorted(result, key=lambda x: x["labelValue"]), indent=2))
