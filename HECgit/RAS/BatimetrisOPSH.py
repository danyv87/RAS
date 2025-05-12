import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import geopandas as gpd
from shapely.geometry import LineString, Point
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.cm as cm

# Ruta del archivo de datos de batimetría y shapefile
file_path = r"C:\Users\danielal\Downloads\Batimetrias_1997-A-2018_solopuntos.xlsx"
shapefile_path = r'C://Users//danielal//OneDrive - ITAIPU Binacional//CIH//Proyectos//HIDRO//Modelación Hidromorfologica//RAS-Embalse//Shps//ContornoEmbalse4.shp'

# Cargar el archivo Excel
df = pd.read_excel(file_path, sheet_name=None)

# Cargar el shapefile usando geopandas
gdf = gpd.read_file(shapefile_path)

# Establecer estilo de gráficos (opcional)
sns.set(style="whitegrid")

# Lista de años disponibles
years_available = sorted(list(df.keys()), key=int)

# Obtener perfiles disponibles
all_perfiles = set()
for year in years_available:
    if 'Perfil' in df[year].columns:
        all_perfiles.update(df[year]['Perfil'].dropna().unique())
all_perfiles = sorted(list(all_perfiles))

# Diccionario de tonalidades y marcadores para cada año
n_years = len(years_available)
colors = cm.Blues(np.linspace(0.3, 0.9, n_years))
year_styles = {year: {'color': colors[i], 'marker': ['o', 's', '^', 'd', 'v'][i % 5]}
               for i, year in enumerate(years_available)}

# Crear la ventana principal de tkinter
root = tk.Tk()
root.title("Selección de Años y Perfiles")
root.geometry("1200x800")
root.minsize(800, 600)

# Variables para la selección
selected_years = tk.StringVar(value="2014,2018")
selected_perfil = tk.StringVar(value="LG-16")

# Crear la figura de Matplotlib
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 4), constrained_layout=True)

# Crear el canvas y la barra de herramientas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
toolbar = NavigationToolbar2Tk(canvas, root)
toolbar.update()
canvas._tkcanvas.pack()

# Función para actualizar el gráfico
def update_graph():
    ax1.clear()
    ax2.clear()
    ax3.clear()
    years = [y.strip() for y in selected_years.get().split(",") if y.strip()]
    plot_data(years)

# Función para graficar los datos y imprimir elevaciones
def plot_data(years):
    # Graficar la geometría del shapefile en el primer subgráfico
    gdf.plot(ax=ax1, color='lightblue', edgecolor='black', alpha=0.5, label='Contorno Embalse')

    # Listas para rastrear si se graficó algo en cada eje
    plotted_ax1 = False
    plotted_ax2 = False
    plotted_ax3 = False

    # Iterar sobre los años seleccionados
    for year in years:
        data = df.get(year)
        if data is not None and 'Este' in data.columns and 'Norte' in data.columns and 'Cota' in data.columns:
            data = data.sort_values(by='Norte', ascending=True)
            talweg_data = data.loc[data.groupby('Perfil')['Cota'].idxmin()]
            talweg_sorted = talweg_data.sort_values(by='Norte', ascending=True)

            # Obtener estilo para el año
            style = year_styles.get(year, {'color': 'gray', 'marker': 'o'})

            # Graficar en el primer subgráfico (planta)
            ax1.scatter(data['Este'], data['Norte'], color=style['color'], alpha=0.5,
                       label=f'Puntos Año {year}', marker=style['marker'], s=10)
            ax1.scatter(talweg_data['Este'], talweg_data['Norte'], color=style['color'],
                       label=f'Talweg Año {year}', edgecolor='black', marker=style['marker'], s=50)
            ax1.plot(talweg_sorted['Este'], talweg_sorted['Norte'], color=style['color'],
                    label=f'Talweg Continuo {year}', linewidth=2)
            plotted_ax1 = True

            # Graficar el perfil longitudinal y preparar datos para imprimir
            talweg_df = talweg_sorted[['Norte', 'Cota']].copy()
            ax2.plot(talweg_df['Norte'], talweg_df['Cota'], color=style['color'], label=f'Cota Año {year}')
            plotted_ax2 = True

            # Imprimir las elevaciones del perfil longitudinal
            print(f"\nElevaciones del perfil longitudinal (Talweg) para el año {year}:")
            print(talweg_df.to_string(index=False))

            # Graficar la sección transversal del perfil seleccionado
            perfil = selected_perfil.get()
            perfil_data = data[data['Perfil'] == perfil]
            if not perfil_data.empty:
                perfil_sorted = perfil_data.sort_values(by='Este', ascending=True)
                ax3.plot(perfil_sorted['Este'], perfil_sorted['Cota'],
                        label=f'Año {year} - Perfil {perfil}')
                plotted_ax3 = True
            else:
                print(f"El perfil {perfil} no existe en los datos del año {year}.")
        else:
            print(f"Datos no disponibles o columnas faltantes para el año {year}.")

    # Configurar los subgráficos con leyendas ajustadas
    ax1.set_xlabel('Coordenada Este')
    ax1.set_ylabel('Coordenada Norte')
    ax1.set_title('Planta General con Talweg')
    if plotted_ax1:
        ax1.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    ax2.set_xlabel('Coordenada Norte')
    ax2.set_ylabel('Cota')
    ax2.set_title('Perfil Longitudinal a lo largo del Talweg')
    ax2.axhline(y=220, color='red', linestyle='--', label='Pelo de Agua (Cota 220)')
    if plotted_ax2:
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    ax3.set_xlabel('Coordenada Este (Derecha a Izquierda)')
    ax3.set_ylabel('Cota')
    ax3.set_title(f'Sección Transversal - Perfil {selected_perfil.get()}')
    if plotted_ax3:
        ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0.)

    # Invertir el eje X del tercer gráfico
    ax3.invert_xaxis()
    canvas.draw()

# Crear el campo de entrada para años
tk.Label(root, text="Seleccionar Años (separar con coma, ej. 2014,2018):").pack()
tk.Entry(root, textvariable=selected_years, width=30).pack()

# Crear el menú desplegable para perfiles
tk.Label(root, text="Seleccionar Perfil:").pack()
perfil_menu = tk.OptionMenu(root, selected_perfil, *all_perfiles)
perfil_menu.pack()

# Botón para actualizar el gráfico
tk.Button(root, text="Actualizar Gráfico", command=update_graph).pack()

# Hacer la ventana redimensionable
root.mainloop()

print("ok")