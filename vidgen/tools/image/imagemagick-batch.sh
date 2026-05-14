#!/usr/bin/env bash
# imagemagick-batch — common image ops via ImageMagick.
#
# Usage:
#   imagemagick-batch.sh resize <input> <output> <WxH>
#   imagemagick-batch.sh to-bw <input> <output>
#   imagemagick-batch.sh blur <input> <output> <radius>
#   imagemagick-batch.sh padded-square <input> <output> <size> <bg_hex>

set -euo pipefail

CMD="${1:-}"; shift || true

if ! command -v magick &>/dev/null; then
  echo "ERROR: ImageMagick (magick) not installed. brew install imagemagick"
  exit 1
fi

case "$CMD" in
  resize)
    [ "$#" -ge 3 ] || { echo "Usage: resize <input> <output> <WxH>"; exit 1; }
    magick "$1" -resize "$3" "$2"
    ;;
  to-bw)
    [ "$#" -ge 2 ] || { echo "Usage: to-bw <input> <output>"; exit 1; }
    magick "$1" -colorspace Gray "$2"
    ;;
  blur)
    [ "$#" -ge 3 ] || { echo "Usage: blur <input> <output> <radius>"; exit 1; }
    magick "$1" -blur "0x$3" "$2"
    ;;
  padded-square)
    [ "$#" -ge 4 ] || { echo "Usage: padded-square <input> <output> <size> <bg_hex>"; exit 1; }
    magick "$1" -resize "${3}x${3}" -background "$4" -gravity center -extent "${3}x${3}" "$2"
    ;;
  *)
    echo "Commands: resize | to-bw | blur | padded-square"
    exit 1
    ;;
esac

echo "OK: $2"
