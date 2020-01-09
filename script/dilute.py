import json
import sys

if __name__ == '__main__':
  fn = sys.argv[1]
  reso = int(sys.argv[2])
  if reso < 2:
    sys.exit(0)
  f = open(fn, 'rb')
  s = json.loads(f.read())
  features = []
  for fe in s['features']:
    coords = fe['geometry']['coordinates']
    new_coords = []
    if fe['geometry']['type'] == 'Polygon':
      for linering in coords:
        if len(linering) < 40:
          new_coords.append(linering)
          continue
        nl = []
        for idx, coord in enumerate(linering):
          if idx % reso == 0:
            nl.append(coord)
        if nl[0] != nl[-1]:
          nl.append(nl[0])
        new_coords.append(nl)
    elif fe['geometry']['type'] == 'MultiPolygon':
      for polygon in coords:
        np = []
        for linering in polygon:
          if len(linering) < 20:
            np.append(linering)
            continue
          nl = []
          for idx, coord in enumerate(linering):
            if idx % reso == 0:
              nl.append(coord)
          if nl[0] != nl[-1]:
            nl.append(nl[0])
          np.append(nl)
        new_coords.append(np)
    print new_coords
    fe['geometry']['coordinates'] = new_coords

    tf = open("./tf.geojson", 'wb')
    tf.write(json.dumps(s))
    tf.flush()
    tf.close()
