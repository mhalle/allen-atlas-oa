from uuid import uuid4

BNODE_PREFIX = '_:'
def get_uuid_id():
    return f'urn:uuid:{uuid4()}'


def convert_bnodes_to_uuids(nodes, bnode_mapping=None):
    # the graph are flattened, so every node is in the index.
    # As a result, all the nodes have their ids in the index.
    # Start by creating the mapping of old to new ids. 
    # only do this if passed the index with no nodes, otherwise
    # this is a recursive call.

    if bnode_mapping == None:
        bnode_mapping = {}
        for n in nodes:
            id = n['@id']
            if id.startswith(BNODE_PREFIX):
                bnode_mapping[id] = get_uuid_id()
    
        if not len(bnode_mapping):
            return nodes
    
    # go hunting for bnode references in the graph, mutating the graph and nodes
    for n in nodes:
        try:
            n['@id'] = bnode_mapping[n['@id']]
        except (KeyError, TypeError):
            pass
        for p, v in n.items():
            if p[0] == '@':
                continue
            for vv in v:  # should always be a list
                try:
                    # look for an @id key
                    vv['@id'] = bnode_mapping[vv['@id']]
                    continue
                except TypeError:
                    # a primitive type, no ids
                    continue
                except KeyError:
                    pass
                
                if '@value' in vv:
                    # if it is a value node, nothing to do
                    continue
                    
                try:
                    listv = vv['@list']
                except (KeyError, TypeError):
                    # if it's something else, continue (TODO: @graph)
                    continue

                # process @list
                convert_bnodes_to_uuids(listv, bnode_mapping)

    return nodes
