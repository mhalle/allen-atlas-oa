
# Files

This section provides a short description of the files used in this sample atlas. Each file consists of a collection of nodes describing different parts or functional layers of the atlas. 

**Note that at this point, the actual Atlas structure that ties all these elementa together is not complete or even here.** 

In particular, JSON-LD has no mechanism to load and merge files of nodes / statements together (analogous to importing modules in programming languages). The atlas uses these files sort of like layers of information that can be selectively loaded. An external mechanism must be used to specify and load these layers.

By convention, files end with the extension "oa.jsonld". They are semantically JSON files as well as JSON-LD.

* `urls.oa.jsonld` - Contains URLs that point to data files. Using these nodes avoids hardcoding path names into files. URL nodes can be relative to a base URL. 

* `datasources.oa.jsonld` - Contains information about how to load NII data from URLs. These data sources can used to access images and other information stored in the files. 

* `images.oa.jsonld` - Nodes that refer to images inside of NII files. There is an image for the different templates as well as the label map.

* `labelmap-shapes.oa.jsonld` - Shapes as defined by masked regions on the label map. The shape information includes the label value for just this structure and also a list of label values that compose all enclosed structures.

* `allen-nomenclature-terms.oa.jsonld` - The Allen ontology for this atlas, extracted from the Allen API. It consists of names, acronyms, stable numeric IDs for structures, and hierarchy information. 

*  `structures.oa.jsonld` - Structures associate shapes with annotations such as ontologies and nomenclatures. There is currently a one-to-one correspondence of structure to shape and to ontology reference, but that does not need to be the case if more structures are added to the atlas (say, as an overlay).

* `structure-actors.oa.jsonld` - Actors associate visual styles with Structures for rendering. Here, each structure has an actor. The actor definitions in this file do not actually contain a style, which can be defined elsewhere. Think of them as abstract classes.

* `structure-allen-annotations.oa.jsonld` - Actors semantic annotations with Structures.

* `volume-actors.oa.jsonld` - Describe how template volumes should be displayed, for instance using window/level contrast controls.

* `allen-actor-colors.oa.jsonld` - Associate simple styles / colors with actors. These colors are taken from the Allen API.

* `random-actor-colors.oa.jsonld` - Another color scheme, designed to be swapped in for the Allen colors like a stylesheet.

* `spaces.oa.jsonld` - provide objects to specify named coordinate spaces. 

* `atlas.oa.jsonld` and `atlas-random-colors.oa.jsonld` top-level atlas files that import relevant data files using the Import node.

# TODO

* TODO: Define Stage (or Scene) objects to provide different rendering configurations of Actors. That includes styles for stages (cameras and other scene-level features).

* TODO: Define the Atlas description node that includes pointers to all other nodes, defining what is exported, and also providing metadata about the atlas itself.

* TODO: formalize the JSON-LD context / schema, overall and for each node.

