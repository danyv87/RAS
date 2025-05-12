import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from pydsstools.heclib.dss import HecDss

# 1. Cargar los datos históricos desde el archivo Excel
file_path = r'C:\Users\danielal\OneDrive - ITAIPU Binacional\CIH\Proyectos\HIDRO\Modelación Hidromorfologica\RAS-Embalse\Condiciones de borde del modelo2.xlsx'

# Leer el archivo Excel
try:
    historical_data = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"Error: Excel file not found at {file_path}")
    exit(1)

# 2. Mostrar las columnas del archivo para verificar
print("Columnas del archivo:", historical_data.columns)

# 3. Renombrar las columnas
try:
    historical_data = historical_data.rename(columns={
        'Fecha': 'Date',
        'Caudal Guaira': 'Flow',
        'Nivel Usina': 'Level'
    })
except KeyError:
    print("Error: Expected columns 'Fecha', 'Caudal Guaira', 'Nivel Usina' not found")
    exit(1)

# 4. Asegurarse de que la columna 'Date' esté en formato datetime
historical_data['Date'] = pd.to_datetime(historical_data['Date'])

# 5. Filtrar las columnas necesarias
historical_data = historical_data[['Date', 'Flow', 'Level']]

# 6. Verificar valores nulos
print("Valores nulos en los datos históricos:")
print(historical_data.isnull().sum())
historical_data = historical_data.dropna()

# 7. Calcular correlación histórica
historical_corr = historical_data[['Flow', 'Level']].corr().iloc[0, 1]
print(f"Correlación histórica entre caudal y nivel: {historical_corr:.3f}")

# 8. Estandarizar los datos
scaler = StandardScaler()
data_scaled = scaler.fit_transform(historical_data[['Flow', 'Level']])
data_scaled = pd.DataFrame(data_scaled, columns=['Flow', 'Level'], index=historical_data.index)

# 9. Preparar datos para KNN
data_with_next = data_scaled[:-1].copy()
data_with_next['Next_Flow'] = data_scaled['Flow'][1:].values
data_with_next['Next_Level'] = data_scaled['Level'][1:].values

# 10. Configurar KNN
k = 5
knn = NearestNeighbors(n_neighbors=k, algorithm='auto')
knn.fit(data_with_next[['Flow', 'Level']])

# 11. Generar serie sintética (2019-2419)
start_date = datetime.strptime('2019-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2419-12-31', '%Y-%m-%d')
synthetic_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
n_synthetic = len(synthetic_dates)

current_point = data_scaled.iloc[-1][['Flow', 'Level']].values
synthetic_series = []

for _ in range(n_synthetic):
    distances, indices = knn.kneighbors([current_point], n_neighbors=k)
    weights = 1 / (distances[0] + 1e-10)
    weights /= weights.sum()
    chosen_index = np.random.choice(indices[0], p=weights)
    next_point = data_with_next.iloc[chosen_index][['Next_Flow', 'Next_Level']].values
    synthetic_series.append(next_point)
    current_point = next_point

# 12. Convertir serie sintética a valores originales
synthetic_series = np.array(synthetic_series)
synthetic_series = scaler.inverse_transform(synthetic_series)
synthetic_df = pd.DataFrame({
    'Date': synthetic_dates,
    'Flow': synthetic_series[:, 0],
    'Level': synthetic_series[:, 1]
})

# 13. Calcular correlación sintética
synthetic_corr = synthetic_df[['Flow', 'Level']].corr().iloc[0, 1]
print(f"Correlación sintética entre caudal y nivel: {synthetic_corr:.3f}")

# 14. Plotear series sintéticas
plt.figure(figsize=(18, 6))

plt.subplot(1, 3, 1)
plt.plot(synthetic_df['Date'], synthetic_df['Flow'], label='Caudal sintético', color='blue')
plt.xlabel('Fecha')
plt.ylabel('Caudal (m³/s)')
plt.title('Serie sintética de caudal (2019-2419)')
plt.grid(True)
plt.legend()

plt.subplot(1, 3, 2)
plt.plot(synthetic_df['Date'], synthetic_df['Level'], label='Nivel sintético', color='green')
plt.xlabel('Fecha')
plt.ylabel('Nivel (m)')
plt.title('Serie sintética de nivel (2019-2419)')
plt.grid(True)
plt.legend()

plt.subplot(1, 3, 3)
plt.scatter(historical_data['Flow'], historical_data['Level'], label='Datos históricos', alpha=0.5, color='gray', marker='x')
plt.scatter(synthetic_df['Flow'], synthetic_df['Level'], label='Datos sintéticos', alpha=0.5, color='red', marker='+')
plt.xlabel('Caudal (m³/s)')
plt.ylabel('Nivel (m)')
plt.title('Relación caudal-nivel: Históricos vs. Sintéticos')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.savefig(r'C:\Users\danielal\Desktop\synthetic_flow_level_plots.png')
plt.show()

# 15. Guardar datos sintéticos como CSV
output_csv = r'C:\Users\danielal\Desktop\synthetic_flow_level_2019_to_2419.csv'
synthetic_df.to_csv(output_csv, index=False)
print(f"Datos sintéticos guardados en '{output_csv}'")

# 16. Escribir datos en formato HEC-DSS
import numpy as np
import pandas as pd
from pydsstools.heclib.dss import HecDss, TimeSeriesContainer  # Importar HecDss y TimeSeriesContainer

dss_file = r'C:\Users\danielal\Desktop\synthetic_flow_level_2019_to_2419.dss'

dss = None  # Inicializar dss como None
try:
    # Abrir archivo DSS usando HecDss.Open
    dss = HecDss.Open(dss_file)

    # Debug: Verificar el tipo y formato de la columna 'Date'
    print("Tipo de synthetic_df['Date']:", synthetic_df['Date'].dtype)
    print("Primeras 5 fechas en synthetic_df['Date']:", synthetic_df['Date'].head().tolist())

    # Formatear fechas como cadenas en 'DDMMMYYYY HH:MM'
    times = [date.strftime("%d%b%Y %H:%M").upper() for date in synthetic_df['Date']]
    flow_values = synthetic_df['Flow'].values
    stage_values = synthetic_df['Level'].values

    # Debug: Verificar datos
    print("Primeras 5 fechas formateadas:", times[:5])
    print("Primeros 5 valores de caudal:", flow_values[:5])
    print("Primeros 5 valores de nivel:", stage_values[:5])
    print("Longitudes:", len(times), len(flow_values), len(stage_values))

    # Crear TimeSeriesContainer para la serie de caudal
    flow_container = TimeSeriesContainer()
    flow_container.pathname = "/ITAIPU/GUAIRA/FLOW/01JAN2019/1DAY/SYNTHETIC/"
    flow_container.times = times
    flow_container.values = flow_values.tolist()
    flow_container.units = "CMS"
    flow_container.type = "INST-VAL"
    flow_container.interval = "1DAY"
    dss.put_ts(flow_container)
    print(f"Escrita serie de caudal en DSS: {flow_container.pathname}")

    # Crear TimeSeriesContainer para la serie de nivel
    stage_container = TimeSeriesContainer()
    stage_container.pathname = "/ITAIPU/USINA/STAGE/01JAN2019/1DAY/SYNTHETIC/"
    stage_container.times = times
    stage_container.values = stage_values.tolist()
    stage_container.units = "M"
    stage_container.type = "INST-VAL"
    stage_container.interval = "1DAY"
    dss.put_ts(stage_container)
    print(f"Escrita serie de nivel en DSS: {stage_container.pathname}")

except Exception as e:
    print(f"Error al abrir el archivo DSS: {e}")
finally:
    # Cerrar el archivo DSS solo si dss fue inicializado
    if dss is not None:
        dss.close()

print(f"Archivo DSS generado: '{dss_file}'")