import sys

try:
    from osgeo import gdal, ogr  # noqa: F401
except ImportError:
    print("Error: GDAL (osgeo) not found.", file=sys.stderr)
    print("  Install system package: apt install python3-gdal", file=sys.stderr)
    print("  Or via conda:           conda install gdal", file=sys.stderr)
    sys.exit(1)


from .cli import main

main()
