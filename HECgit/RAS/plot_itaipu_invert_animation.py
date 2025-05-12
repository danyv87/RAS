import h5py
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime
from PIL import Image
import cv2
import numpy as np
import os

# Plan definido directamente (Plan 1)
hdf_file = r"C:\HECtest\Test.p27.hdf"
plan_label = 'calibwithobstruction'
color = 'brown'

# Función para extraer el año de la fecha (formato "01JAN2011 01:00:00")
def extract_year(timestamp):
    try:
        date = datetime.strptime(timestamp, '%d%b%Y %H:%M:%S')
        return date.year
    except ValueError:
        print(f"Error al extraer el año de: {timestamp}")
        return None

# Procesar el plan y extraer fechas
print(f"\nProcesando plan: {plan_label} ({hdf_file})")
try:
    with h5py.File(hdf_file, 'r') as f:
        invert_elevation_data = \
            f['Results']['Unsteady']['Output']['Output Blocks']['Sediment']['Sediment Time Series']['Cross Sections'][
                'Invert Elevation']
        time_data = f['Results']['Unsteady']['Output']['Output Blocks']['Sediment']['Sediment Time Series'][
                        'Time Date Stamp'][:]
        time_stamps = [str(t.decode('utf-8')) if isinstance(t, bytes) else str(t) for t in time_data]
        plan_data = {'data': invert_elevation_data[:, :], 'label': plan_label, 'color': color, 'times': time_stamps}
except Exception as e:
    print(f"Error: {e}")
    exit(1)

# Verificar los años en los datos
years = [extract_year(t) for t in plan_data['times'] if extract_year(t) is not None]
print(f"Años cubiertos en los datos: {sorted(set(years))}")

# Calcular 10 índices uniformemente distribuidos, incluyendo el primero y el último
num_intervals = 20
data_length = len(plan_data['data'])
uniform_indices = np.linspace(0, data_length - 1, num_intervals, dtype=int)
print(f"Índices uniformes seleccionados: {uniform_indices.tolist()}")
print("Marcas temporales seleccionadas:")
for idx in uniform_indices:
    print(f"Índice {idx}: {plan_data['times'][idx]} (Año: {extract_year(plan_data['times'][idx])})")

observed_2018 = {
    'Invert_Elevation': [193.08, 175.62, 182.37, 145.27, 128.01, 107.38, 76.50, 88.56, 85.25, 82.26, 78.73, 64.64,
                         61.55, 76.38, 56.26, 67.76]
}
data_observed_2018 = pd.DataFrame(observed_2018)

# Configurar la figura
fig, ax = plt.subplots(figsize=(12, 8))
ax.set_ylabel('Elevación del Invert (m)')
ax.set_title('Cambio de Elevación del Invert a lo Largo del Tiempo - Guairá A-A')
ax.grid(True)
ax.invert_xaxis()
ax.set_xticks([])

# Línea para el plan (inicialmente vacía)
line = ax.plot([], [], label=plan_data['label'], color=plan_data['color'], linestyle='-', marker='o')[0]
# Línea para datos observados (estática)
ax.plot(data_observed_2018['Invert_Elevation'], label='Observado 2018 (LG-01)', color='black', linestyle=':',
        marker='o', linewidth=2)
# Línea inicial (estática) para referencia
initial_line = ax.plot(range(len(plan_data['data'][0])), plan_data['data'][0], label='Paso Inicial',
                       color='gray', linestyle='--', linewidth=1)[0]

# Dibujar la presa referencial en el lado derecho (trapezoidal)
n_sections = len(plan_data['data'][0])  # Número de secciones transversales
presa_x = [n_sections, n_sections - 0.20, n_sections - 0.30, n_sections - 0.5]  # Coordenadas X para un trapecio
presa_y = [50, 225, 225, 50]  # Coordenadas Y (cota 50 a 225)
ax.fill(presa_x, presa_y, color='gray', alpha=0.5, label='Presa Referencial')  # Relleno de la presa

ax.legend()

# Variable para el relleno (se actualizará en la animación)
fill = None
# Lista para almacenar las líneas de cada año (como tuplas: (año, línea))
year_lines = []
# Variable para rastrear el año anterior
last_year = None

# Función de inicialización
def init():
    global fill, last_year, year_lines
    line.set_data([], [])
    if fill is not None:
        fill.remove()  # Eliminar el relleno anterior si existe
    fill = ax.fill_between([], [], [], color='brown', alpha=0.3)  # Relleno inicial vacío
    # Limpiar las líneas de años anteriores
    for _, year_line in year_lines:
        year_line.remove()
    year_lines = []
    last_year = None
    return [line, fill] + [yl for _, yl in year_lines]

# Función de animación con 10 intervalos uniformes
def animate(frame):
    global fill, last_year, year_lines
    data_index = uniform_indices[frame]  # Usar índices uniformes
    if data_index < len(plan_data['data']):
        x = range(len(plan_data['data'][data_index]))
        line.set_data(x, plan_data['data'][data_index])
        if fill is not None:
            fill.remove()
        fill = ax.fill_between(x, plan_data['data'][0], plan_data['data'][data_index],
                               color='brown', alpha=0.3, label='Depósito/Erosión')
        current_time = plan_data['times'][data_index]
        ax.set_title(f'Cambio de Elevación del Invert - {current_time}')

        current_year = extract_year(current_time)
        if current_year is not None:
            if last_year is not None and current_year != last_year:
                print(f"Registrando línea para el año {last_year} en índice {data_index}")
                year_line = ax.plot(x, plan_data['data'][data_index], linestyle='-',
                                    linewidth=1, alpha=0.5, label=f'Año {last_year}')[0]
                year_lines.append((last_year, year_line))
            last_year = current_year

            # En el último frame, registrar la línea para el año actual (2100)
            if frame == num_intervals - 1 and current_year is not None:
                print(f"Registrando línea para el año {current_year} en índice {data_index} (último frame)")
                year_line = ax.plot(x, plan_data['data'][data_index], linestyle='-',
                                    linewidth=1, alpha=0.5, label=f'Año {current_year}')[0]
                year_lines.append((current_year, year_line))

        # Actualizar la leyenda en cada frame
        ax.legend()

        # Guardar el frame como PNG
        output_png = f'frame_{frame}.png'
        plt.savefig(output_png, dpi=300, bbox_inches='tight')
        print(f"Guardado {output_png}")

    return [line, fill] + [yl for _, yl in year_lines]

# Crear la animación con 10 frames
ani = FuncAnimation(fig, animate, frames=num_intervals, init_func=init, blit=False, interval=1000)  # Desactivar blit para PNGs

# Guardar la animación como GIF
output_gif = 'invert_elevation_animation_10_intervals_with_first_last.gif'
ani.save(output_gif, writer='pillow', fps=1)  # 1 fps para que cada intervalo dure 1 segundo
print(f"Animación guardada como {output_gif}")

# Convertir GIF a MP4
gif_path = 'invert_elevation_animation_10_intervals_with_first_last.gif'
mp4_path = 'invert_elevation_animation_10_intervals_with_first_last.mp4'

# Abrir el GIF
gif = Image.open(gif_path)

# Obtener tamaño y frames
width, height = gif.size
frames = []

# Extraer cada cuadro del GIF
try:
    while True:
        frame = gif.convert('RGB')  # Convertir a formato RGB
        frame_np = np.array(frame)
        frame_bgr = cv2.cvtColor(frame_np, cv2.COLOR_RGB2BGR)  # Convertir a BGR para OpenCV
        frames.append(frame_bgr)
        gif.seek(gif.tell() + 1)
except EOFError:
    pass  # Fin del GIF

# Crear el archivo de video
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec para MP4
fps = 1  # 1 fps para coincidir con el GIF
out = cv2.VideoWriter(mp4_path, fourcc, fps, (width, height))

# Escribir cada frame
for frame in frames:
    out.write(frame)

# Finalizar
out.release()
print(f"✅ GIF convertido exitosamente a MP4: {mp4_path}")