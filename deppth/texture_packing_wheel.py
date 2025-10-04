from pathlib import Path
from PIL import Image
from deppth.texpacking import get_hull_points, transform_hull
from deppth.entries import AtlasEntry
import json
import os
import shutil
import re
from .deppth import pack

# To use this script, you'll need to pip install scipy and PyTexturePacker in addition to deppth and pillow

def build_atlases(source_dir, target_dir, deppth_pack=True, include_hulls=False, logger=lambda s: None, codec='RGBA'):
  """
    Build texture atlases from images within a source directory.

    Args:
        source_dir (str): The root directory to recursively search for images.
        target_dir (str): The target directory where the atlases will be saved. The atlases filenames will be named after the target directory name. The .pkg file too. (If created)
        deppth_pack (bool, optional): If True, automatically call pack for putting the built atlases into a SGG .pkg file. Defaults to True.
        include_hulls (bool, optional): If True, computes convex hull points of images 
                                        and includes them in the atlas data. Defaults to False.
        logger (callable, optional): A logging function that accepts a single string argument.
                                     Defaults to a no-op (does nothing).

    Returns:
        None
  """
  
  try:
    import scipy
    import PyTexturePacker
    import PIL
  except ImportError as e:
    print("This function requires the scipy, PyTexturePacker and pillow packages. Please install them with pip.")
    return

  print(target_dir)
  basename = os.path.splitext(os.path.basename(target_dir))[0]
  print(basename)

  # Regex check to make sure user inserts a mod guid type basename
  regexpattern = r"^[a-z0-9]+(\w+[a-z0-9])?-\w+$"
  
  if re.match(regexpattern, basename, flags=re.I|re.A):
    pass
  else:
    print("Please provide a target with your mod guid, example ThunderstoreTeamName-Modname")
    return

  if os.path.isdir(target_dir) == True:
    print(f"Target directory {target_dir} already exists, deleting it.")
    shutil.rmtree(target_dir)
    
  os.mkdir(target_dir, 0o666)
  os.mkdir(os.path.join(target_dir, "manifest"), 0o666)
  os.mkdir(os.path.join(target_dir, "textures"), 0o666)
  os.mkdir(os.path.join(target_dir, "textures", "atlases"), 0o666)

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
  packer = PyTexturePacker.Packer.create(max_width=2880, max_height=2880, bg_color=0x00000000, atlas_format='json', 
  enable_rotated=False, trim_mode=1, border_padding=0, shape_padding=0)
  packer.pack(files, f'{basename}%d')
  
  # Now, loop through the atlases made and transform them to be the right format
  index = 0
  atlases = []
  manifest_paths = [] # Manifest Path Start
  while os.path.exists(f'{basename}{index}.json'):
    atlases.append(transform_atlas(target_dir, basename, f'{basename}{index}.json', namemap, hulls, source_dir, manifest_paths))
    os.remove(f'{basename}{index}.json')
    index += 1
  
  # Now, loop through the atlas images made and move them to the package folder
  index = 0
  while os.path.exists(f'{basename}{index}.png') or os.path.exists(f'{basename}{index}.dds'):
    try:
      os.rename(f'{basename}{index}.png', os.path.join(target_dir, "textures", "atlases", f'{basename}{index}.png'))
    except:
      pass
    try:
      os.rename(f'{basename}{index}.dds', os.path.join(target_dir, "textures", "atlases", f'{basename}{index}.dds'))
    except:
      pass
    index += 1

    # Create the packages
    if deppth_pack:
      pack(target_dir, f'{target_dir}.pkg', *[], logger=lambda s: print(s), codec=codec)

    # print the manifest paths, so its easy to see the game path
    print("\nManifest Paths - Use in Codebase:")
    for path in manifest_paths:
        print(path, "\n")


def find_files(source_dir):
  file_list = []
  for path in Path(source_dir).rglob('*.png'):
    file_list.append(path)
  for path in Path(source_dir).rglob('*.dds'):
    file_list.append(path)
  return file_list

def transform_atlas(target_dir, basename, filename, namemap, hulls={}, source_dir='', manifest_paths=[]):
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

  os.rename(f'{os.path.splitext(filename)[0]}.atlas.json', os.path.join(target_dir, "manifest", f'{os.path.splitext(filename)[0]}.atlas.json'))
  return atlas
