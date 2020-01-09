# -*- coding: UTF-8 -*-

import json
import sys

if __name__ == '__main__':
  f = open(sys.argv[1], 'rb')
  data = f.read()
  attrs = json.loads(data)['nodes'][0]['node']['attributes']
  at = {}
  for attr in attrs:
    at[attr['name']] = attr['value']
  result = {}
  result['name'] = json.loads(at['translatedName'])['zh'].encode("utf-8")
  result['name_en'] = at['name'].replace('"', '').encode("utf-8")
  result['center'] = ", ".join([at['centerLng'].replace('"', ''), at['centerLat'].replace('"', '')]).encode("utf-8")
  result['place_id'] = at['googlePlaceId'].replace('"', '').encode("utf-8")
  print json.dumps(result, encoding="UTF-8", ensure_ascii=False)
