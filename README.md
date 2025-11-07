# deppth2
Decompress, Extract, and Pack for Pyre, Transistor, Hades and Hades 2.

Deppth2 is a high-level I/O interface for package files in the games Transistor, Pyre, Hades and Hades 2. Deppth provides both command-line and programmer interfaces.

## Installation

To install Deppth2, `pip install deppth2` or download the latest [wheel](https://github.com/SGG-Modding/deppth/releases) and `pip install` it. Then read the following instructions to install dependencies.

### Dependencies

Deppth2 technically has two required dependencies, `pillow` and `lz4`, as they are the primary tools that deppth2 uses. If an optional dependency is missing, Deppth2 will abort an operation dependent on that module informing you of the missing module.

> As packages primarily contain sprite sheets, deppth2 uses Pillow to work with the image data within. <br>
> Hades/Hades 2 uses LZ4 compression on its packages, and as such, lz4 is automatically installed to allow for deppth2 to work with Hades/Hades 2.

Transistor and Pyre both use LZF compression on their packages. If you plan to work with these packages, you'll want to install the LZF module: `pip install lzf`. You may need to install C++ build tools to get this dependency to install correctly.

## CLI Quick-Start

Let's say we want to edit a spritesheet in Launch.pkg. First, we'll want to **extract** the package to get the individual assets out.

    deppth2 ex Launch.pkg

This will create a folder called Launch in the current working directory. The texture atlases will be in the textures/atlases directory within there.

Let's say I edit Launch_Textures02.png. Now, to rebuild the package, I'll want to **pack** this folder into a package again.

    deppth2 pk -s Launch -t Launch.pkg

If I then replace the package file in the game files with this package file, it should use my updated asset. But, suppose I'm trying to distribute a mod. I probably only want to distribute my change to the package, not the entire package. In that case, you probably want to build a patch for someone else to apply.

To do this, you can use the **pack** command with the **entries** flag to only include any items you changed (this works similar to patterns in other CLI tools).

    deppth2 pk -s Launch -t Launch_patch.pkg -e *Launch_Textures02*

I can then distribute Launch_patch.pkg and Launch_patch.pkg_manifest. To apply this patch to the actual package, one would need to place these files in the same folder and then use the **patch** command to perform the patching. 

    deppth2 pt Launch.pkg Launch_patch.pkg

This will replace any entries in the package with any matching entries in the patches and append any new entries in the patches. More than one patch can be applied at a time (later ones take precedence if there are conflicts).

## Deppth2 API

The Deppth2 module exposes functions that perform the actions described above, plus a fourth (which is also part of the CLI) to list the contents of a package. It's basically just a programmer interface for the same things the CLI does -- the latter is just a wrapper for the former.
```py
    list(name, *patterns, logger=lambda  s: None)
    extract(package, target_dir, *entries, subtextures=False, logger=lambda  s: None)
    pack(source_dir, package, *entries, logger=lambda  s: None)
    patch(name, *patches, logger=lambda  s : None)
```

The logger kwarg allows for customization of output of these functions -- for example, you may want to write to a file instead of print to screen.

## SGGPIO

The SGGPIO module is a lower-level interface for working with packages. The aim is to provide IO-esque streams to read and write package data. Most users won't need this, but for certain applications, using it could lead to better performance or more customizable behavior.

SGGPIO exports two functions, which really just wrap functionality in a variety of reader and writer classes. I recommend reading the docs on these classes if you're interested, but basic usage looks something like this.

    from deppth import sggpio

    # Copy Launch.pkg and corresponding manifest
    with sggpio.open_package('Launch.pkg', 'rm') as pkg:
	    with sggpio.open_package('Launch_copy.pkg', 'wm') as pkg_out:
		    for entry in pkg:
			    pkg_out.write_entry_with_manifest(entry)
	
	# Print manifest contents of copy to verify success
	with sggpio.open_package('Launch_copy.pkg', 'rm') as pkg:
		for entry in pkg.manifest:
			print(entry)

## Hades 2 Packing CLI Quick-Start

In order to pack your `.png` files to be used in Hades II, open the CLI in the parent folder containing the images you want to pack.
For example, here is a directory tree.

```
├ <deppth command line open here> 
├── NewDeppthPackage
│   ├── GUI
│   │   ├── image1.png
│   │   ├── image2.png
│   │   ├── image3.png
│   │   │ Icons
│   │   │   ├── Iconimage.png
```

Using the command line in order to create your package for your mod, the package name must include the ``Mod-GUID`` (ThunderstoreTeamName-ModName) in order to work with Hell2Modding.

    deppth2 hpk -s NewDeppthPackage -t ThunderstoreTeamName-NewIconPackage

This will generate a folder called ThunderstoreTeamName-NewIconPackage in the parent directory that will be correctly formatted for deppth2 packaging, as well as 2 package files to use for your mod.

This will also generate the paths needed to be used in the game.

```
ThunderstoreTeamName-NewIconPackage/GUI/image1.png
ThunderstoreTeamName-NewIconPackage/GUI/image2.png
ThunderstoreTeamName-NewIconPackage/GUI/image3.png
and
ThunderstoreTeamName-NewIconPackage/GUI/Icons/Iconimage.png
```

All image file paths will follow the file path inside the folder they were originally in, plus the package name appended to the start of it - in order to work with Hell2Modding.\
For example, if the package was in the folder by itself its file path in-game would just be the ``ThunderstoreTeamName-NewIconPackage\\{Name}``, but if its path was `NewIconPkg/GUI/Icons` then its file path in-game would be `ThunderstoreTeamName-NewIconPackage\\GUI\\Icons\\{Name}`

### Args

    -s or --source is the name of the folder in which to recursively search for images
    -t or --target is the name of the resulting folder to be packed by deppth2, must be in the form of a mod GUID (ModAuthor-ModName).
    -c or --codec is to specify the image codec to use for packing, default is RGBA, often used is BC7 because of max chunk size being 32MB.
    -dp or --deppthpack (not used above) set to anything but "True" to disable automatic Deppth2 Packing.
    -iH or --includehulls (not used above) set to anything but "False" to calculate hull points.