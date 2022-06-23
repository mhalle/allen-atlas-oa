# Working idea for Open Anatomy atlas descriptions

This project contains a prototype reference implementation of the next generation openanatomy file format. 

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

All data is  in JSON-LD format, which extends JSON to allow for more semantic and interlinked descriptions of data. These files assume JSON-LD version 1.1. Note that, unfortunately, JSON-LD has its quirks and challenges. OA uses it basically for its object references, types, and [open world data model](https://en.wikipedia.org/wiki/Open-world_assumption). 

### IDs

OA depends on elements (known as nodes in JSON-LD) that have IDs, types, and properties to describe elements of atlases. IDs may be explicit (assigned with "@id") or implicit (unnamed nodes are called blank nodes in JSON-LD). Nodes can be referenced from other nodes only if they have assigned IDs. 

### Types

Node types are specified with the property "@type". A node's type defines what properties are allowed in each node. Types also provide annotation of that the node's purpose or use is. In the OA file format, types are not explicitly inherited like they might be in a class-based type system. They are instead overlaid, more like mix-ins, to provide extra functionality or specialization. A node, then, may have more than one type, which are then specified as a list of type names. 

**By convention, types in OA begin with an uppercase letter.**

### Properties

Properties associate data (literals or references to other nodes) with ids using property names. 

**By convention, property names in OA begin with a lowercase letter.**

### Node merging and the open world model

Another unusual characteristic of the OA file format, and semantic web descriptions using an open world data model, is how information about nodes can be specified. In a typical programming language, all the information about an object's or structure's properties is specified in one place. And changes to an object's property values overwrite the previous values. 

In an open world model, additional information about a node can be added anywhere. If multiple values for a node property are specified, all values are maintained (i.e., values are not ovewritten.)

```
    [
        { 
           "@id": "node1",
           "name": "A node",
           "value": "one"
        },
        {
            "@id": "node1",
            "value": "two",
            "anotherValue": "10" 
        }
    ]
```

produces the same result as:

```
    [
        {
            "@id": "node1",
            "value": ["one", "two"],
            "anotherValue": "10"
        }
    ]
```

The values for "node1" are specified using two JSON objects. The objects are effectively "joined" in database terms using the `@id` property. Values from the two JSON objects are merged together within a graph (see below).

It is actually, then, easier to think of each property of a node as being an array of values. If a property value is specified only once, the property value consists of a JSON array of one element. While JSON-LD offers the option of compacting single valued arrays down to primitive values, OA maintains property arrays of length 1 to simplify  value parsing. So, in effect, the above node would be represented as:
```
    [
        {
            "@id": "node1",
            "value": ["one", "two"],
            "anotherValue": ["10"]
        }
    ]
```
(The OA parser provides shortcuts to treat node property value lists of length 1 specially in order make parsing single valued property values easier.)

## The JSON-LD and OA graph models

### Graphs

A collection of JSON-LD nodes is called a graph. A graph acts as a namespace or container for nodes identified by node IDs: nodes in a graph have unique IDs. Currently, the OA file format consists of a single global namespace, which is most commonly used model in JSON-LD. 

### Contexts

In this typical use, a JSON-LD file consists of an object with a property `@graph` with a value consisting of an array of nodes. This top-level object may also include a `@context` property. The `@context` describes the nodes, IDs, properties, and values of the graph as linked data in a way that makes them suitable for use in semantic web applications. In these semantic web applications, JSON properties are typically transformed into URIs (Uniform Resource Identifiers), which are effectively unique strings that may be de-referencable to provide unique attribution and meaning to the property. In JSON-LD, properties and types map to URIs using the context. Nodes that describe well-known or standardized things my have URIs that references authorities such as the institution that created or defined them. In other cases, IDs of properties may be locally-defined and bear URIs that are relative to the defining document. 

The context of a document can also describe a per-type subcontext that applied to each node of particular type. OA uses this mechanism to specify properties that are valid only within nodes of a specific type.  Some properties are defined outside of these type-based subcontexts and can be used in any node. For example, the OA `metadata` property can be used are a property for any node. 

Note: if a property's URI isn't defined in a context, that property is removed when processed by a compliant JSON-LD parser. There is no warning of undefined properties. A validator such as JSON schema is required if this useful behavior is desired. The same holds true for types. (A special JSON-LD context directive called `@vocab` can provide a default URI prefix for property names and types.)

A `@context` defined inside a JSON-LD file is called a *internal context*. An additional context, called an *external context*, can also be applied when a JSON-LD document is processed. An external context works exactly the same way as an internal context; the only difference is that is doesn't need to be explicitly defined by the creator of the JSON-LD file. 

OA makes at least some attempt to insulate the user from the complexities of JSON-LD and otherwise support the use of JSON data from sources that are naive to JSON-LD or OA. The OA parser applies an OpenAnatomy context, consisting of OA types, properties, and common property prefixes, as an external context when JSON-LD files are imported. (It is possible to turn off this behavior.) It also allows specialized external contexts to be used for specific files.

As a result, OA properties and types can use used without any additional context provided by either the data provider or the atlas builder. 

### `Import` and graphs spanning multiple files

JSON-LD documents consist of graphs defined in single files (though contexts may come from multiple sources). One of the goals of OA, however, is to integrate data from multiple sources and authors together without requiring tight integration between data sources. The more straightforward way to achieve this loose coupling of data is to allow the use of multiple files from different sources. For example, some files may describe the location of atlas data using URLs. Other files may describe segmented regions in the data. Still other files may be dumps of anatomical information from nomenclatures or ontologies. Finally, additional files may provide linkage between different isolated sources of data, associating annotations with anatomic regions or graphical styles with annotated structures. OA thus requires the capability to integrate graph data from multiple files.

To allow data to be imported from multiple files, OA introduces a special node  that has type `Import`. `Import` nodes allow a OA JSON-LD file to include nodes from other files, optionally using a specialized context for processing. By default, the OA default context is also included, though that can be disabled. In the current implementation, nodes imported with the `Import` node are placed into the global ID namespace. The Import node permits a prefix to be added to imported nodes (note that a prefix is added using JSON-LD's `@base` directive and must end in a special character such as `#/:` .)

The `Import` node is a powerful tool in OA. Combined with the merging behavior of the open world data model, `Import` encourages modularity and reuse of data and atlas components. For example, two atlases can be share a large number of underlying data files using `Import`, but also include additional "layers" of data to feature or display unique data. An OA implementation can cache and share these layers to minimize file or network access and memory requirements. 

## More about properties and property names in JSON-LD and OA

Understanding how JSON, JSON-LD, and OA deal with property names is essential in processing and merging data from different sources into a coherent atlas. 

Essentially every data representation and programming language using something like properties or fields to describe data: Python has dictionaries with keys and values, SQL has columns, JSON has objects. Property names are the "handles" we use to access specific aspects or facets of data.

OA, in no small part because it is based on JSON-LD and its semantic web / knowledge management roots, has some complexity with regard to properties. The open world data model and the merging of property data values is one such complexity. Another, also touched on previously, comes from property names.

Let's break down the processing of property names into three stages: raw property data, nodes after they have been processed and expanded with a JSON-LD parser, and OA's in-memory model that provides data access to programmers and programs. Raw data could be a database with column names, a DICOM image with DICOM tags, or a JSON file with objects and property names. Property names are typically simple strings, or binary values that can be mapped to strings. The meaning (or semantics) of these property names may be ad hoc in a program, enforced in a schema, or defined in a standard. 

Simple string or string-like representations for property names are useful and commonplace for most applications. On potential problem they suffer from, however, is name clashes, where two different types of data use the same property name accidentally. Centrally-controlled applications and standards can generally avoid name clashes. The semantic web, however, is based on the idea that information about "things" can come from many sources, making name clashes more likely, and the need for a mechanism to globally define the meaning of properties more important. 

JSON-LD uses a mechanism for property and type naming based on URIs (which is common in RDF, OWL, and other semantic web frameworks). Every property name is mapped to a global or document-local URI in order to distinguish it from property names of a different meaning. For example, schema.org provides an entire set of types and properties for things referenced by web pages for the benefit of search engines. These "things" are all of base type `http://schema.org/Thing`, with many different specializations such as `Person` (`http://schema.org/Person`) and `CreativeWork` (`http://schema.org/CreativeWork`). These types have properties such as `name` (`http://schema.org/name`) or `author` (`http://schema.org/author`). 

In theory, then, schema.org property names and their corresponding values can be used at the same time with data from any number of other schemas, ontologies, or nomenclatures as long as they also define their properties using URIs. The semantic web knowledge representations that exist that are based on RDF represent all their data in this form for this reason.

Expressing every property name as a full URI is, however, far too painful for even the most hardened semantic web diehard to put up with. An abbreviated syntax based on common prefixes has been developed called a CURIE. A CURIE is no more and no less than a prefix abbreviation, mapping a prefix such as `schema` to a URI string such as `http://schema.org`. Using CURIEs, a `name` in schema.org can be called `schema:name` rather than `http://schema.org/name` provided that the `schema` prefix is defined. JSON-LD parsers and processors can assign and expand CURIE definitions to different types and property names, assign default prefixes using `@vocab` and `@base`, and rename properties. 

For the programmer, however, URI-based or even CURIE-based property names are a major practical pain point that offers 95% inconvenience, no practical gains, and only 5% potential value. Programming languages are built around simple string-like names that can be used as `["dictionary_keys"]` or `.property_values`. 

This "impedence mismatch" between semantic web URI-based representations and frictionless data access in mainstream programming language is one reason that I believe the semantic web isn't commonly used. 

OA takes a pragmatic approach to this naming issue by noting that while arbitrary descriptive data ("knowledge") may potentially be used in an atlas, this data is not truly arbitraty in practice. Name clashes can be avoided. Indeed, it is poor development practice to use two different but similarly-named properties that have subtley different semantics. These properties should be aligned, disambiguated, or renamed if at all possible. This disambiguation process is the role of contexts and other preprocessing steps that can map arbitrary URI-based properties into an unambiguous form. This form, which still retains URIs to avoid name clashes, is still potentially compatible with other semantic web tools.

Once this mapping of property names is complete, OA's API shortens the URI-based property and type names by brutally stripping off the URI base paths, leaving only the programmer-friendly simple names of the property. This name can use used as a key to a node's dictionary representation or as part of a dotted "property path" that allows for chained property lookups. This simple step enables an atlas to act as a  database to look up related information across joined and cross-referenced nodes. 

## Using types

In addition to providing schema-like definitions of allowed properties for nodes in a mixin-like manner, types are a powerful way to find specific information that complements properties. For example, every node in OA accepts a `metadata` property that can refer to nodes that describe the node itself (as opposed to the data that the node represents). For example, metadata for an atlas could include its title, abstract, license, authors, or the funding mechanisms that sponsored its creation. Being able to provide metadata all the way down to the node level enables OA to credit every person and every institution fairly. 

Metadata information about a node could be included in a single metadata node (for instance, using the properties from schema.org's CreativeWork type). However, it may be more practical or convenience to separate out the license information from the title and abstact and the authors and grants. 

Types are a way to perform this split. A `LicenseInformation` type could contain information about licensing, `ContributorInformation` about the people and institutions working on the atlas, and a `Description` type could contain title and abstract information. 

Nodes of these different descriptive types could then be assigned independently to a node's `metadata` property. When a programmer looks up the value of the `metadata` property, they will find multiple nodes with difference facets of metadata. This data could be accessed by merging the nodes, but that might introduce name clashes. Alternatively, the list of metadata nodes could by filtered by type, leaving only (for example) `LicenseInformation`. In fact, the entire atlas can be scanned for nodes of type `LicenseInformation` to make sure there aren't multiple licenses.

## Design patterns

OA is still in its alpha-stage infancy, but several design patterns are emerging. They take advantage of several properties of JSON-LD that don't commonly exist in other data storage systems and programming languages. In particular, the open world data model allows different aspects of nodes to be defined separately or in different files. This mechanism encourages data modularity and reuse beyond what is otherwise possible in other systems.

### Keep data from different sources separate

An atlas is composed of different kinds of information. Nodes may describe the location of data on disk or on the internet, how to interpret it, how to extract subsets of it, what that data means, and what a visual representation of that data should look like. Each of these types of data may evolve at a different rate, or be worked on by different people, or perhaps even come from a different or remote source. A robust data model splits the data up in a modular way to avoid interdependencies when possible. Such a data model, for example, allowed more collaborators to work on a project without conflict or version skew.

One simple way to accomplish this goal is to **keep different types of information separate.** URLs describing where to find data files goes in one file. Shapes extracted from a particular data set should be stored together in another file. Standardized nomenclatures should be stored in yet another file, or better yet, be stored in a standard location on the web. A style library is another resource that can be used and reused across multiple atlases to provide visual consistency and quality without being reinvented. **Common resources are best stored remotely and accessed via URL.**

Once all these separate and isolated atlas components are assembled, **the atlas consists primarily of links or joins between different standalone components**. For example, atlas structures are joins between shapes and annotations, and actors are joins between structures and styles. 

Going further, these **joining elements (e.g, Structures, Actors, etc.) can be considered as part of the atlas and defined separately from the nodes they link to**. An atlas can define abstract structures by id, for instance, without including references to any data annotations. Those references can be included in another file. 

How is this layer functionality useful? New information can be added to the atlas without extensively editing atlas data files or raw data files. In general, new data can be provided in new files as an overlay that links existing data. Rather than editing the definition of each node, all the changes associated with the addition are contained in one file.
