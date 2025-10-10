"""Command-line interface for deppth functionality"""
import os
import argparse
import sys

from .deppth import list_contents, pack, patch, extract
from .texpacking import build_atlases_hades

def main():
    parser = argparse.ArgumentParser(prog='deppth', description='Decompress, Extract, Pack for Pyre, Transistor, and Hades')
    subparsers = parser.add_subparsers(help='The action to perform', dest='action')

    # List parser
    list_parser = subparsers.add_parser('list', help='List the entries of a package', aliases=['ls'])
    list_parser.add_argument('path', metavar='path', type=str, help='The path to the package to act on')
    list_parser.add_argument('patterns', metavar='pattern', nargs='*', help='Patterns to search for')
    list_parser.set_defaults(func=cli_list)

    # Extract parser
    extract_parser = subparsers.add_parser('extract', help='Extract assets from a package', aliases=['ex'])
    extract_parser.add_argument('source', metavar='source', type=str, help='The path to extract')
    extract_parser.add_argument('-t', '--target', metavar='target', default='', help='Where to extract the package')
    extract_parser.add_argument('-e', '--entries', nargs='*', metavar='entry', help='One or more entry names to extract')
    extract_parser.add_argument('-s', '--subtextures', action='store_true', default=False, help='Export subtextures instead of full atlases')
    extract_parser.set_defaults(func=cli_extract)

    # Pack parser
    pack_parser = subparsers.add_parser('pack', help='Pack assets into a package', aliases=['pk'])
    pack_parser.add_argument('-s', '--source', metavar='source', default='', type=str, help='Path to the folder to pack, default is current folder')
    pack_parser.add_argument('-t', '--target', metavar='target', default='', help='Path of output file')
    pack_parser.add_argument('-e', '--entries', nargs='*', metavar='entry', help='Only pack entries matching these patterns')
    pack_parser.add_argument('-c', '--codec', metavar='codec', default='RGBA', help='Specify the image codec to use for packing, default is RGBA, often used is BC7 because of max chunk size being 32MB')
    pack_parser.set_defaults(func=cli_pack)

    # Patch parser
    patch_parser = subparsers.add_parser('patch', help='Patch a package, replacing or adding entries from patches', aliases=['pt'])
    patch_parser.add_argument('package', metavar='package', type=str, help='The package to patch')
    patch_parser.add_argument('patches', metavar='patches', nargs='*', help='The patches to apply')
    patch_parser.set_defaults(func=cli_patch)

    # Pack textures
    hadespack_parser = subparsers.add_parser('hadespack', help='Format images into an atlas and manifest for packing with deppth', aliases=['hpk'])
    hadespack_parser.add_argument('-s', '--source', metavar='source', default='MyPackage', type=str, help='The directory to recursively search for images in, default is current folder')
    hadespack_parser.add_argument('-t', '--target', metavar='target', default='ThunderstoreTeamName-MyPackage', help='Filenames created will start with this plus a number')
    hadespack_parser.add_argument('-c', '--codec', metavar='codec', default = "RGBA", help='Specify the image codec to use for packing, default is RGBA, often used is BC7 because of max chunk size being 32MB')
    hadespack_parser.add_argument('-dP', '--deppthpack', metavar='deppthpack', default='True', help='Automatically Pack your images and Manifest using deppth')
    hadespack_parser.add_argument('-iH', '--includehulls', metavar='includehulls', default = "False", help='Set to anything if you want hull points computed and added')
    hadespack_parser.set_defaults(func=cli_hadespack)

    args = parser.parse_args()

    # Print help if no arguments were provided
    if not hasattr(args, 'func'):
        parser.print_help()
        sys.exit(1)

    args.func(args)

def cli_list(args):
    path = args.path
    patterns = args.patterns

    list_contents(path, *patterns, logger=lambda s: print(s))

def cli_extract(args):
    source = args.source
    target = args.target
    entries = args.entries or []
    subtextures = args.subtextures

    extract(source, target, *entries, subtextures=subtextures, logger=lambda s: print(s))

def cli_pack(args):
    curdir = os.getcwd()
    source = os.path.join(curdir, args.source)
    target = args.target
    entries = args.entries or []
    codec = args.codec

    pack(source, target, *entries, logger=lambda s: print(s), codec=codec)

def cli_hadespack(args):
    source = args.source
    target = args.target
    codec = args.codec

    deppth = True
    if args.deppthpack != "True":
        deppth = False

    hulls = False
    if args.includehulls != "False":
        hulls = True

    build_atlases_hades(source, target, deppth, hulls, codec=codec)

def cli_patch(args):
    package = args.package
    patches = args.patches
    patch(package, *patches, logger=lambda s : print(s))