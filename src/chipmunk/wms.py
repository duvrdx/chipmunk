import time

import requests


def download_wms_tile(url, layers, bbox, crs, width, height,
                      fmt="image/png", version="1.3.0", retries=5,
                      retry_delay=2.0):
    xmin, ymin, xmax, ymax = bbox

    # WMS 1.3.0: axis order depends on CRS
    # For geographic (EPSG:4326): bbox=latmin,lonmin,latmax,lonmax
    # For projected (UTM): bbox=xmin,ymin,xmax,ymax
    # We send xmin,ymin,xmax,ymax — works for projected CRS in 1.3.0
    bbox_str = f"{xmin},{ymin},{xmax},{ymax}"

    params = {
        "SERVICE": "WMS",
        "VERSION": version,
        "REQUEST": "GetMap",
        "LAYERS": layers,
        "STYLES": "",
        "CRS": crs,
        "BBOX": bbox_str,
        "WIDTH": width,
        "HEIGHT": height,
        "FORMAT": fmt,
        "TRANSPARENT": "TRUE",
    }

    last_err = None
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=120)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            last_err = e
            if attempt < retries - 1:
                time.sleep(retry_delay * (attempt + 1))
    raise last_err


def write_tfw(tfw_path, bbox, width, height):
    xmin, ymin, xmax, ymax = bbox
    pixel_size_x = (xmax - xmin) / width
    pixel_size_y = (ymax - ymin) / height
    x_ul = xmin + pixel_size_x / 2.0
    y_ul = ymax - pixel_size_y / 2.0

    with open(tfw_path, "w") as f:
        f.write(f"{pixel_size_x}\n")
        f.write("0.0\n")
        f.write("0.0\n")
        f.write(f"{-pixel_size_y}\n")
        f.write(f"{x_ul}\n")
        f.write(f"{y_ul}\n")
