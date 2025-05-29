#generar tabla comparativa del analisis de sensibilidad
import h5py
import os
from tabulate import tabulate

folder = 'C:\\HECtest'
file_prefix = 'Test.p'
start_num = 33
end_num = 56

def extract_float_from_attr(attrs, key):
    raw = attrs.get(key)
    if raw is None:
        return None
    text = raw.decode().strip()
    number_str = text.split()[0]
    return float(number_str)

def process_hdf_file(file_path):
    result = {
        'File': os.path.basename(file_path),
        'Mass In (tonnes)': None,
        'Mass Out (tonnes)': None,
        'Vol In (m³)': None,
        'Vol Out (m³)': None,
        'Trap Eff Mass (%)': None,
        'Trap Eff Vol (%)': None
    }

    try:
        with h5py.File(file_path, 'r') as hdf:
            summary_path = 'Results/Unsteady/Summary'
            if summary_path not in hdf:
                print(f"⚠️ Grupo '{summary_path}' no encontrado en {file_path}")
                return result

            attrs = hdf[summary_path].attrs
            attr_keys = [k.decode() if isinstance(k, bytes) else k for k in attrs]

            key_mass_in = next(k for k in attr_keys if 'Cum In' in k and 'Mass' in k)
            key_mass_out = next(k for k in attr_keys if 'Cum Out' in k and 'Mass' in k)
            key_vol_in = next(k for k in attr_keys if 'Cum In' in k and 'Vol' in k)
            key_vol_out = next(k for k in attr_keys if 'Cum Out' in k and 'Vol' in k)

            mass_in = extract_float_from_attr(attrs, key_mass_in)
            mass_out = extract_float_from_attr(attrs, key_mass_out)
            vol_in = extract_float_from_attr(attrs, key_vol_in)
            vol_out = extract_float_from_attr(attrs, key_vol_out)

            result['Mass In (tonnes)'] = mass_in
            result['Mass Out (tonnes)'] = mass_out
            result['Vol In (m³)'] = vol_in
            result['Vol Out (m³)'] = vol_out

            if mass_in and mass_in > 0:
                result['Trap Eff Mass (%)'] = (mass_in - mass_out) / mass_in * 100
            if vol_in and vol_in > 0:
                result['Trap Eff Vol (%)'] = (vol_in - vol_out) / vol_in * 100

    except Exception as e:
        print(f"❌ Error en archivo {file_path}: {e}")

    return result

results = []
for i in range(start_num, end_num + 1):
    file_path = os.path.join(folder, f'{file_prefix}{i}.hdf')
    if os.path.exists(file_path):
        res = process_hdf_file(file_path)
        results.append(res)
    else:
        print(f"⚠️ Archivo no encontrado: {file_path}")

# Imprimir tabla
print(tabulate(results, headers="keys", floatfmt=".2f", tablefmt="grid"))
