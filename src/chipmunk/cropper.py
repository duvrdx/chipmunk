import os
import time
import math

from osgeo import gdal, ogr

from .crs import coord_transform, transform_bbox
from .wms import download_wms_tile, write_tfw
from .utils import sanitize_name

gdal.UseExceptions()


def build_bbox(cx, cy, w, h):
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)


def crop_raster(raster_path, bbox, output_path, raster_crs_str, output_crs_str,
                width_px, height_px, resample):
    bbox_raster = transform_bbox(bbox, output_crs_str, raster_crs_str)
    xmin, ymin, xmax, ymax = bbox_raster

    gdal.Translate(
        destName=output_path,
        srcDS=raster_path,
        projWin=[xmin, ymax, xmax, ymin],
        outputSRS=output_crs_str,
        width=width_px,
        height=height_px,
        resampleAlg=resample,
        format="GTiff",
        creationOptions=["COMPRESS=LZW"],
    )


def process_points(points_path, output_folder, filename_field,
                   points_crs, output_crs,
                   width_m, height_m,
                   output_width, output_height,
                   mode, logger, skip_existing=False,
                   raster_path=None, raster_crs=None, resample="near",
                   wms_url=None, wms_layers=None, wms_version="1.3.0",
                   wms_format="image/png", wms_delay=0):

    os.makedirs(output_folder, exist_ok=True)
    ct = coord_transform(points_crs, output_crs)

    ds = ogr.Open(points_path)
    if ds is None:
        raise RuntimeError(f"Cannot open shapefile: {points_path}")
    layer = ds.GetLayer()
    total = layer.GetFeatureCount()

    if filename_field:
        layer_defn = layer.GetLayerDefn()
        field_names = [layer_defn.GetFieldDefn(i).GetName() for i in range(layer_defn.GetFieldCount())]
        if filename_field not in field_names:
            logger.warning(f"Field '{filename_field}' not found. Using sample_NNN naming.")
            filename_field = None

    # count digits for zero-padding
    ndigits = max(3, len(str(total)))

    success = 0
    errors_list = []

    for i, feat in enumerate(layer):
        geom = feat.GetGeometryRef()
        centroid = geom.Centroid()
        cx, cy, _ = ct.TransformPoint(centroid.GetX(), centroid.GetY())

        bbox = build_bbox(cx, cy, width_m, height_m)

        if filename_field:
            raw = feat.GetField(filename_field)
            name = sanitize_name(str(raw)) if raw else f"sample_{i+1:0{ndigits}d}"
        else:
            name = f"sample_{i+1:0{ndigits}d}"

        output_path = os.path.join(output_folder, f"{name}.tif")

        if skip_existing and os.path.exists(output_path):
            logger.info(f"[{i+1}/{total}] SKIP {name}.tif (exists)")
            success += 1
            continue

        try:
            if mode == "raster":
                crop_raster(
                    raster_path=raster_path,
                    bbox=bbox,
                    output_path=output_path,
                    raster_crs_str=raster_crs,
                    output_crs_str=output_crs,
                    width_px=output_width,
                    height_px=output_height,
                    resample=resample,
                )
            elif mode == "wms-http":
                img_data = download_wms_tile(
                    url=wms_url,
                    layers=wms_layers,
                    bbox=bbox,
                    crs=output_crs,
                    width=output_width,
                    height=output_height,
                    fmt=wms_format,
                    version=wms_version,
                )
                with open(output_path, "wb") as f:
                    f.write(img_data)
                tfw_path = os.path.splitext(output_path)[0] + ".tfw"
                write_tfw(tfw_path, bbox, output_width, output_height)

            success += 1
            logger.info(f"[{i+1}/{total}] OK  {name}.tif")

        except Exception as e:
            msg = f"[{i+1}/{total}] FAIL {name}.tif: {e}"
            logger.error(msg)
            errors_list.append(msg)

        if mode == "wms-http" and wms_delay > 0:
            time.sleep(wms_delay)

    logger.info(f"Done: {success}/{total} OK")
    if errors_list:
        for e in errors_list:
            logger.error(e)

    ds = None
