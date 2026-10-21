#!/usr/bin/env bash
set -euo pipefail

POINTS="/c/Users/duvrd/Documents/doce_river_points.shp"
CBERS_DIR="/c/Users/duvrd/Documents/Mestrado/DOCE_CBERS"
OUTPUT_DIR="./dataset/doce_river2"
WMS_URL="https://ide.geobases.es.gov.br/geoserver/ows"
WMS_LAYER="geonode:ijsn_map_uso_solo_es_2019_20200"

# config
POINTS_CRS="EPSG:4326"
OUTPUT_CRS="EPSG:31984"
WIDTH_M=2500
HEIGHT_M=2500
OUT_W=512
OUT_H=512
FIELD="id"
DELAY=0.3
SKIP="--skip-existing"

run() {
  echo ""
  echo ">>> $1"
  shift
  uv run chipmunk "$@" --log "$OUTPUT_DIR/chipmunk.log"
}

mkdir -p "$OUTPUT_DIR"

for raster in "$CBERS_DIR"/CBERS_*_BAND*.tif; do
  band=$(basename "$raster" | sed -E 's/.*_BAND([0-9]+)\.tif/BAND\1/')
  run "Crop $band ($(basename "$raster"))" \
    --mode raster \
    --points "$POINTS" \
    --points-crs "$POINTS_CRS" \
    --output-crs "$OUTPUT_CRS" \
    --raster "$raster" \
    --folder "$OUTPUT_DIR/bands/$band" \
    --width-m "$WIDTH_M" --height-m "$HEIGHT_M" \
    --output-width "$OUT_W" --output-height "$OUT_H" \
    --field "$FIELD" \
    $SKIP
done

run "Ground truth (WMS $WMS_LAYER)" \
  --mode wms-http \
  --points "$POINTS" \
  --points-crs "$POINTS_CRS" \
  --output-crs "$OUTPUT_CRS" \
  --folder "$OUTPUT_DIR/groundtruth" \
  --width-m "$WIDTH_M" --height-m "$HEIGHT_M" \
  --output-width "$OUT_W" --output-height "$OUT_H" \
  --field "$FIELD" \
  --wms-url "$WMS_URL" \
  --wms-layers "$WMS_LAYER" \
  --wms-version 1.3.0 \
  --wms-delay "$DELAY" \
  $SKIP

echo ""
echo "Dataset structure:"
echo "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 2 -type d | sort | head -20
echo "Chips por banda: $(ls "$OUTPUT_DIR"/bands/* | head -1 | xargs -I{} dirname {} | xargs -I{} ls {} | wc -l)"
