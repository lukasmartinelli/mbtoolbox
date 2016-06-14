"""
MBTiles wrapper class with support for various access
methods and modifications for the tiles table.
"""

from collections import namedtuple
import hashlib

TileSize = namedtuple('TileSize', ['x', 'y', 'z', 'size'])


def flip_y(zoom, y):
    return (2**zoom-1) - y


class MBTiles:
    def __init__(self, mbtiles_file, scheme):
        self.conn = sqlite3.connect(mbtiles_file)
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
                y = flip_y(z, y)
            yield TileSize(x, y, z, size)

    def tiles_by_size(self, max_size):
        tiles = self.conn.execute("""
            select zoom_level, tile_column, tile_row, length(tile_data) from tiles
            where length(tile_data) > {}
        """.format(max_size))
        for tile in tiles:
            z = tile[0]
            x = tile[1]
            y = tile[2]
            size = tile[3]

            if self.scheme == 'tms':
                y = flip_y(z, y)
            yield TileSize(x, y, z, size)

    def all_tiles(self):
        tiles = self.conn.execute('select zoom_level, tile_column, tile_row, length(tile_data) from tiles')
        for tile in tiles:
            z = tile[0]
            x = tile[1]
            y = tile[2]
            size = tile[3]

            if self.scheme == 'tms':
                y = flip_y(z, y)
            yield TileSize(x, y, z, size)

    def tile_exists(self, x, y, z):
        if self.scheme == 'tms':
            y = flip_y(z, y)
        query = (
            'select count(*) from tiles where zoom_level={} and tile_column={} and tile_row={}'
            .format(z, x, y)
        )
        rs = self.conn.execute(query).fetchone()
        return rs[0] == 1

    def remove_tiles(self, tiles):
        for tile in tiles:
            self.remove_tile(x=tile.x, y=tile.y, z=tile.z)
        self.conn.commit()

    def remove_tile(self, x, y, z):
        if self.scheme == 'tms':
            y = flip_y(z, y)

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
            y = flip_y(z, y)

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
