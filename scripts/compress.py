import argparse
import xarray as xr
import xbitinfo as xb
import zstandard as zstd
import os
import tempfile
import netCDF4

def xbitinfo_round(file_path, inflevel):
    ds = xr.open_dataset(file_path)
    coord_vars = list(ds.coords)

    if "TAITIME" in list(ds.data_vars):
        coord_vars.append('TAITIME')
    coord_data = {var: ds[var] for var in coord_vars if var in ds}
    ds_round = ds.drop_vars(coord_vars)

    bitinfo = xb.get_bitinformation(ds, dim="lon")
    keepbits = xb.get_keepbits(bitinfo, inflevel=inflevel)

    neg_vars = [v for v, kb in keepbits.items() if kb.item() < 0]
    if neg_vars:
        print(f"Skipping variables with negative keepbits: {neg_vars}")
        neg_data = {v: ds[v] for v in neg_vars}
        ds_round  = ds_round.drop_vars(neg_vars)
        # remove them from the keepbits dict so xr_bitround won’t see them
        keepbits = {v: kb for v, kb in keepbits.items() if v not in neg_vars}
    else:
        neg_data = {}

    keepbits = {var: int(kb.item()) for var, kb in keepbits.items()}

    ds_bitrounded = xb.xr_bitround(ds_round, keepbits)

    for v, arr in {**coord_data, **neg_data}.items():
        ds_bitrounded[v] = arr

    with tempfile.NamedTemporaryFile(suffix=".nc4", delete=False) as tmp:
        temp_path = tmp.name

    ds_bitrounded.to_netcdf(path=temp_path, mode='w', format="NETCDF4", engine="netcdf4")

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
