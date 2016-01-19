# Optimize MBTiles

If you are using tilelive and a tile server which supports `maskLevel`
you can remove save a lot of redundant data by backfilling missing high zoom
levels with data from low zoom levels.

## Install

You need **Python 2** installed on your system due to limitations of [mbutil](https://github.com/mapbox/mbutil).

```bash
git clone https://github.com/lukasmartinelli/optimize-mbtiles.git
cd optimize-mbtiles
pip install -r requirements.txt
```

## Usage

```bash
Usage:
  optimize.py check <mbtiles_file> -z=<mask_level> [--scheme=<scheme>]
  optimize.py (-h | --help)
  optimize.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -z=<mask_level>           Minimum zoom level where data should still exist
  --scheme=<scheme>         Tiling scheme of the tiles can be either xyz or tms [default: tms]
```

## Theory

### Mask Level

[tilelive-vector]() supports the powerful concept of mask level.

> To avoid requiring many duplicate or empty vector tiles to be generated at high zoom levels,
  the backend source can specify a `maskLevel`.
  If a vector tile is not initially found at some `z > maskLevel`, Vector will issue an additional request
  to the backend using the parent tile of of the request at `maskLevel`.
  This allows a lower zoom level to backfill high zoom levels.

### Example

If each descendant tile in the entire subpyramid `8/100/101` has the same binary
data as `8/100/101` we can remove all descendants. A request to `9/200/202` will
then receive the data from `8/100/101` without the need of duplicating the data
across multiple zoom levels.

![Subpyramid](subpyramid.png)
