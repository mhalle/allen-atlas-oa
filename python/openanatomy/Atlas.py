import json
from pyld import jsonld
import re
from collections import UserDict, UserList
from urllib.parse import urljoin
import urllib.request
import itertools
import sys

LastRE = re.compile(r"(\w+)$")

def shorten(url):
    return LastRE.search(url).group(1)

def match_values_filter(o, m):
    for k in m.keys():
        if o.getprop(k).value != m[k]:
            return False
    return True

def match_ids_filter(o, m):
    for k in m.keys():
        if o.getprop(k).id != m[k]:
            return False

    return True

class ValueList(UserList):
    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index

    @property
    def value(self):
        if len(self) == 1:
            return self[0].value
        else:
            return [v.value for v in self]

    @property
    def valuelist(self):
        return [v.value for v in self]

    @property
    def type(self):
        if len(self) == 1:
            return self[0].type
        else:
            return [v.type for v in self]

    @property
    def fqtype(self):
        if len(self) == 1:
            return self[0].fqtype
        else:
            return [v.fqtype for v in self]

    @property
    def typelist(self):
        return [v.type for v in self]

    @property
    def fqtypelist(self):
        return [v.type for v in self]

    @property
    def language(self):
        if len(self) == 1:
            return self[0].language
        else:
            return [v.language for v in self]

    @property
    def languagelist(self):
        return [v.language for v in self]

    @property
    def ref(self):
        if len(self) == 1:
            return self[0].ref
        else:
            return ValueList(v.ref for v in self)

    @property
    def hasref(self):
        if len(self) == 1:
            return self[0].hasref
        else:
            return [v.hasref for v in self]

    @property
    def reflist(self):
        return ValueList(v.ref for v in self)

    @property
    def id(self):
        if len(self) == 1:
            return self[0].id
        else:
            return [v.id for v in self]

    @property
    def idlist(self):
        return [v.ref for v in self]

    def get(self, id):
        if self.index == None:
            self.index = {n.id: n for n in self}
        return self.index[id]

    def mergeprop(self, prop):
        r = ValueList()
        for n in self.reflist:
            if prop in n.ref:
                r.append(n[prop])
        return r

    def filter(
        self,
        filter=None,
        type="",
        fqtype="",
        match_values=None,
        match_ids=None,
        id=None,
    ):
        result = self
        if filter:
            result = ValueList(v.ref for v in result if filter(v.ref))

        if not type == "":
            if type == None:
                result = ValueList(v.ref for v in result if "@type" not in v)
            else:
                result = ValueList(
                    v.ref for v in result if "@type" in v and type in v.type
                )

        if not fqtype == "":
            if fqtype == None:
                result = ValueList(v.ref for v in result if "@type" not in v)
            else:
                result = ValueList(
                    v.ref for v in result if "@type" in v and type in v.fqtype
                )

        if not match_values == None:
            result = ValueList(
                v.ref for v in result if match_values_filter(v.ref, match_values)
            )

        if not match_ids == None:
            result = ValueList(
                v.ref for v in result if match_ids_filter(v.ref, match_ids)
            )

        if not id == None:
            if self.index == None:
                self.index = {n.id: n for n in self}
            result = ValueList([self.index[id]])

        return result


class ValueObject(UserDict):
    def __init__(self, *args, index=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.index = index

    @property
    def value(self):
        try:
            return self["@value"]
        except KeyError:
            return self["@list"]

    @property
    def language(self):
        return self["@language"]

    @property
    def haslanguage(self):
        return "@language" in self

    @property
    def type(self):
        return self["@type"]

    @property
    def hastype(self):
        return "@type" in self

    @property
    def valuelist(self):
        v = self["@value"]
        if isinstance(v, list):
            return [x["@value"] for x in v]
        if isinstance(v, dict):
            return [self["@value"]]

    @property
    def graph(self):
        return self["@graph"]

    @property
    def id(self):
        return self["@id"]

    @property
    def ref(self):
        return self.index[self["@id"]] if self.index else self

    @property
    def hasref(self):
        return "@id" in self and self["@id"] in self.index

    def getprop(self, path):
        props = path.split(".")
        node = self
        for p, pnext in itertools.zip_longest(props, props[1:]):
            if p[0].isupper():  # already handled in a previous iteration
                continue
            if pnext and pnext[0].isupper():
                node = node[p].reflist.filter(type=pnext)
            else:
                node = node[p]
            if not pnext:
                break
            if node.hasref:
                node = node.ref

        return node

    def hasprop(self, path):
        props = path.split(".")
        node = self
        for p, pnext in itertools.zip_longest(props, props[1:]):
            if p[0].isupper():  # already handled in a previous iteration
                continue
            if pnext and pnext[0].isupper():
                try:
                    node = node[p].reflist.filter(type=pnext)
                except KeyError:
                    return False
            else:
                try:
                    node = node[p]
                except KeyError:
                    return False
            if not pnext:
                break
            if node.hasref:
                node = node.ref

        return True


def get_value_object(v, index):
    if isinstance(v, dict):
        return ValueObject(v, index=index)

    return ValueObject({"@value": v})


def listify(t):
    return t if isinstance(t, list) else [t] if t else []


def parse_nodes(nodes):
    index = {}
    pindex = {}

    for n in nodes:
        index[n["@id"]] = n

    for n in nodes:
        pindex[n["@id"]] = ValueObject(index=pindex)

    for n in nodes:
        p = pindex[n["@id"]]
        for prop, value in n.items():
            if prop == "@type":
                p["@type"] = [shorten(v) for v in listify(value)]
                p.fqtype = listify(value)
                continue
            if prop[0] == "@":
                p[prop] = n[prop]
                continue

            p[shorten(prop)] = ValueList([get_value_object(v, pindex) for v in value])

    return ValueList(pindex.values(), index=pindex)


def jsonld_to_nodes(jld):
    return jsonld.flatten(jsonld.expand(jld), {}, {"compactArrays": False})





def parse_and_expand(
    filename,
    basecontext,
    importType,
    context_filenames=None,
    idprefix=None,
    loader=None,
):
    # import property names are all suffixes of the import type
    srcprop = importType + "/src"
    ctxprop = importType + "/contextsrc"
    frameprop = importType + "/framesrc"
    idprefixprop = importType + "/idprefix"
    inheritcontextprop = importType + "/inheritcontext"
    srcbaseprop = importType + "/srcbase"

    if not loader:
        loader = DocumentLoader()

    this_context = basecontext
    if context_filenames:
        cdata = merge_context_files(context_filenames, filename, loader=loader)
        this_context = merge_contexts([basecontext, cdata]) if basecontext else cdata
    if idprefix:
        prefix_context = {"@base": idprefix}
        this_context = merge_contexts([this_context, prefix_context])
        
    ndata = loader.load(filename)

    jld = jsonld.expand(ndata, {"expandContext": this_context, "base":'#'})

    new_nodes = []

    for node in jld:
        if not "@type" in node or not importType in node["@type"]:
            new_nodes.append(node)
            continue

        # handle import
        
        if basecontext:
            # only look for imports if using open anatomy semantics.
            src = [x["@value"] for x in node[srcprop]] if srcprop in node else []
            ctx = [x["@value"] for x in node[ctxprop]] if ctxprop in node else []
            idprefix = node[idprefixprop][0]["@value"] if idprefixprop in node else None
            # frame = [x["@value"] for x in node[frameprop]] if frameprop in node else []
            inheritcontext = ( node[inheritcontextprop][0]["@value"]
                    if inheritcontextprop in node else True
            )
            srcbase = (
                [x["@value"] for x in node[srcbaseprop]]
                if srcbaseprop in node
                else None
            )

            if srcbase:
                srcbase = urljoin(filename, srcbase)
            for s in src:
                import_filename = urljoin(srcbase if srcbase else filename, s)
                importnodes = parse_and_expand(
                    import_filename,
                    this_context if inheritcontext else None,
                    importType,
                    ctx,
                    loader=loader,
                    idprefix=idprefix
                )
                new_nodes += importnodes

    return new_nodes


def merge_context_files(filenames, base=None, loader=None):
    subcontexts = []
    if not loader:
        loader = DocumentLoader()

    for filename in filenames:
        filename = urljoin(base, filename) if base else filename
        js = loader.load(filename)

        subcontexts.append(js)

    return merge_contexts(subcontexts)


def merge_contexts(contexts):
    accum = []

    for c in contexts:
        if isinstance(c, dict):
            if "@context" in c:
                dd = c["@context"]
                if isinstance(dd, dict):
                    accum.append(dd)
                else:
                    accum += dd
            else:
                accum.append(c)
        else:
            accum += c
    return {"@context": accum}


class DocumentLoader:
    def __init__(self):
        self.file_cache = {}

    def load(self, url_or_filename: str):
        if url_or_filename in self.file_cache:
            return self.file_cache[url_or_filename]

        if str(url_or_filename).startswith(("http:", "https:")):
            with urllib.request.urlopen(url_or_filename) as fp:
                self.file_cache[url_or_filename] = json.load(fp)
        else:
            with open(url_or_filename) as fp:
                self.file_cache[url_or_filename] = json.load(fp)

        return self.file_cache[url_or_filename]


class Atlas:
    def __init__(self):
        self.oacontext = None
        self.atlas_src_filename = None
        self.oaschema = "https://www.openanatomy.org/schema/"
        self.loader = DocumentLoader()

    def parse_context(self, contextfilenames, contextdir=None):
        self.oacontext = merge_context_files(
            contextfilenames, contextdir, loader=self.loader
        )
        return self.oacontext

    def parse_atlas(self, filename):
        merged = parse_and_expand(filename, self.oacontext, self.oaschema + "Import", loader=self.loader)
        flattened = jsonld.flatten(merged, {}, {"compactArrays": False})
        self.fqnodes = flattened['@graph'] if '@graph' in flattened else flattened
        self.nodes = parse_nodes(self.fqnodes)


def parse_atlas(atlasfilename, oacontextfilenames, contextbase=None):
    atlas = Atlas()
    atlas.parse_context(oacontextfilenames, contextbase)
    atlas.parse_atlas(atlasfilename)
    return atlas

if __name__ == "__main__":
    import sys

    contextfilenames = [sys.argv[2]]
    atlas = parse_atlas(sys.argv[1], contextfilenames)
