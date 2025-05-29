import h5py

hdf_files = [
    r"C:\HECtest\Test.p45.hdf"
]

group_paths = [
    "Plan Data/Plan Information",
    "Results",
]

def recorrer_grupo(grupo, nivel=1):
    indent = "  " * nivel
    for key in grupo.keys():
        item = grupo[key]
        if isinstance(item, h5py.Group):
            print(f"{indent}[GROUP]   {key}")
            recorrer_grupo(item, nivel + 1)
        elif isinstance(item, h5py.Dataset):
            print(f"{indent}[DATASET] {key} - shape: {item.shape}, dtype: {item.dtype}")

for file_path in hdf_files:
    print(f"\n📁 Archivo: {file_path}")
    try:
        with h5py.File(file_path, 'r') as hdf:
            for group_path in group_paths:
                if group_path in hdf:
                    group = hdf[group_path]
                    print(f"  ✅ Grupo encontrado: {group_path}")

                    print(f"    Contenido (claves): {list(group.keys())}")
                    if group.attrs:
                        print(f"    Atributos del grupo:")
                        for attr_name, attr_value in group.attrs.items():
                            print(f"      - {attr_name}: {attr_value}")
                    else:
                        print("    (Sin atributos)")

                    recorrer_grupo(group)
                else:
                    print(f"  ❌ Grupo no encontrado: {group_path}")
    except Exception as e:
        print(f"  ⚠️ Error al leer el archivo {file_path}: {e}")
