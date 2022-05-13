# Working idea for Open Anatomy atlas descriptions

The Open Anatomy atlas data format (OA) is designed to create highly reusable, modular anatomy atlases. The data format itself is very much in flux. This atlas is a working testbed of format ideas.

## Goals and philosophy
The OA format has a variety of driving concepts and goals:
* Modularity of atlas elements to promote reuse
* Encouraging data to be used "at rest" from remote repositories rather than copied
* Encourage extensibility and "mashups" of data from different sources.
* Separation of concerns between data, data storage/location, semantic interpretation, and visual representation.
* Avoid "yet another format" by acting as a container for other data files, thus
    - Speeding adoption
    - Reducing development time
    - Providing interoperability
* Embrace the web by assuming resources are available across the network and not just in local files
* Using the web / HTML data model, use explicit URLs to point to resources. 
* Provide web-addressibility for important pieces of data inside of binary files.
* Do not assume a particular hierarchy of data, nor use directory/file names to carry information (except for file extensions for file formats).
* Be version control friendly. Different elements of atlases have different rates of change: source images are large but effectively immutable, label maps and geometry are smaller but can be replaced more often, and metadata and styles are textlike but can change frequently. 
* Provide mechanisms for attibution at a granular level to allow everyone to get credit for their contributions.


## File description

The files here represent a significant extension of previous OA atlas descriptions. Significant work remains. Here is a quick guide to the current structure.

All data is (currently) in JSON-LD format, which extends JSON to allow for more semantic and interlinked descriptions of data. These files assume JSON-LD version 1.1. Note that, unfortunately, JSON-LD has its quirks and challenges. OA uses it basically for its object references, types, and [open world data model](https://en.wikipedia.org/wiki/Open-world_assumption). It is not a design goal, however, to force the use of JSON-LD processors, nor to support all of JSON-LD's complex syntax options. OA uses a subset of JSON-LD to simplify parsing and atlas use.

OA depends on elements (known as nodes in JSON-LD) that have IDs, types, and properties to describe elements of atlases. IDs and types may be explicit (assigned with "@id" and "@type") or implicit (unnamed nodes are called blank nodes in JSON-LD, while types can often be inferred from use).

## Files

This section provides a short description of the files used in this sample atlas. Each file consists of a collection of nodes describing different parts or functional layers of the atlas. 

**Note that at this point, the actual Atlas structure that ties all these elementa together is not complete or even here.** 

In particular, JSON-LD has no mechanism to load and merge files of nodes / statements together (analogous to importing modules in programming languages). The atlas uses these files sort of like layers of information that can be selectively loaded. An external mechanism must be used to specify and load these layers.

By convention, files end with the extension "oa.jsonld". They are semantically JSON files as well as JSON-LD.

* `urls.oa.jsonld` - Contains URLs that point to data files. Using these nodes avoids hardcoding path names into files. URL nodes can be relative to a base URL. 

* `datasources.oa.jsonld` - Contains information about how to load NII data from URLs. These data sources can used to access images and other information stored in the files. 

* `images.oa.jsonld` - Nodes that refer to images inside of NII files. There is an image for the different templates as well as the label map.

* `labelmap-shapes.oa.jsonld` - Shapes as defined by masked regions on the label map. The shape information includes the label value for just this structure and also a list of label values that compose all enclosed structures.

* `allen-ontology.oa.jsonld` - The Allen ontology for this atlas, extracted from the Allen API. It consists of names, acronyms, stable numeric IDs for structures, and hierarchy information. 

*  `structures.oa.jsonld` - Structures associate shapes with annotations such as ontologies and nomenclatures. There is currently a one-to-one correspondence of structure to shape and to ontology reference, but that does not need to be the case if more structures are added to the atlas (say, as an overlay).

* `structure-actors.oa.jsonld` - Actors associate visual styles with Structures for rendering. Here, each structure has an actor. The actor definitions in this file do not actually contain a style, which can be defined elsewhere. Think of them as abstract classes.

* `volume-actors.oa.jsonld` - Describe how template volumes should be displayed, for instance using window/level contrast controls.

* `allen-actor-colors.oa.jsonld` - Associate simple styles / colors with actors. These colors are taken from the Allen API.

* `random-actor-colors.oa.jsonld` - Another color scheme, designed to be swapped in for the Allen colors like a stylesheet.

* `spaces.oa.jsonld` - provide objects to specify named coordinate spaces. 

* TODO: Define Stage (or Scene) objects to provide different rendering configurations of Actors.

* TODO: Define the Atlas description node that includes pointers to all other nodes, defining what is exported, and also providing metadata about the atlas itself.
