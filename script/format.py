# -*- coding: UTF-8 -*-

import json
import sys
import requests

MATCHA_SEARCH_URI = "https://matcha-test-1.d.musta.ch/Matcha/searchNodesInDb"

def get_node_by_filter(key, value, nodeType):
  data = {'filters':[]}
  data['nodeType'] = nodeType
  data['filters'] = [{'name': key, 'values':[value]}]
  data['index'] = 'MatchaCityIndexOnGooglePlaceId'

  resp = requests.post(MATCHA_SEARCH_URI, data=json.dumps(data), headers={'Content-Type': 'application/json'})

  nodes = json.loads(resp.text)['nodes']
  if nodes:
    return nodes[0]["cityNodeValue"]["guid"]
  return None

if __name__ == '__main__':
  f = open(sys.argv[1], 'rb')
  t = sys.argv[2]
  data = f.read()
  records = []
  for feature in json.loads(data)['features']:
    place_id = feature['properties']['place_id']
    if not get_node_by_filter('google_place_id', place_id, t):
      r = {}
      attrs = {}
      attrs["name"] = feature['properties']['name_en']
      attrs["centerLat"] = feature['properties']['center'].split(',')[1].strip()
      attrs["centerLng"] = feature['properties']['center'].split(',')[0].strip()
      attrs["googlePlaceId"] = place_id
      attrs["translatedName"] = {"zh": feature['properties']['name']}
      r["endpoint"] = "CREATE_NODE"
      r["payload"] = {"cityAttributes":attrs}
      records.append(r)

  result = open("./jp_city_create", 'wb')
  result.write(json.dumps(records, encoding="UTF-8", ensure_ascii=False).encode('utf-8'))
  result.flush()
  result.close()
