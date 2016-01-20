from collections import defaultdict
import humanize
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


def redundant_tiles(mbtiles, required_tiles):
    """All tiles that should not be in MBTiles"""
    xyz_dict= lambda: defaultdict(xyz_dict)

    # Mark all tiles that are required
    marked_tiles = xyz_dict()
    for tile in required_tiles:
        marked_tiles[tile.z][tile.x][tile.y] = True


    for tile in mbtiles.all_tiles():
        required = marked_tiles[tile.z][tile.x][tile.y]
        if required != True:
            yield tile


def missing_tiles(mbtiles, required_tiles):
    """All tiles that should be in MBTiles but are missing"""
    for tile in required_tiles:
        if not mbtiles.tile_exists(tile.x, tile.y, tile.z):
            yield tile


def verify_size(mbtiles_file, max_size, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)
    for tile in mbtiles.tiles_by_size(max_size):
        print('{}/{}/{}\t{}'.format(tile.z, tile.x, tile.y,
                                        humanize.naturalsize(tile.size)))


def list_required_tiles(x, y, min_zoom, max_zoom):
    root_tile = mercantile.Tile(x, y, min_zoom)
    required_tiles = list(all_descendant_tiles(x, y, min_zoom, max_zoom))
    required_tiles += [root_tile]
    return required_tiles


def verify_redundant_tiles(mbtiles_file, x, y, min_zoom, max_zoom, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)
    required_tiles = list_required_tiles(x, y, min_zoom, max_zoom)
    for tile in redundant_tiles(mbtiles, required_tiles):
        print('{}/{}/{}\t{}'.format(tile.z, tile.x, tile.y, 'REDUNDANT'))


def verify_missing_tiles(mbtiles_file, x, y, min_zoom, max_zoom, scheme):
    mbtiles = MBTiles(mbtiles_file, scheme)
    required_tiles = list_required_tiles(x, y, min_zoom, max_zoom)

    for tile in missing_tiles(mbtiles, required_tiles):
        print('{}/{}/{}\t{}'.format(tile.z, tile.x, tile.y, 'MISSING'))
