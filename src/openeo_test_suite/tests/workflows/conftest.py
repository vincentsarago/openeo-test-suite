import json
import os
import urllib

import numpy as np
import openeo
import pystac
import pystac_client
import pytest


@pytest.fixture
def s2_collection(request) -> str:
    """
    Fixture to provide the data collection to test against.
    If we provide a string, it will be interpreted as openEO Collection.
    If it's an URL, it's interpreted as STAC Collection.
    """
    # TODO: also support getting it from a config file?
    if request.config.getoption("--s2-collection"):
        collection = request.config.getoption("--s2-collection")
    elif "S2_COLLECTION" in os.environ:
        collection = os.environ["S2_COLLECTION"]
    else:
        raise RuntimeError(
            "No S2 test collection found. Specify it using the `--s2-collection` command line option or through the 'S2_COLLECTION' environment variable"
        )
    return collection


@pytest.fixture
def auto_authenticate() -> bool:
    """
    Fixture to act as parameterizable toggle for authenticating the connection fixture.
    Allows per-test/folder configuration of auto-authentication.
    """
    return True


@pytest.fixture
def cube_one_day_red(
    connection,
    bounding_box,
    temporal_interval_one_day,
    s2_collection,
) -> dict:
    params = {
        "spatial_extent": bounding_box,
        "temporal_extent": temporal_interval_one_day,
        "bands": ["B04"],
    }
    if "http" in s2_collection:
        cube = connection.load_stac(s2_collection, **params)
    else:
        cube = connection.load_collection(s2_collection, **params)
    return cube


@pytest.fixture
def cube_one_day_red_nir(
    connection,
    bounding_box,
    temporal_interval_one_day,
    s2_collection,
) -> dict:
    params = {
        "spatial_extent": bounding_box,
        "temporal_extent": temporal_interval_one_day,
        "bands": ["B04", "B08"],
    }
    if "http" in s2_collection:
        cube = connection.load_stac(s2_collection, **params)
    else:
        cube = connection.load_collection(s2_collection, **params)
    return cube


@pytest.fixture
def cube_red_nir(
    connection,
    bounding_box,
    temporal_interval,
    s2_collection,
) -> dict:
    params = {
        "spatial_extent": bounding_box,
        "temporal_extent": temporal_interval,
        "bands": ["B04", "B08"],
    }
    if "http" in s2_collection:
        cube = connection.load_stac(s2_collection, **params)
    else:
        cube = connection.load_collection(s2_collection, **params)
    return cube


@pytest.fixture
def cube_red_10x10(
    connection,
    bounding_box_32632_10x10,
    temporal_interval_one_day,
    s2_collection,
) -> dict:
    params = {
        "spatial_extent": bounding_box_32632_10x10,
        "temporal_extent": temporal_interval_one_day,
        "bands": ["B04"],
    }
    if "http" in s2_collection:
        cube = connection.load_stac(s2_collection, **params)
    else:
        cube = connection.load_collection(s2_collection, **params)
    return cube


@pytest.fixture
def cube_full_extent(
    connection,
    temporal_interval,
    s2_collection,
) -> dict:
    if "http" in s2_collection:
        cube = connection.load_stac(s2_collection, temporal_extent=temporal_interval)
    else:
        # Maybe not the best idea to load a full openEO collection?
        # It would work fine if the STAC sample collection is replicated
        return None
    return cube


@pytest.fixture
def bounding_box(
    west=10.342, east=11.352, south=46.490, north=46.495, crs="EPSG:4326"
) -> dict:
    spatial_extent = {
        "west": west,
        "east": east,
        "south": south,
        "north": north,
        "crs": crs,
    }
    return spatial_extent


@pytest.fixture
def bounding_box_32632_10x10(
    west=680000, east=680100, south=5151500, north=5151600, crs="EPSG:32632"
) -> dict:
    spatial_extent = {
        "west": west,
        "east": east,
        "south": south,
        "north": north,
        "crs": crs,
    }
    return spatial_extent


@pytest.fixture
def temporal_interval():
    return ["2022-06-01", "2022-07-01"]


@pytest.fixture
def temporal_interval_one_day():
    return ["2022-06-01", "2022-06-03"]


# TODO: the dimension names are back-end specific, even though they should be the ones from the STAC metadata
@pytest.fixture
def collection_dims(
    connection,
    s2_collection,
):
    if "/" in s2_collection:
        # I ocnsider it as a STAC url
        parsed_url = urllib.parse.urlparse(s2_collection)
        if not bool(parsed_url.scheme):
            parsed_url = parsed_url._replace(**{"scheme": "https"})
        s2_collection_url = parsed_url.geturl()
        stac_api = pystac_client.stac_api_io.StacApiIO()
        stac_dict = json.loads(stac_api.read_text(s2_collection_url))
    else:
        # I consider it as an openEO Collection
        stac_dict = dict(connection.describe_collection(s2_collection))
    collection_dims = dict(b_dim=None, t_dim=None, x_dim=None, y_dim=None, z_dim=None)
    if "cube:dimensions" in stac_dict:
        for dim in stac_dict["cube:dimensions"]:
            if stac_dict["cube:dimensions"][dim]["type"] == "bands":
                collection_dims["b_dim"] = dim
            if stac_dict["cube:dimensions"][dim]["type"] == "temporal":
                collection_dims["t_dim"] = dim
            if stac_dict["cube:dimensions"][dim]["type"] == "spatial":
                if stac_dict["cube:dimensions"][dim]["axis"] == "x":
                    collection_dims["x_dim"] = dim
                if stac_dict["cube:dimensions"][dim]["axis"] == "y":
                    collection_dims["y_dim"] = dim
                if stac_dict["cube:dimensions"][dim]["axis"] == "z":
                    collection_dims["z_dim"] = dim
    return collection_dims
