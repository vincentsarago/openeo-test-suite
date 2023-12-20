import xarray as xr


def test_apply_dimension_order(
    cube_one_day_red_nir,
    collection_dims,
    tmp_path,
):
    filename = tmp_path / "test_apply_dimension_order.nc"
    b_dim = collection_dims["b_dim"]

    from openeo.processes import order

    cube = cube_one_day_red_nir.apply_dimension(
        process=lambda d: order(d),
        dimension=b_dim,
    )

    cube.download(filename)
    assert filename.exists()
    try:
        data = xr.open_dataarray(filename)
    except ValueError:
        data = xr.open_dataset(filename, decode_coords="all").to_dataarray(dim=b_dim)
    assert len(data[b_dim]) == 2
