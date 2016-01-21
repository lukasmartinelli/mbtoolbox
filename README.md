# mbtoolbox [![Build Status](https://travis-ci.org/lukasmartinelli/mbtoolbox.svg?branch=master)](https://travis-ci.org/lukasmartinelli/mbtoolbox) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/lukasmartinelli/mbtoolbox/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/lukasmartinelli/mbtoolbox/?branch=master) [![MIT license](https://img.shields.io/badge/license-MIT-blue.svg)](https://tldrlegal.com/license/mit-license)

<img align="right" alt="mbtoolbox" src="subpyramid.png" />

A **MBTiles introspection tool** for optimizing and verifying [MBTiles](https://github.com/mapbox/mbtiles-spec) files.

- Save space by removing redundant subpyramids
- Ensure size of tiles is below a threshold
- Verify that there are no missing or redundant tiles in subpyramids

## Install

You need Python 2 or Python 3 installed on your system.

```bash
git clone https://github.com/lukasmartinelli/mbtoolbox.git
cd mbtoolbox
pip install --process-dependency-links .
```

## Usage

### Check MBTiles for Redundancy

If you are using [tilelive-vector](https://github.com/mapbox/tilelive-vector) or a tile server like [tileserver-php](https://github.com/klokantech/tileserver-php/) which supports `maskLevel`  you can **save a lot of redundant data in your MBTiles file** by backfilling missing high zoom levels with data from low zoom levels. This approach is used at [osm2vectortiles](github.com/osm2vectortiles/osm2vectortiles) to decrease the size of the MBTiles downloads.

Check if a file contains any removable redundant subpyramids for a `maskLevel` of `8`.

```bash
mboptimize check <mbtiles_file> -z 8
```

You get back a list of all optimizable subpyramids.

```bash
8/125/188   OPTIMIZABLE
```

### Remove subpyramids

Once you know your file contains redundancy you can remove the unnecessary tiles.
Removing subpyramids will gain a lot of space in big files since you no longer need to store
all the references to the binary image data. If you render vector tiles of the entire wolrd
to a file with 70GB this can decrease the size by over 12GB.

```bash
mboptimize remove <mbtiles_file> -z 8
```

### Verify Size of MBTiles

Check if a file contains any tiles larger than 500KB.

```bash
mbverify size <mbtiles_file> -s=500000
```

You get back a list of all tiles larger than 500KB.

```bash
14/8024/12095   506 KByte
14/8025/12095   1.1 Mbyte
```

### Verify Subpyramid contains all Tiles

Given you have a MBTiles file you want to verify that that
all tile data for the XYZ subpyramid `8/125/188` down to zoom level 14 is present.

```bash
mbverify missing <mbtiles_file> 125 188 -z 8 -Z 14
```

### Verify Subpyramid has no additional Tiles

Given you have a MBTiles file you want to verify that **only** the exact
tile data of the XYZ subpyramid `8/125/188` down to zoom level 14 is present.
Any additional data is treated as redundant.

```bash
mbverify redundant <mbtiles_file> 125 188 -z 8 -Z 14
```

## Mask Level

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
