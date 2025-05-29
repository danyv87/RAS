import matplotlib.pyplot as plt
import numpy as np
import h5py
import os
from tabulate import tabulate

folder = 'C:\\HECtest'

datos_informes = {
    'Test.p35': {'param': 'Concentración 1000', 'base': '99.67 mg/L', 'var': '+10%', 'nuevo_valor': '109.64 mg/L'},
    'Test.p36': {'param': 'Concentración 1000', 'base': '99.67 mg/L', 'var': '-10%', 'nuevo_valor': '89.70 mg/L'},
    'Test.p37': {'param': 'Concentración 6857', 'base': '99.67 mg/L', 'var': '+10%', 'nuevo_valor': '109.64 mg/L'},
    'Test.p38': {'param': 'Concentración 6857', 'base': '99.67 mg/L', 'var': '-10%', 'nuevo_valor': '89.70 mg/L'},
    'Test.p39': {'param': 'Concentración 19217', 'base': '355.4 mg/L', 'var': '+10%', 'nuevo_valor': '390.94 mg/L'},
    'Test.p41': {'param': 'Concentración 19217', 'base': '355.4 mg/L', 'var': '-10%', 'nuevo_valor': '318.82 mg/L'},
    'Test.p42': {'param': 'Clay', 'base': '40%', 'var': '+10%', 'nuevo_valor': '44%'},
    'Test.p43': {'param': 'Clay', 'base': '40%', 'var': '-10%', 'nuevo_valor': '36%'},
    'Test.p44': {'param': 'VFM', 'base': '22%', 'var': '+10%', 'nuevo_valor': '24.2%'},
    'Test.p45': {'param': 'VFM', 'base': '22%', 'var': '-10%', 'nuevo_valor': '19.8%'},
    'Test.p46': {'param': 'FM', 'base': '18%', 'var': '+10%', 'nuevo_valor': '19.8%'},
    'Test.p47': {'param': 'FM', 'base': '18%', 'var': '-10%', 'nuevo_valor': '16.2%'},
    'Test.p48': {'param': 'Clay', 'base': '40%', 'var': '+20%', 'nuevo_valor': '48%'},
    'Test.p49': {'param': 'Clay', 'base': '40%', 'var': '+30%', 'nuevo_valor': '52%'},
    'Test.p50': {'param': 'Clay', 'base': '40%', 'var': '-20%', 'nuevo_valor': '32%'},
    'Test.p51': {'param': 'Clay', 'base': '40%', 'var': '-30%', 'nuevo_valor': '28%'},
    'Test.p52': {'param': 'VFM', 'base': '18%', 'var': '+20%', 'nuevo_valor': '26.4%'},
    'Test.p53': {'param': 'VFM', 'base': '18%', 'var': '+30%', 'nuevo_valor': '28.6%'},
    'Test.p54': {'param': 'VFM', 'base': '18%', 'var': '-20%', 'nuevo_valor': '17.6%'},
    'Test.p55': {'param': 'VFM', 'base': '18%', 'var': '-30%', 'nuevo_valor': '15.4%'},
}

def extract_float_from_attr(attrs, key):
    raw = attrs.get(key)
    if raw is None:
        return None
    text = raw.decode().strip()
    number_str = text.split()[0]
    try:
        return float(number_str)
    except:
        return None

def calcular_trap_eff(mass_in, mass_out, vol_in, vol_out):
    te_mass = (mass_in - mass_out) / mass_in * 100 if mass_in and mass_in > 0 else None
    te_vol = (vol_in - vol_out) / vol_in * 100 if vol_in and vol_in > 0 else None
    return te_mass, te_vol

def process_hdf_file(file_path):
    try:
        with h5py.File(file_path, 'r') as hdf:
            summary_path = 'Results/Unsteady/Summary'
            if summary_path not in hdf:
                return None
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

            te_mass, te_vol = calcular_trap_eff(mass_in, mass_out, vol_in, vol_out)

            return te_mass, vol_out
    except Exception as e:
        print(f"Error en {file_path}: {e}")
        return None

tabla = []
retencion_base = None
volumen_salida_base = None

# Para graficar
parametros = []
variaciones = []
cambios_retencion_pct = []
cambios_volumen_pct = []

for key in sorted(datos_informes.keys()):
    file_path = os.path.join(folder, f"{key}.hdf")
    resultados = process_hdf_file(file_path)
    if resultados is None:
        print(f"⚠️ No se procesó {key}")
        continue

    te_mass, vol_out = resultados

    # Primer valor base para cambios
    if retencion_base is None:
        retencion_base = te_mass
    if volumen_salida_base is None:
        volumen_salida_base = vol_out

    cambio_retencion = te_mass - retencion_base if te_mass is not None else None
    cambio_vol_salida = vol_out - volumen_salida_base if vol_out is not None else None

    # Cambios relativos porcentuales para graficar
    cambio_retencion_rel = (cambio_retencion / retencion_base * 100) if (cambio_retencion is not None and retencion_base != 0) else 0
    cambio_volumen_rel = (cambio_vol_salida / volumen_salida_base * 100) if (cambio_vol_salida is not None and volumen_salida_base != 0) else 0

    tabla.append([
        key,
        datos_informes[key]['param'],
        datos_informes[key]['base'],
        datos_informes[key]['var'],
        datos_informes[key]['nuevo_valor'],
        f"{te_mass:.2f}%" if te_mass is not None else "N/A",
        f"{vol_out:.2e}" if vol_out is not None else "N/A",
        f"{cambio_retencion:+.2f}%",
        f"{cambio_vol_salida:+.2e}",
        f"{cambio_retencion_rel:+.2f}%",
        f"{cambio_volumen_rel:+.2f}%"
    ])

    parametros.append(datos_informes[key]['param'] + " " + datos_informes[key]['var'])
    variaciones.append(datos_informes[key]['var'])
    cambios_retencion_pct.append(cambio_retencion_rel)
    cambios_volumen_pct.append(cambio_volumen_rel)

headers = [
    "ID - SA", "Parámetro modificado", "Valor base", "Variación", "Nuevo valor",
    "% de retención", "Volumen de salida",
    "Cambio absoluto retención", "Cambio absoluto volumen",
    "Cambio % retención (relativo)", "Cambio % volumen (relativo)"
]

print(tabulate(tabla, headers=headers, tablefmt="plain", stralign="center"))

# Gráfico de sensibilidad
x = np.arange(len(parametros))
width = 0.4

fig, ax = plt.subplots(figsize=(15,7))
bar1 = ax.bar(x - width/2, cambios_volumen_pct, width, label='% Cambio Relativo Volumen de salida')
bar2 = ax.bar(x + width/2, cambios_retencion_pct, width, label='% Cambio Relativo Retención')

ax.set_ylabel('Cambio relativo (%) respecto base')
ax.set_title('Sensibilidad del modelo: cambios relativos en volumen y retención')
ax.set_xticks(x)
ax.set_xticklabels(parametros, rotation=45, ha='right')
ax.legend()
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.show()
