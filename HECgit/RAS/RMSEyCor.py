import h5py
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt

# Ruta de archivos HDF
hdf_files = [
    fr"C:\HECtest\Test.p{num}.hdf"
    for num in range(35, 55)  # 53 porque el límite superior no se incluye
]

# Nombres amigables para métodos de transporte
nombres_metodos = {
    "Test.p33.hdf": "Meyer-Peter Müller",
    "Test.p34.hdf": "Larsen-Copeland",
    "Test.p35.hdf": "Toffaletti"
}

# Datos observados (2018)
observed_2018 = np.array([
    193.08, 175.62, 182.37, 145.27, 128.01, 107.38, 76.50, 88.56,
    85.25, 82.26, 78.73, 64.64, 61.55, 76.38, 56.26, 67.76
])

# Lista para resultados
results = []
simulated_profiles = {}

for file_path in hdf_files:
    file_name = os.path.basename(file_path)
    metodo = nombres_metodos.get(file_name, file_name)

    try:
        with h5py.File(file_path, 'r') as f:
            invert_data = f['Results']['Unsteady']['Output']['Output Blocks']['Sediment']\
                ['Sediment Time Series']['Cross Sections']['Invert Elevation']
            last_sim = invert_data[-1]
    except Exception as e:
        print(f"⚠️ Error al procesar {file_path}: {e}")
        continue

    if len(last_sim) != len(observed_2018):
        print(f"⚠️ Tamaño incompatible en {file_path}: {len(last_sim)} vs {len(observed_2018)}")
        continue

    rmse = np.sqrt(np.mean((last_sim - observed_2018) ** 2))
    corr = np.corrcoef(last_sim, observed_2018)[0, 1]

    results.append({
        "Método": metodo,
        "RMSE": round(rmse, 3),
        "Correlación (r)": round(corr, 3)
    })

    # Guardar perfil para graficar
    simulated_profiles[metodo] = last_sim

# Crear tabla ordenada por RMSE
df = pd.DataFrame(results)
df_sorted = df.sort_values(by="RMSE")

# Mostrar tabla
print("\n📊 Resultados comparativos:")
print(df_sorted.to_string(index=False))

# Guardar en Excel
df_sorted.to_excel("comparacion_metodos_sedimentos.xlsx", index=False)

# 🔹 Gráfico de perfiles longitudinales
plt.figure(figsize=(10, 6))
x = np.arange(len(observed_2018))

# Perfil observado
plt.plot(x, observed_2018, 'k--', label="Observado (2018)", linewidth=2)

# Perfiles simulados
for metodo, perfil in simulated_profiles.items():
    plt.plot(x, perfil, label=metodo)

plt.xlabel("Sección transversal")
plt.ylabel("Elevación del lecho (m)")
plt.title("Comparación de Perfiles Longitudinales")
plt.legend()
plt.grid(True)
plt.gca().invert_xaxis()  # 👈 Esta línea invierte el eje X
plt.tight_layout()
plt.show()
