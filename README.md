# optimize-mbtiles [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/lukasmartinelli/optimize-mbtiles/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/lukasmartinelli/optimize-mbtiles/?branch=master) [![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](https://tldrlegal.com/license/mit-license)

If you are using [tilelive-vector](https://github.com/mapbox/tilelive-vector) or a tile server like [tileserver-php](https://github.com/klokantech/tileserver-php/) which supports `maskLevel`  you can **save a lot of redundant data in your MBTiles file** by backfilling missing high zoom levels with data from low zoom levels. This approach is used at [osm2vectortiles](github.com/osm2vectortiles/osm2vectortiles) to decrease the size of the MBTiles downloads.

## Install

You need **Python 2** installed on your system due to limitations of [mbutil](https://github.com/mapbox/mbutil).

```bash
git clone https://github.com/lukasmartinelli/optimize-mbtiles.git
cd optimize-mbtiles
pip install -r requirements.txt
```

## Usage

Check if a file contains any removable redundant subpyramids.

```bash
./optimize.py check <mbtiles_file> -z=<mask_level> [--scheme=<scheme>]
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
