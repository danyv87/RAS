#inspeccionar el dataset sediment rating curve
import h5py
import pandas as pd

file_path = 'C:\\HECtest\\Test.p55.hdf'
dataset_path = 'Sediment/Sediment Control Volume/Bottom'

with h5py.File(file_path, 'r') as hdf:
    if dataset_path in hdf:
        data = hdf[dataset_path][:]
        print(f"✅ Dataset leído: shape {data.shape}\n")

        # Convertir a DataFrame y mostrar todas las filas
        df = pd.DataFrame(data)
        pd.set_option('display.max_rows', None)
        print("📊 Todas las filas del dataset:")
        print(df)

        # Inspeccionar atributos del dataset
        print("\n🔖 Atributos del dataset:")
        for attr in hdf[dataset_path].attrs:
            print(f" - {attr}: {hdf[dataset_path].attrs[attr]}")
