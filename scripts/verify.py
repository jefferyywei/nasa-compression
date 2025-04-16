import argparse
import xarray as xr
import numpy as np

def verify_netcdf_files(original_path, restored_path):
    print(f"Opening files:\n - Original: {original_path}\n - Restored: {restored_path}")
    original = xr.open_dataset(original_path)
    restored = xr.open_dataset(restored_path)

    print("\nVariable name check...")
    orig_vars = set(original.variables)
    rest_vars = set(restored.variables)
    print(" - Variables match:", orig_vars == rest_vars)
    if orig_vars != rest_vars:
        print(" - Difference:", orig_vars.symmetric_difference(rest_vars))

    print("\nDimension check...")
    print(" - Dimensions match:", original.sizes == restored.sizes)
    if original.sizes != restored.sizes:
        print(" - Original dims:", original.sizes)
        print(" - Restored dims:", restored.sizes)

    print("\nData variable dtype and shape check...")
    for var in original.data_vars:
        if var not in restored:
            print(f" - {var}: missing in restored file")
            continue

        orig = original[var]
        rest = restored[var]

        shape_match = orig.shape == rest.shape
        dtype_match = orig.dtype == rest.dtype
        print(f" - {var}: shape match = {shape_match}, dtype match = {dtype_match}")

    print("\nNumerical difference check (due to rounding)...")
    for var in original.data_vars:
        if var in restored:
            orig_vals = original[var].values
            rest_vals = restored[var].values

            if orig_vals.shape == rest_vals.shape:
                diff = np.abs(orig_vals - rest_vals)
                print(f" - {var}: max error = {np.nanmax(diff):.4g}, mean error = {np.nanmean(diff):.4g}")
            else:
                print(f" - {var}: shape mismatch, skipping numerical comparison.")

    print("\nGlobal attributes check...")
    attr_match = original.attrs == restored.attrs
    print(" - Attributes match:", attr_match)
    if not attr_match:
        print(" - Original attrs:", original.attrs)
        print(" - Restored attrs:", restored.attrs)

def main():
    parser = argparse.ArgumentParser(description="Verify integrity of restored NetCDF file")
    parser.add_argument("original_path", help="Path to original NetCDF file")
    parser.add_argument("restored_path", help="Path to restored NetCDF file")
    args = parser.parse_args()

    verify_netcdf_files(args.original_path, args.restored_path)

if __name__ == "__main__":
    main()
