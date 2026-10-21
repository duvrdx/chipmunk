#!/usr/bin/env bash
set -euo pipefail

POINTS="/c/Users/duvrd/Documents/itapemirim_river_points.shp"
OUTPUT_DIR="./dataset/hydro_itapemirim"
WMS_URL="https://ide.geobases.es.gov.br/geoserver/ows"
WMS_LAYER="geonode:agerh_cursos_dagua_es_q90"

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

run "Hidrografia (WMS $WMS_LAYER)" \
  --mode wms-http \
  --points "$POINTS" \
  --points-crs "$POINTS_CRS" \
  --output-crs "$OUTPUT_CRS" \
  --folder "$OUTPUT_DIR/hidrografia" \
  --width-m "$WIDTH_M" --height-m "$HEIGHT_M" \
  --output-width "$OUT_W" --output-height "$OUT_H" \
  --field "$FIELD" \
  --wms-url "$WMS_URL" \
  --wms-layers "$WMS_LAYER" \
  --wms-version 1.3.0 \
  --wms-delay "$DELAY" \
  $SKIP

echo ""
echo "Hydrography dataset structure:"
echo "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 2 -type d | sort | head -20
echo "Chips de hidrografia: $(ls "$OUTPUT_DIR/hidrografia" | wc -l)"
