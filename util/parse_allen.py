import json
import sys
import re


KeepFields = [
    'id',
    'parent_structure_id',
    'structure_id_path',
    'name',
    'acronym',
    'color_hex_triplet',
    'graph_id',
    'graph_order',
]

def copy_dict_keys(d, fields):
    return {k: v for k, v in d.items() if k in fields}


def parse_allen(allen_json):
    nodes = allen_json['msg']

    index = {n['id']: copy_dict_keys(n, KeepFields) for n in nodes}
    
    return index

def add_children_and_descendents(index):
    for n in index.values():
        n['child_ids'] = set()
        n['descendent_ids'] = set()

    for n in index.values():
        if n['parent_structure_id'] == None:
            continue

        id = n['id']
        index[n['parent_structure_id']]['child_ids'].add(id)
        
        a = index[n['parent_structure_id']]
        while True:
            a['descendent_ids'].add(id)
            a_id = a['parent_structure_id']
            if a_id == None:
                break
            a = index[a_id]

    for n in index.values():
        n['child_ids'] = sorted(list(n['child_ids']))
        n['descendent_ids'] = sorted(list(n['descendent_ids']))

    return index


def parse_itk_snap(lines):
    ret = {}
    for line in lines:
        e = line.split()
        allen_id = int(e[-1].strip('"'))
        label_value = int(e[0])
        color = [int(x) for x in e[1:4]]
        ret[allen_id] = dict(label_value=label_value, color=color)
    return ret

def add_label_values(index, label_info):
    for i, node in index.items():
        label_values = (
            [label_info[i]['label_value']] +
            [label_info[x]['label_value'] for x in node['descendent_ids']]
        )
        node['label_value'] = label_info[i]['label_value']
        node['label_values'] = label_values
        node['random_color'] = label_info[i]['color']
    return index


def node_to_jsonld(node, prefix):
    ret = {
        "@id": str(node['id']),
        "structure_id": node['id'],
        "name": node['name'],
        "acronym": node['acronym'],
        "alternativeName": node['acronym'],
        "structure_id_path": node['structure_id_path'],
        "graph_id": node['graph_id'],
        "graph_order": node['graph_order'],
        "parent_structure_id": node['parent_structure_id'],
    }
    if node['parent_structure_id'] != None:
       ret['parent_structure'] = str(node['parent_structure_id'])
    return ret



def annotation_jsonld(index, schema_url):
    ret = {
        '@graph': [node_to_jsonld(n, "allen-terms") for n in index.values()]
    }
    return ret

def get_shape(n):
    return {
            "@id": f'shape_{n["label_value"]}',
            "@type": ["Shape", "LabelMaskShape"],
            "labelValue": n['label_value'],
            "includeLabelValues": sorted(n['label_values']),
            "labelMapImage": 'atlasLabelMap'
        }

def get_shapes(index):
    return wrap_oa_context([get_shape(n) for n in index.values()])


OA_SCHEMA = "https://openanatomy.org/schema.oa.jsonld"

def wrap_oa_context(nodes, addl=None):
    if addl:
        return { 
            "@context": [addl],
            "@graph": nodes 
        }
    else:
        return { 
            "@graph": nodes 
        }

def get_allen_structure_annotation(n, prefix):
        return {
            '@id': f"structure_{n['id']}",
            '@type': ["Structure"],
            "annotation": f"allen-terms:{n['id']}"
        }
def get_allen_structure_annotations(index):
    return [get_allen_structure_annotation(n, 'allen-index') for n in index.values()]

def get_structures(index):
    return [get_structure(n) for n in index.values()]


def get_structure(n):
    return {
        '@id': f"structure_{n['id']}",
        '@type': ["Structure"],
        "shape": f"shape_{n['label_value']}"
    }

def get_actors(index):
    ret = []
    for n in index.values():
        r = {
            "@id": f"actor_{n['id']}",
            "@type": ["Actor", "StructureActor"],
            'name': n['name'],
            "structure": f"structure_{n['id']}"
        }
        ret.append(r)
    return wrap_oa_context(ret)


def get_actor_colors_allen(index):
    ret = []
    for n in index.values():
        r = {
            "@id": factor_{n['id']}",
            "@type": "Actor",
            "style": {
                "@type": "Style",
                "color": f"{n['color_hex_triplet']}"
            }
        }
        ret.append(r)
    return wrap_oa_context(ret)

def get_actor_colors_random(index):
    ret = []
    for n in index.values():
        color = n['random_color']
        r = {
            "@id": f"actor_{n['id']}",
            "@type": "Actor",
            "style": {
                "@type": "Style",
                "color": f"rgb({color[0]},{color[1]},{color[2]})"
            }
        }
        ret.append(r)
    return wrap_oa_context(ret)


if __name__ == '__main__':

    allen_info_file = sys.argv[1]
    label_info_file = sys.argv[2]


    allen_json = json.load(open(allen_info_file, 'rb'))
    label_lines = open(label_info_file).readlines()

    label_mapping = parse_itk_snap(label_lines)
    allen_info = parse_allen(allen_json)
    add_children_and_descendents(allen_info)
    add_label_values(allen_info, label_mapping)

    a = annotation_jsonld(allen_info, "https://brain-map.info/cell-locator/nomenclature/ccf-2017/structures#")
    # print(json.dumps(a, indent=2))
    # print(json.dumps(get_shapes(allen_info), indent=2))
    # print(json.dumps(get_structures(allen_info), indent=2))
    print(json.dumps(get_allen_structure_annotations(allen_info), indent=2))

    # print(json.dumps(get_actors(allen_info), indent=2))
    # print(json.dumps(get_actor_colors_allen(allen_info), indent=2))
    # print(json.dumps(get_actor_colors_random(allen_info), indent=2))




    
    dataSources = []
    shapes = []
    colors_allen = []
    colors_itksnap = []

    


