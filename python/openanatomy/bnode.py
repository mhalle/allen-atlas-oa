import ulid

BNODE_PREFIX = '_:b'
def unique_bnode_id():
    return f'_:b{ulid.new()[:-10]}'


def convert_graph_unique_bnodes(index):
    bnode_mapping = {}

    for id in index:
        if id.startswith(BNODE_PREFIX):
            bnode_mapping[id] = unique_bnode_id()
    
    if not len(bnode_mapping):
        return index

    # go hunting for bnodes in an expanded uncompacted graph

    for n in index.values():
        try:
            n['@id'] = bnode_mapping[n['@id']]
            index[n['@id']] = n
        except KeyError:
            pass
        for p, v in n.items():
            if p[0] == '@':
                continue
            for vv in v:
                try:
                    vv['@id'] = bnode_mapping[vv['@id']]
                except KeyError:
                    continue
    for oldid in bnode_mapping:
        del index[oldid]
    return index
