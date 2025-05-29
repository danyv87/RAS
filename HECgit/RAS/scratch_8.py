#inspeccionar estructura de archivo HDF
import h5py

file_path = 'C:\\HECtest\\Test.p45.hdf'


def explore_hecras_hdf(file_path):
    try:
        with h5py.File(file_path, 'r') as hdf:
            print(f"✅ Opened file: {file_path}\n")
            print("📂 Top-level groups:")
            for key in hdf.keys():
                print(f" - {key}")

            print("\n🔍 Full structure of the file:\n")

            def visit(name, obj):
                if isinstance(obj, h5py.Dataset):
                    print(f"[DATASET] {name}")
                elif isinstance(obj, h5py.Group):
                    print(f"[GROUP]   {name}")

            hdf.visititems(visit)
    except Exception as e:
        print(f"❌ Failed to read the file: {e}")


# Run the function
explore_hecras_hdf(file_path)
