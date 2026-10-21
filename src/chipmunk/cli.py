import argparse
import sys
import os


def build_parser():
    p = argparse.ArgumentParser(
        prog="chipmunk",
        description="Crop geo-referenced raster chips from point samples.",
    )
    p.add_argument("--mode", required=True, choices=["raster", "wms-http"],
                   help="raster: crop local file | wms-http: fetch via WMS GetMap")
    p.add_argument("--points", required=True, help="Path to input Shapefile")
    p.add_argument("--folder", required=True, help="Output directory")
    p.add_argument("--points-crs", required=True,
                   help="CRS of input points, e.g. EPSG:4674")
    p.add_argument("--output-crs", required=True,
                   help="Target CRS, e.g. EPSG:32723")
    p.add_argument("--width-m", type=float, required=True,
                   help="Crop width in meters")
    p.add_argument("--height-m", type=float, required=True,
                   help="Crop height in meters")
    p.add_argument("--output-width", type=int, default=400,
                   help="Output width in pixels (default: 400)")
    p.add_argument("--output-height", type=int, default=400,
                   help="Output height in pixels (default: 400)")
    p.add_argument(
        "--field", help="Attribute field to use as output filename (optional)")
    p.add_argument("--skip-existing", action="store_true",
                   help="Skip points whose output file already exists (resume support)")
    p.add_argument("--resample", default="near", choices=["near", "cubic", "lanczos", "bilinear"],
                   help="GDAL resampling method for raster mode (default: near)")
    p.add_argument("--log", help="Path to log file (optional)")

    p.add_argument("--raster", help="Path to input raster file (raster mode)")
    p.add_argument(
        "--raster-crs", help="CRS of raster file, auto-detected if omitted")

    p.add_argument("--wms-url", help="WMS GetCapabilities URL")
    p.add_argument("--wms-layers", help="Comma-separated WMS layer names")
    p.add_argument("--wms-version", default="1.3.0",
                   help="WMS version (default: 1.3.0)")
    p.add_argument("--wms-format", default="image/png",
                   help="WMS image format (default: image/png)")
    p.add_argument("--wms-delay", type=float, default=0,
                   help="Seconds between WMS requests")

    return p


def validate_args(args):
    errors = []
    if not os.path.isfile(args.points):
        errors.append(f"Points file not found: {args.points}")

    if args.mode == "raster":
        if not args.raster:
            errors.append("--raster is required in raster mode")
        elif not os.path.isfile(args.raster):
            errors.append(f"Raster file not found: {args.raster}")

    elif args.mode == "wms-http":
        if not args.wms_url:
            errors.append("--wms-url is required in wms-http mode")
        if not args.wms_layers:
            errors.append("--wms-layers is required in wms-http mode")

    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    try:
        from osgeo import gdal, ogr  # noqa: F401
    except ImportError:
        print("Error: GDAL (osgeo) not found.", file=sys.stderr)
        print("  Install system package: apt install python3-gdal", file=sys.stderr)
        print("  Or via conda:           conda install gdal", file=sys.stderr)
        sys.exit(1)

    from .cropper import process_points
    from .crs import extract_raster_crs
    from .utils import setup_logger

    parser = build_parser()
    args = parser.parse_args()
    validate_args(args)

    logger = setup_logger(args.log)

    raster_crs = None
    if args.mode == "raster":
        raster_crs = args.raster_crs or extract_raster_crs(args.raster)

    process_points(
        points_path=args.points,
        output_folder=args.folder,
        filename_field=args.field,
        points_crs=args.points_crs,
        output_crs=args.output_crs,
        width_m=args.width_m,
        height_m=args.height_m,
        output_width=args.output_width,
        output_height=args.output_height,
        mode=args.mode,
        raster_path=args.raster,
        raster_crs=raster_crs,
        resample=args.resample,
        wms_url=args.wms_url,
        wms_layers=args.wms_layers,
        wms_version=args.wms_version,
        wms_format=args.wms_format,
        wms_delay=args.wms_delay,
        skip_existing=args.skip_existing,
        logger=logger,
    )


if __name__ == "__main__":
    main()
