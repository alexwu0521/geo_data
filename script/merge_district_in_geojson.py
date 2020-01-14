# -*- coding: UTF-8 -*-

import os
import os.path
import json
import sys
import requests

GEO_ENDPOINT = "https://prometheus.d.musta.ch/api/simplified?s=%s&force_geocode_with_location=true"

CITY_LIST = [u"北広島市", u"札幌市", u"仙台市", u"さいたま市", u"千葉市", u"横浜市", u"川崎市", u"相模原市", u"新潟市", u"静岡市", u"浜松市", u"名古屋市", u"京都市", u"大阪市", u"堺市", u"神戸市", u"岡山市", u"広島市", u"北九州市", u"福岡市", u"熊本市"]

def buildWKT(coords):
  return 'MULTIPOLYGON(' + ','.join(['(' + ','.join(['(' + ','.join([' '.join([str(coord[0]), str(coord[1])]) for coord in linering]) + ')' for linering in polygon ]) + ')' for polygon in coords]) + ')'

def geo_result(state_name, name, query):
  geo_query = GEO_ENDPOINT % query
  res = json.loads(requests.get(geo_query).text)
  types = res['types']
  precision = res['precision']
  country_code = res['country_code']
  place_id = res['place_id']
  name_en = res['city']
  center = "%s, %s" % (res['lng'], res['lat'])
  if 'locality' in types and 'political' in types and precision == 'CITY':
    return name_en, center, place_id
  else:
    print state_name, name, query
    return None, None, None

if __name__ == '__main__':
  path = sys.argv[1]
  paths = os.listdir(path)
  for p in paths:
    m = {}
    for c in CITY_LIST:
      m[c] = []
    if p.endswith("geojson"):
      full_name = path + p
      f = open(full_name, 'rb')
      s = json.loads(f.read())
      n_features = []
      state_name = None
      state_guid = None
      for f in s['features']:
        state_name = f['properties']['state_name']
        state_guid = f['properties']['state_guid']
        is_merged = False
        for c in CITY_LIST:
          if c in f['properties']['full_name']:
            if f['geometry']['type'] == 'MultiPolygon':
              m[c].extend(f['geometry']['coordinates'])
            elif f['geometry']['type'] == 'Polygon':
              m[c].append(f['geometry']['coordinates'])
            is_merged = True
            break
        if not is_merged:
          n_features.append(f)
      s['features'] = n_features
      for k, v in m.items():
        if not v:
          continue
        query = "%s, %s, Japan" % (k, state_name)
        print query
        name_en, center, place_id = geo_result(state_name, k, query)
        feature = {"geometry":{}, "properties": {}}
        feature['geometry']['type'] = 'MultiPolygon'
        feature['geometry']['coordinates'] = v
        feature['type'] = "Feature"
        feature['properties']['full_name'] = k
        feature['properties']['state_guid'] = state_guid
        feature['properties']['state_name'] = state_name
        feature['properties']['center'] = center
        feature['properties']['place_id'] = place_id
        feature['properties']['query'] = query
        feature['properties']['name_en'] = name_en
        if not name_en:
          print json.dumps(feature['properties'], encoding="UTF-8", ensure_ascii=False).encode('utf-8')
        s['features'].append(feature)
      ff = open("./%s" % p, 'wb')
      ff.write(json.dumps(s, encoding="UTF-8", ensure_ascii=False).encode('utf-8'))
      ff.flush()
      ff.close()



