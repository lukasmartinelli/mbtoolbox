"""
Find and remove descendant tiles below a parent tile with specified mask level.
"""
from collections import Counter

import sys
import mercantile

from .mbtiles import MBTiles


def all_descendant_tiles(x, y, zoom, max_zoom):
    """Return all subtiles contained within a tile"""
    if zoom < max_zoom:
        for child_tile in mercantile.children(x, y, zoom):
            yield child_tile
            for desc_tile in all_descendant_tiles(child_tile.x, child_tile.y,
                                                  child_tile.z, max_zoom):
                yield desc_tile


def find_optimizable_tiles(mbtiles, maskLevel, scheme):
    parent_tiles = [t for t in mbtiles.tiles_at_zoom_level(maskLevel)]

    def descendant_checksums(x, y, zoom, max_zoom):
        for tile in all_descendant_tiles(x, y, zoom, max_zoom=14):
            yield mbtiles.inspect_tile(tile.x, tile.y, tile.z)

    for tile in parent_tiles:
        parent_checksum = mbtiles.inspect_tile(tile.x, tile.y, tile.z)
        counter = Counter(descendant_checksums(tile.x, tile.y, tile.z, 14))

        checksum, _ = counter.most_common(1)[0]
        if parent_checksum == checksum and len(counter) == 1:
            yield tile


def remove_subpyramids(mbtiles_file, maskLevel, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)

    for tile in find_optimizable_tiles(mbtiles, maskLevel, scheme):
        desc_tiles = list(all_descendant_tiles(x=tile.x, y=tile.y,
                                               zoom=tile.z, max_zoom=14))
        mbtiles.remove_tiles(desc_tiles)
        for desc_tile in desc_tiles:
            print('{}/{}/{}\t{}'.format(desc_tile.z, desc_tile.x,
                                        desc_tile.y, 'REMOVED'))


def check_masked_tiles(mbtiles_file, maskLevel, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)
    tiles = list(find_optimizable_tiles(mbtiles, maskLevel, scheme))
    for tile in tiles:
        print('{}/{}/{}\t{}'.format(tile.z, tile.x, tile.y, 'OPTIMIZABLE'))
    return len(tiles)


def purge_tiles_by_size(mbtiles_file, max_size, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)
    oversized_tiles = mbtiles.tiles_by_size(max_size)
    mbtiles.remove_tiles(oversized_tiles)

    for tile in oversized_tiles:
        print('{}/{}/{}\t{}'.format(
            tile.z, tile.x, tile.y,
            humanize.naturalsize(tile.size))
        )
