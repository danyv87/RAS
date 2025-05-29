import h5py
import numpy as np
import pandas as pd

hdf_path = r"C:\HECtest\Test.p32.hdf"

with h5py.File(hdf_path, "r") as f:
    time_array = f["Results/Unsteady/Output/Output Blocks/Computation Block/Global/Time"][:]
    print("✓ time_array shape:", time_array.shape)
    print("✓ time_array sample:", time_array[:10])

    # Calcular dt desde time_array
    dt_days = time_array[1] - time_array[0]
    dt_seconds = dt_days * 24 * 3600
    print(f"✓ Paso de tiempo (dt): {dt_days:.6f} días = {dt_seconds:.2f} segundos")

    depths = f["Results/Unsteady/Output/Output Blocks/Sediment/Sediment Time Series/Cross Sections/Effective Depth"][:]
    print("✓ depths shape:", depths.shape)

    coords = f["Geometry/Cross Sections/Polyline Points"][:]
    print("✓ coords shape:", coords.shape)
    print("✓ coords sample:", coords[:10])

    # Identificar el talweg (punto medio de cada sección)
    n_sections = 16
    points_per_section = coords.shape[0] // n_sections
    talweg_points = []
    for i in range(n_sections):
        start_idx = i * points_per_section
        mid_idx = start_idx + points_per_section // 2
        talweg_points.append(coords[mid_idx])
    talweg_points = np.array(talweg_points)

    distances = np.sqrt(np.sum(np.diff(talweg_points, axis=0) ** 2, axis=1))
    distances = np.append(distances, distances[-1])  # repetir última distancia
    print("✓ distances shape:", distances.shape)
    print("✓ distances:", distances)

    # Calcular celeridad
    g = 9.81
    mean_depths = np.mean(depths, axis=0)
    print("✓ mean_depths sample:", mean_depths[:10])
    celerity = np.sqrt(g * mean_depths)
    print("✓ celerity shape:", celerity.shape)

    # Calcular CFL usando dt en segundos
    CFL = (celerity * dt_seconds) / distances
    print("✓ CFL shape:", CFL.shape)

# Crear tabla con pandas
df = pd.DataFrame({
    "Sección": np.arange(1, n_sections + 1),
    "Distancia (m)": distances,
    "Profundidad media (m)": mean_depths,
    "Celeridad (m/s)": celerity,
    "CFL": CFL
})

# Mostrar tabla con 3 decimales
print(df.round(3))
