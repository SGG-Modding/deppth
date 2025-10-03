from pathlib import Path
from PyTexturePacker import Packer
from PIL import Image
from scipy.spatial import ConvexHull
from deppth.entries import AtlasEntry
import json
import os
import shutil
import re

# To use this script, you'll need to pip install scipy and PyTexturePacker in addition to deppth and pillow

SOURCE_DIRECTORY = 'Example_'       # The directory to recursively search for images in
BASENAME = 'Example'                # Filenames created will start with this plus a number
DEPPTH_PACK = True                  # Change to False if you don't want to automatically pack
INCLUDE_HULLS = False               # Change to True if you want hull points computed and added

def build_atlases(source_dir, basename, deppth_pack=True, include_hulls=False, logger=lambda s: None):
  # Regex check to make sure user inserts a mod guid type basename
  regexpattern = r"^[a-z0-9]+(\w+[a-z0-9])?-\w+$"
  
  if re.match(regexpattern, basename, flags=re.I|re.A):
    pass
  else:
    print("Please provide a target with your mod guid, example ThunderstoreTeamName-Modname")
    return

  if os.path.isdir(basename) == True:
    shutil.rmtree(basename)
    
  os.mkdir(basename, 0o666)
  os.mkdir(basename + "\\manifest", 0o666)
  os.mkdir(basename + "\\textures", 0o666)
  os.mkdir(basename + "\\textures\\atlases", 0o666)

  files = find_files(source_dir)
  hulls = {}
  namemap = {}
  for filename in files:
    # Build hulls for each image so we can store them later
    if include_hulls:
      hulls[filename.name] = get_hull_points(filename)
    else:
      hulls[filename.name] = []
    namemap[filename.name] = str(filename)

  # Perfom the packing. This will create the spritesheets and primitive atlases, which we'll need to turn to usable ones
  packer = Packer.create(max_width=2880, max_height=2880, bg_color=0x00000000, atlas_format='json', 
  enable_rotated=False, trim_mode=1, border_padding=0, shape_padding=0)
  packer.pack(files, f'{basename}%d')
  

  # Now, loop through the atlases made and transform them to be the right format
  index = 0
  atlases = []
  manifest_paths = [] # Manifest Path Start
  while os.path.exists(f'{basename}{index}.json'):
    atlases.append(transform_atlas(basename, f'{basename}{index}.json', namemap, hulls, source_dir, manifest_paths))
    os.remove(f'{basename}{index}.json')
    index += 1
  
  # Now, loop through the pngs made and move them to the package folder
  index = 0
  while os.path.exists(f'{basename}{index}.png'):
    os.rename(f'{basename}{index}.png', basename + "\\textures\\atlases\\" + f'{basename}{index}.png')
    index += 1

    # Create the packages
    if deppth_pack:
      os.system(f'deppth pk -s {basename} -t {basename}.pkg')

    # print the manifest paths, so its easy to see the game path
    print("\nManifest Paths - Use in Codebase:")
    for path in manifest_paths:
        print(path, "\n")


def find_files(source_dir):
  file_list = []
  for path in Path(source_dir).rglob('*.png'):
    file_list.append(path)
  return file_list

def get_hull_points(path):
  im = Image.open(path)
  points = []

  width, height = im.size
  for x in range(width):
      for y in range(height):
          r,g,b,a = im.getpixel((x, y))
          if a > 4:
              points.append((x, y))

  if (len(points)) > 0:
    try:
      hull = ConvexHull(points)
    except:
      return [] # Even if there are points this can fail if e.g. all the points are in a line
    vertices = []
    for vertex in hull.vertices:
        x, y = points[vertex]
        vertices.append((x,y))
    
    return vertices
  else:
    return []

def transform_atlas(basename, filename, namemap, hulls={}, source_dir='', manifest_paths=[]):
  with open(filename) as f:
    ptp_atlas = json.load(f)
    frames = ptp_atlas['frames']
    atlas = AtlasEntry()
    atlas.version = 4
    atlas.name = f'bin\\Win\\Atlases\\{os.path.splitext(filename)[0]}'
    atlas.referencedTextureName = atlas.name
    atlas.isReference = True
    atlas.subAtlases = []

    for texture_name in frames:
      frame = frames[texture_name]
      subatlas = {}
      subatlas['name'] = os.path.join(basename, os.path.splitext(os.path.relpath(namemap[texture_name], source_dir))[0])
      manifest_paths.append(subatlas['name'])
      subatlas['topLeft'] = {'x': frame['spriteSourceSize']['x'], 'y': frame['spriteSourceSize']['y']}
      subatlas['originalSize'] = {'x': frame['sourceSize']['w'], 'y': frame['sourceSize']['h']}
      subatlas['rect'] = {
        'x': frame['frame']['x'],
        'y': frame['frame']['y'],
        'width': frame['frame']['w'],
        'height': frame['frame']['h']
      }
      subatlas['scaleRatio'] = {'x': 1.0, 'y': 1.0}
      subatlas['isMulti'] = False
      subatlas['isMip'] = False
      subatlas['isAlpha8'] = False
      subatlas['hull'] = transform_hull(hulls[texture_name], subatlas['topLeft'], (subatlas['rect']['width'], subatlas['rect']['height']))
      atlas.subAtlases.append(subatlas)

  atlas.export_file(f'{os.path.splitext(filename)[0]}.atlas.json')

  os.rename(f'{os.path.splitext(filename)[0]}.atlas.json', basename + "\\manifest\\" + f'{os.path.splitext(filename)[0]}.atlas.json')
  return atlas
    
def transform_hull(hull, topLeft, size):
  # There are two transforms to do. First, we need to subtract the topLeft offset values
  # to account for the shifting of the hull as the result of that.
  # Then, we need to subtract half the width and height from x and y of each point because
  # the hull values appear to be designed to be such that 0,0 is the center of the image, not
  # the top-left like most coordinate systems

  def transform_point(point):
    x = point[0] - topLeft['x'] - round(size[0]/2.0)
    y = point[1] - topLeft['y'] - round(size[1]/2.0)
    return {"x": x, "y": y}

  new_hull = []
  for point in hull:
    new_hull.append(transform_point(point))

  return new_hull