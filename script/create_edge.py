# -*- coding: UTF-8 -*-

import json
import sys
import requests
from geomet import wkt

TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJub2RlX3BvbGljeV9pZCI6MTEsImVkZ2VfcG9saWN5X2lkIjoxMywiZXhwIjoxNTc5MzcyNDY2LCJpYXQiOjE1NzkxMTMyNjYsImVtYWlsIjoieGlhb3dlaS53dUBhaXJibmIuY29tIn0.X1OAr_LDT15PSscW38t-Zs1igFuqrAfE9zcCvdnhOWM"
HOST = "https://matcha.d.musta.ch"
MATCHA_SEARCH_URI = "%s/Matcha/searchNodesInDb" % HOST
MATCHA_EDGE_CREATION_URI = "%s/Matcha/createEdge" % HOST
MATCHA_NODE_CREATION_URI = "%s/Matcha/createNode" % HOST
MATCHA_EDGE_SEARCH_URI = "%s/Matcha/getEdges" % HOST

def is_prod():
  return "test" not in HOST

def get_node_by_place_id(place_id, nodeType):
  data = {'filters':[]}
  data['nodeType'] = nodeType
  data['filters'] = [{'name': 'google_place_id', 'values':[place_id]}]
  data['index'] = 'Matcha%sIndexOnGooglePlaceId' % nodeType

  resp = requests.post(MATCHA_SEARCH_URI, data=json.dumps(data), headers={'Content-Type': 'application/json'})

  nodes = json.loads(resp.text)['nodes']
  if nodes:
    return nodes[0]["%sNodeValue" % nodeType.lower()]["guid"]
  return None

def create_edge(source, target, edgeType, originType):
  data = {"createEdgeAttributes": {"sourceGuid": source, "targetGuid": target, "type": edgeType, "originType": originType}}
  if is_prod():
    data["matchaAclToken"] = TOKEN
  resp = requests.post(MATCHA_EDGE_CREATION_URI, data=json.dumps(data), headers={'Content-Type': 'application/json'})
  edges = json.loads(resp.text)
  if edges.has_key("edge"):
    return edges["edge"]["guid"]
  print edges
  return None

def create_node(nodeType, attrs):
  data = {"createNodeAttributes": attrs}
  if is_prod():
    data["matchaAclToken"] = TOKEN
  resp = requests.post(MATCHA_NODE_CREATION_URI, data=json.dumps(data), headers={'Content-Type': 'application/json'})
  nodes = json.loads(resp.text)
  if nodes.has_key("node"):
    return nodes["node"]["%sNodeValue" % nodeType]["guid"]
  print nodes
  return None

def get_edge(source, edgeType, originTypes):
  data = {"sourceGuids": [source], "edgeTypes": [edgeType], "originTypes":originTypes}
  resp = requests.post(MATCHA_EDGE_SEARCH_URI, data=json.dumps(data), headers={'Content-Type': 'application/json'})
  edges = json.loads(resp.text)["edges"]
  if edges:
    return edges[0]["guid"]
  return None

if __name__ == '__main__':
  f = open(sys.argv[1], 'rb')
  t = sys.argv[2]
  target_node_guid = sys.argv[3]
  print t, target_node_guid
  data = f.read()
  records = []
  for feature in json.loads(data)['features']:
    place_id = feature['properties']['place_id']
    parent_guid = target_node_guid
    if feature['properties'].has_key('state_guid'):
      parent_guid = feature['properties']['state_guid']
    node_guid = get_node_by_place_id(place_id, t)
    if not node_guid:
      print "unexist node", feature['properties']['name']
      continue
    located_in_edge = get_edge(node_guid, "LOCATED_IN", ["CHINA"])
    if not located_in_edge:
      r = create_edge(node_guid, parent_guid, "LOCATED_IN", "CHINA")
      print "create locate edge", node_guid, parent_guid, "LOCATED_IN", r
    else:
      print "skip locate edge", feature['properties']['name']
    shape_edge = get_edge(node_guid, "LOCATION_ASSOCIATED_WITH_GEO_SHAPE", ["KG_CORE", "CHINA"])
    if not shape_edge:
      wkt_string = wkt.dumps(feature['geometry'], decimals= 9)
      cate = feature['geometry']['type'].upper()
      shape_guid = create_node("geoShape", {"geoShapeAttributes":{"category": cate, "wkt": wkt_string}})
      if shape_guid:
        rr = create_edge(node_guid, shape_guid, "LOCATION_ASSOCIATED_WITH_GEO_SHAPE", "CHINA")
        print "create locate edge", node_guid, shape_guid, "LOCATION_ASSOCIATED_WITH_GEO_SHAPE", rr
      else:
        print "failed create shape", feature['properties']['name']
    else:
      print "skip shape edge", feature['properties']['name']

