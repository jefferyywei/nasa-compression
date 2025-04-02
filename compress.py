import argparse
import xarray as xr
import xbitinfo as xb
import zstandard as zstd
import os
import tempfile

def xbitinfo_round(file_path, inflevel):
    ds = xr.open_dataset(file_path)
    coord_vars = ['TAITIME', 'time', 'lon', 'lat']
    coord_data = {var: ds[var] for var in coord_vars if var in ds}
    ds = ds.drop_vars(coord_vars)

    bitinfo = xb.get_bitinformation(ds, dim="lon")
    keepbits = xb.get_keepbits(bitinfo, inflevel=inflevel)
    ds_bitrounded = xb.xr_bitround(ds, keepbits)

    for var, var_data in coord_data.items():
        ds_bitrounded[var] = var_data

    with tempfile.NamedTemporaryFile(suffix=".nc4", delete=False) as tmp:
        temp_path = tmp.name

    ds_bitrounded.to_netcdf(temp_path)

    with open(temp_path, 'rb') as f:
        data_bytes = f.read()

    os.remove(temp_path)

    return data_bytes

def main():
    parser = argparse.ArgumentParser(
        description="Apply xbitinfo rounding in memory and compress the result with zstd."
    )
    parser.add_argument("file_path", help="Path to the input NetCDF file")
    parser.add_argument("compression_level", type=float, help="Rounding level for xbitinfo rounding")
    parser.add_argument("output_path", help="Path to write the compressed file")
    args = parser.parse_args()

    rounded_data_bytes = xbitinfo_round(args.file_path, args.compression_level)

    cctx = zstd.ZstdCompressor(level=22)
    compressed_data = cctx.compress(rounded_data_bytes)

    with open(args.output_path, "wb") as f:
        f.write(compressed_data)
    print(f"Compressed file written to: {args.output_path}")

if __name__ == "__main__":
    main()
