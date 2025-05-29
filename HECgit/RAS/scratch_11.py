import h5py
import numpy as np
import os

def extraer_datos_sedimentos(hdf_path):
    if not os.path.exists(hdf_path):
        print(f"❌ Archivo no encontrado: {hdf_path}")
        return

    output = {}
    with h5py.File(hdf_path, "r") as hdf:
        print(f"📂 Abierto: {os.path.basename(hdf_path)}")

        # 1. Masa total de entrada según curva de carga de sedimentos
        try:
            flow_load_path = (
                "Sediment/Boundary Conditions/Sediment Rating Curve/"
                "River: RioParana Reach: Embalse RS: 163200/Flow Load"
            )
            flow_load = hdf[flow_load_path][()]
            output["Masa total (kg) - Flow Load"] = float(np.sum(flow_load))
        except Exception as e:
            output["Flow Load error"] = str(e)

        # 2. Datos observados (si están disponibles)
        try:
            obs_path = "Sediment/XS Parameters/Observed Data"
            obs_data = hdf[obs_path][()]
            output["Datos observados - Shape"] = obs_data.shape
            output["Datos observados - Muestra"] = obs_data[:5].tolist()
        except Exception as e:
            output["Observed Data error"] = str(e)

        # 3. Gradación base del sedimento
        try:
            grad_path = "Sediment/Bed Gradation Data/Base Gradation"
            grad = hdf[grad_path][()]
            output["Base Gradation - Muestra"] = grad[:5].tolist()
        except Exception as e:
            output["Base Gradation error"] = str(e)

    # Mostrar resultados
    print("\n📊 RESULTADOS:")
    for key, val in output.items():
        print(f"- {key}: {val}")

# 🔧 USO
# Colocá el path correcto a tu archivo .hdf de resultados
archivo = "C:\\HECtest\\Test.p35.hdf"
extraer_datos_sedimentos(archivo)
