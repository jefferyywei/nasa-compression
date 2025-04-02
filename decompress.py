import argparse
import zstandard as zstd

def decompress_zstd_to_netcdf(compressed_path, output_netcdf_path):
    with open(compressed_path, "rb") as f:
        compressed_data = f.read()

    dctx = zstd.ZstdDecompressor()
    decompressed_data = dctx.decompress(compressed_data)

    with open(output_netcdf_path, "wb") as f:
        f.write(decompressed_data)

    print(f"Restored NetCDF file written to: {output_netcdf_path}")

def main():
    parser = argparse.ArgumentParser(description="Decompress a Zstandard-compressed NetCDF file")
    parser.add_argument("compressed_path", help="Path to the compressed file")
    parser.add_argument("output_netcdf_path", help="Path to save the decompressed NetCDF file")
    args = parser.parse_args()

    decompress_zstd_to_netcdf(args.compressed_path, args.output_netcdf_path)

if __name__ == "__main__":
    main()
