#!/usr/bin/env python
"""Remove descendant tiles below a parent tile with specified mask level.
Usage:
  optimize.py check <mbtiles_file> -z=<mask_level> [--scheme=<scheme>]
  optimize.py optimize <mbtiles_file> -z=<mask_level> [--scheme=<scheme>]
  optimize.py (-h | --help)
  optimize.py --version

Options:
  -h --help                 Show this screen.
  --version                 Show version.
  -z=<mask_level>           Minimum zoom level where data should still exist
  --scheme=<scheme>         Tiling scheme of the tiles can be either xyz or tms [default: tms]
"""
from collections import namedtuple, Counter
from docopt import docopt

import sys
import hashlib
import mbutil
import mercantile

TileSize = namedtuple('TileSize', ['x', 'y', 'z', 'size'])


class MBTiles:
    def __init__(self, mbtiles_file, scheme):
        self.conn = mbutil.mbtiles_connect(mbtiles_file)
        self.scheme = scheme
        self._tiles_view = self.using_tiles_view()

    def using_tiles_view(self):
        rs = self.conn.execute("""
            SELECT COUNT(*) FROM sqlite_master
            WHERE (type='view' AND name='tiles')
               OR (type='table' AND name='map') COLLATE NOCASE
        """).fetchone()
        return rs[0] == 2

    def tiles_at_zoom_level(self, z):
        query = (
            'select tile_column, tile_row, length(tile_data) from tiles where zoom_level={}'
            .format(z)
        )
        for tile in self.conn.execute(query):
            x = tile[0]
            y = tile[1]
            size = tile[2]

            if self.scheme == 'tms':
                y = mbutil.flip_y(z, y)
            yield mercantile.Tile(x, y, z)

    def remove_tiles(self, tiles):
        for tile in tiles:
            self.remove_tile(x=tile.x, y=tile.y, z=tile.z)
        self.conn.commit()

    def remove_tile(self, x, y, z):
        if self.scheme == 'tms':
            y = mbutil.flip_y(z, y)

        if self._tiles_view:
            delete_query = (
                'delete from map where zoom_level={} ' +
                'and tile_column={} and tile_row={}'
            ).format(z, x, y)
        else:
            delete_query = (
                'delete from tiles where zoom_level={} ' +
                'and tile_column={} and tile_row={}'
            ).format(z, x, y)

        self.conn.execute(delete_query)

    def inspect_tile(self, x, y, z):
        if self.scheme == 'tms':
            y = mbutil.flip_y(z, y)

        query = (
            'select tile_data from tiles where zoom_level={} ' +
            'and tile_column={} and tile_row={}'
        ).format(z, x, y)
        rs = self.conn.execute(query).fetchone()
        if rs:
            raw = rs[0]
            return hashlib.sha1(raw).hexdigest()
        else:
            return None


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


if __name__ == '__main__':
    args = docopt(__doc__, version='0.1')
    if args.get('check'):
        sys.exit(check_masked_tiles(
            args['<mbtiles_file>'],
            int(args['-z']),
            args['--scheme']
        ))
    if args.get('optimize'):
        remove_subpyramids(
            args['<mbtiles_file>'],
            int(args['-z']),
            args['--scheme']
        )
