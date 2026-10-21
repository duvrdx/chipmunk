from osgeo import gdal, osr

OAMS_TRADITIONAL = osr.OAMS_TRADITIONAL_GIS_ORDER


def _to_sr(crs):
    if isinstance(crs, osr.SpatialReference) or hasattr(crs, 'ExportToWkt'):
        crs.SetAxisMappingStrategy(OAMS_TRADITIONAL)
        return crs
    code = crs
    if code.upper().startswith("EPSG:"):
        code = code[5:]
    sr = osr.SpatialReference()
    sr.ImportFromEPSG(int(code))
    sr.SetAxisMappingStrategy(OAMS_TRADITIONAL)
    return sr


def extract_raster_crs(raster_path):
    ds = gdal.Open(raster_path)
    if ds is None:
        raise RuntimeError(f"Cannot open raster: {raster_path}")
    wkt = ds.GetProjection()
    if not wkt:
        raise RuntimeError(f"Raster has no CRS: {raster_path}")
    sr = osr.SpatialReference()
    sr.ImportFromWkt(wkt)
    sr.SetAxisMappingStrategy(OAMS_TRADITIONAL)
    return sr


def coord_transform(src_crs, dst_crs):
    src = _to_sr(src_crs)
    dst = _to_sr(dst_crs)
    return osr.CoordinateTransformation(src, dst)


def transform_bbox(bbox, src_crs, dst_crs):
    ct = coord_transform(src_crs, dst_crs)
    xmin, ymin, xmax, ymax = bbox
    corners = [
        ct.TransformPoint(xmin, ymin),
        ct.TransformPoint(xmax, ymin),
        ct.TransformPoint(xmin, ymax),
        ct.TransformPoint(xmax, ymax),
    ]
    xs = [c[0] for c in corners]
    ys = [c[1] for c in corners]
    return (min(xs), min(ys), max(xs), max(ys))
