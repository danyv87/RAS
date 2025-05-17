import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pydsstools.heclib.dss import HecDss
from pydsstools.core import TimeSeriesContainer

# 1. Cargar los datos desde Excel
file_path = r'C:\Users\ASUS\OneDrive - ITAIPU Binacional\CIH\Proyectos\HIDRO\Modelación Hidromorfologica\RAS-Embalse\Condiciones de borde del modelo2.xlsx'

try:
    historical_data = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"Error: Excel file not found at {file_path}")
    exit(1)

# 2. Renombrar columnas
historical_data = historical_data.rename(columns={
    'Fecha': 'Date',
    'Caudal Guaira': 'Flow',
    'Nivel Usina': 'Level'
})

# 3. Asegurar formato datetime y limpiar datos
historical_data['Date'] = pd.to_datetime(historical_data['Date'])
historical_data = historical_data[['Date', 'Flow', 'Level']].dropna()

# 4. Estandarizar
scaler = StandardScaler()
data_scaled = scaler.fit_transform(historical_data[['Flow', 'Level']])
data_scaled = pd.DataFrame(data_scaled, columns=['Flow', 'Level'], index=historical_data.index)

# 5. Preparar KNN
data_with_next = data_scaled[:-1].copy()
data_with_next['Next_Flow'] = data_scaled['Flow'][1:].values
data_with_next['Next_Level'] = data_scaled['Level'][1:].values

k = 5
knn = NearestNeighbors(n_neighbors=k)
knn.fit(data_with_next[['Flow', 'Level']])

# 6. Generar serie sintética
start_date = datetime.strptime('2019-01-01', '%Y-%m-%d')
end_date = datetime.strptime('2419-12-31', '%Y-%m-%d')
synthetic_dates = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]
n_synthetic = len(synthetic_dates)

current_point = data_scaled.iloc[-1][['Flow', 'Level']].values
synthetic_series = []

for _ in range(n_synthetic):
    distances, indices = knn.kneighbors([current_point])
    weights = 1 / (distances[0] + 1e-10)
    weights /= weights.sum()
    chosen_index = np.random.choice(indices[0], p=weights)
    next_point = data_with_next.iloc[chosen_index][['Next_Flow', 'Next_Level']].values
    synthetic_series.append(next_point)
    current_point = next_point

# 7. Invertir la estandarización
synthetic_series = np.array(synthetic_series)
synthetic_series = scaler.inverse_transform(synthetic_series)
synthetic_df = pd.DataFrame({
    'Date': synthetic_dates,
    'Flow': synthetic_series[:, 0],
    'Level': synthetic_series[:, 1]
})

# 8. Guardar como CSV
output_csv = r'C:\Users\ASUS\OneDrive - ITAIPU Binacional\CIH\Proyectos\HIDRO\Modelación Hidromorfologica\RAS-Embalse\synthetic_flow_level_2019_to_2419.csv'
synthetic_df.to_csv(output_csv, index=False)
print(f"Datos sintéticos guardados en '{output_csv}'")

# 9. Guardar en archivo DSS como serie regular
output_dss = r'C:\Users\ASUS\OneDrive - ITAIPU Binacional\CIH\Proyectos\HIDRO\Modelación Hidromorfologica\RAS-Embalse\synthetic_flow_level_2019_to_2419.dss'

try:
    with HecDss.Open(output_dss) as dss:
        start_str = synthetic_df['Date'].iloc[0].strftime('%d%b%Y %H:%M').upper()

        # Guardar Flow
        flow_container = TimeSeriesContainer()
        flow_container.pathname = "/ITAIPU/GUAIRA/FLOW//1DAY/SYNTHETIC/"
        flow_container.startDateTime = start_str
        flow_container.interval = 1
        flow_container.values = synthetic_df['Flow'].values.tolist()
        flow_container.numberValues = len(flow_container.values)
        flow_container.units = "CMS"
        flow_container.type = "INST"
        dss.put_ts(flow_container)
        print(f"Escrita serie de caudal en DSS: {flow_container.pathname}")

        # Guardar Level
        level_container = TimeSeriesContainer()
        level_container.pathname = "/ITAIPU/USINA/STAGE//1DAY/SYNTHETIC/"
        level_container.startDateTime = start_str
        level_container.interval = 1
        level_container.values = synthetic_df['Level'].values.tolist()
        level_container.numberValues = len(level_container.values)
        level_container.units = "M"
        level_container.type = "INST"
        dss.put_ts(level_container)
        print(f"Escrita serie de nivel en DSS: {level_container.pathname}")

except Exception as e:
    print(f"Error al guardar archivo DSS: {e}")