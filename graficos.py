import os
import matplotlib.pyplot as plt

carpeta_25 = "results"
carpeta_16 = "results_16fps"
carpeta_salida = "graficos"

color_25 = "#2a78d6"   
color_16 = "#eb6834"   

def leer_tabla(ruta):
    arch = open(ruta, "r")
    lineas = arch.readlines()
    arch.close()
    encabezados = lineas[0].strip().split(",")
    filas = []
    for linea in lineas[1:]:
        valores = linea.strip().split(",")
        fila = {}
        for i in range(len(encabezados)):
            fila[encabezados[i]] = valores[i]
        filas.append(fila)
    return filas

def leer_indicadores(ruta):
    filas = leer_tabla(ruta)
    resultado = {}
    for fila in filas:
        resultado[fila["indicador"]] = float(fila["valor"])
    return resultado

def numero_experimento(nombre):
    return int(nombre.split("_")[-1])

def columna(filas, nombre):
    return [float(fila[nombre]) for fila in filas]

comparacion_25 = leer_tabla(carpeta_25 + "/comparacion_experimentos.csv")
comparacion_16 = leer_tabla(carpeta_16 + "/comparacion_experimentos.csv")
os.makedirs(carpeta_salida, exist_ok=True)

def ventanas(carpeta, filas):
    densidades = []
    velocidades = []
    for fila in filas:
        r = leer_indicadores(carpeta + "/" + fila["experimento"] + "_colectivo.csv")
        n = int(r["num_ventanas_densidad"])
        maxima = max([r[f"ventana_{k}_densidad_p_m2"] for k in range(n)])
        for k in range(n):
            rho = r[f"ventana_{k}_densidad_p_m2"]
            v = r[f"ventana_{k}_velocidad_m_s"]
            if rho >= 0.5 * maxima and v > 0:
                densidades.append(rho)
                velocidades.append(v)
    return densidades, velocidades

def correlacion(xs, ys):
    n = len(xs)
    media_x = sum(xs) / n
    media_y = sum(ys) / n
    covarianza = sum([(xs[i] - media_x) * (ys[i] - media_y) for i in range(n)])
    desv_x = sum([(x - media_x) ** 2 for x in xs]) ** 0.5
    desv_y = sum([(y - media_y) ** 2 for y in ys]) ** 0.5
    return covarianza / (desv_x * desv_y)


def flujo_por_ventana(carpeta, filas):
    densidades = []
    flujos = []
    for fila in filas:
        r = leer_indicadores(carpeta + "/" + fila["experimento"] + "_colectivo.csv")
        ventanas_densidad = [(r[f"ventana_{k}_inicio_s"], r[f"ventana_{k}_densidad_p_m2"])
                            for k in range(int(r["num_ventanas_densidad"]))]
        maxima = max([rho for inicio_d, rho in ventanas_densidad])
        for k in range(int(r["num_ventanas_flujo"])):
            inicio = r[f"flujo_ventana_{k}_inicio_s"]
            segundos_total = 0
            suma = 0
            for inicio_d, rho in ventanas_densidad:
                comun = min(inicio_d + 10, inicio + 10) - max(inicio_d, inicio)
                if comun > 0:
                    segundos_total = segundos_total + comun
                    suma = suma + comun * rho
            # al menos 5 s de densidad medida y dentro del período estacionario
            if segundos_total > 5 and suma / segundos_total >= 0.5 * maxima:
                densidades.append(suma / segundos_total)
                flujos.append(r[f"flujo_ventana_{k}_p_s"])
    return densidades, flujos

def promedio_por_tramo(xs, ys, ancho=0.5, minimo=5):
    tramos = {}
    for i in range(len(xs)):
        centro = round(xs[i] / ancho) * ancho
        if centro not in tramos:
            tramos[centro] = []
        tramos[centro].append(ys[i])
    centros = sorted([c for c in tramos if len(tramos[c]) >= minimo])
    promedios = [sum(tramos[c]) / len(tramos[c]) for c in centros]
    return centros, promedios

rho_25, v_25 = ventanas(carpeta_25, comparacion_25)
rho_16, v_16 = ventanas(carpeta_16, comparacion_16)
todas_rho = rho_25 + rho_16
todas_v = v_25 + v_16
r = correlacion(todas_rho, todas_v)
print(f"Correlación densidad-velocidad: r = {r:.2f} ({len(todas_rho)} ventanas de 10 s)")
centros, promedios = promedio_por_tramo(todas_rho, todas_v)
 
plt.figure(figsize=(7, 4.5))
plt.scatter(rho_25, v_25, color=color_25, s=14, alpha=0.45, label="Ventana de 10 s (25 fps)")
plt.scatter(rho_16, v_16, color=color_16, s=14, alpha=0.45, marker="s", label="Ventana de 10 s (16 fps)")
plt.plot(centros, promedios, color="black", linewidth=2, marker="o", label="Promedio por tramo de 0,5 p/m²")
plt.xlabel("Densidad en el área de medición (personas/m²)")
plt.ylabel("Velocidad en el área de medición (m/s)")
plt.title(f"A mayor densidad, menor velocidad (r = {r:.2f})".replace(".", ","))
plt.xlim(0, 4)
plt.ylim(0, 1.9)
plt.grid(alpha=0.3)
plt.legend(fontsize=8)
plt.savefig(carpeta_salida + "/figura6_velocidad_densidad.png", dpi=200, bbox_inches="tight")
plt.close()

rho_f25, j_25 = flujo_por_ventana(carpeta_25, comparacion_25)
rho_f16, j_16 = flujo_por_ventana(carpeta_16, comparacion_16)
centros, promedios = promedio_por_tramo(rho_f25 + rho_f16, j_25 + j_16)
print(f"Diagrama fundamental: {len(rho_f25) + len(rho_f16)} ventanas de 10 s")
for i in range(len(centros)):
    print(f"  densidad ~{centros[i]:.1f} p/m2 -> flujo promedio {promedios[i]:.1f} p/s")

plt.figure(figsize=(7, 4.5))
plt.scatter(rho_f25, j_25, color=color_25, s=14, alpha=0.45, label="Ventana de 10 s (25 fps)")
plt.scatter(rho_f16, j_16, color=color_16, s=14, alpha=0.45, marker="s", label="Ventana de 10 s (16 fps)")
plt.plot(centros, promedios, color="black", linewidth=2, marker="o", label="Promedio por tramo de 0,5 p/m²")
plt.xlabel("Densidad en el área de medición (personas/m²)")
plt.ylabel("Flujo en la línea central (personas/s)")
plt.title("Diagrama fundamental: el flujo máximo ocurre cerca de 1,5 p/m²")
plt.xlim(0, 4)
plt.ylim(0, 9)
plt.grid(alpha=0.3)
plt.legend(fontsize=8)
plt.savefig(carpeta_salida + "/figura7_diagrama_fundamental.png", dpi=200, bbox_inches="tight")
plt.close()

fig, (arriba, abajo) = plt.subplots(2, 1, figsize=(7, 6), sharex=True)
colores = {3: "#6da7ec", 6: "#256abf", 9: "#0d366b"}
for numero in [3, 6, 9]:
    r = leer_indicadores(carpeta_16 + f"/uni_corr_500_{numero}_colectivo.csv")

    # densidad cada 10 s
    n = int(r["num_ventanas_densidad"])
    inicio = r["ventana_0_inicio_s"]
    tiempos = [r[f"ventana_{k}_inicio_s"] - inicio for k in range(n)]
    densidades = [r[f"ventana_{k}_densidad_p_m2"] for k in range(n)]
    arriba.plot(tiempos, densidades, color=colores[numero], linewidth=2, label=f"Exp. {numero}")

    # flujo cada 10 s
    n = int(r["num_ventanas_flujo"])
    inicio = r["flujo_ventana_0_inicio_s"]
    tiempos = [r[f"flujo_ventana_{k}_inicio_s"] - inicio for k in range(n)]
    flujos = [r[f"flujo_ventana_{k}_p_s"] for k in range(n)]
    abajo.plot(tiempos, flujos, color=colores[numero], linewidth=2, label=f"Exp. {numero}")

arriba.set_ylabel("Densidad (p/m²)")
arriba.set_title("Densidad cada 10 s (16 fps)")
arriba.grid(alpha=0.3)
arriba.set_ylim(0, 4.5)
arriba.legend(loc="upper center", ncol=3)
abajo.set_ylabel("Flujo (p/s)")
abajo.set_xlabel("Tiempo desde el inicio (s)")
abajo.set_title("Flujo cada 10 s (16 fps)")
abajo.grid(alpha=0.3)
abajo.set_ylim(0, 9.5)
abajo.legend(loc="upper center", ncol=3)
fig.tight_layout()
fig.savefig(carpeta_salida + "/figura8_series_tiempo.png", dpi=200, bbox_inches="tight")
plt.close(fig)

plt.figure(figsize=(7, 4))
for filas, color, desplazamiento, etiqueta in [(comparacion_25, color_25, -0.2, "25 fps"),
                                                (comparacion_16, color_16, 0.2, "16 fps")]:
    numeros = [numero_experimento(fila["experimento"]) + desplazamiento for fila in filas]
    porcentajes = [100 * float(fila["peatones_con_detenciones"]) / float(fila["cantidad_peatones"]) for fila in filas]
    plt.bar(numeros, porcentajes, width=0.38, color=color, label=etiqueta)
plt.xticks(range(1, 10))
plt.xlabel("Experimento")
plt.ylabel("% de peatones")
plt.title("Peatones con al menos una detención")
plt.ylim(0, 100)
plt.grid(axis="y", alpha=0.3)
plt.legend()
plt.savefig(carpeta_salida + "/figura4_detenciones.png", dpi=200, bbox_inches="tight")
plt.close()

velocidades = []
eficiencias = []
etiquetas = []
for fila in comparacion_16:
    filas = leer_tabla(carpeta_16 + "/" + fila["experimento"] + "_individual.csv")
    velocidades.append(columna(filas, "velocidad_media_m_s"))
    eficiencias.append(columna(filas, "eficiencia"))
    etiquetas.append(str(numero_experimento(fila["experimento"])))

fig, (izq, der) = plt.subplots(1, 2, figsize=(9, 4))
izq.boxplot(velocidades, showfliers=False)
izq.set_xticks(range(1, len(etiquetas) + 1))
izq.set_xticklabels(etiquetas)
izq.set_xlabel("Experimento (16 fps)")
izq.set_ylabel("m/s")
izq.set_title("Velocidad media por peatón")
izq.grid(alpha=0.3)
der.boxplot(eficiencias, showfliers=False)
der.set_xticks(range(1, len(etiquetas) + 1))
der.set_xticklabels(etiquetas)
der.set_xlabel("Experimento (16 fps)")
der.set_ylabel("E = D / Dr")
der.set_title("Eficiencia por peatón")
der.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(carpeta_salida + "/figura3_individual.png", dpi=200, bbox_inches="tight")
plt.close(fig)

fig, ejes = plt.subplots(1, 2, figsize=(9, 4.5))
for eje, carpeta, filas, titulo in [(ejes[0], carpeta_25, comparacion_25, "Cámara de 25 fps"),
                                    (ejes[1], carpeta_16, comparacion_16, "Cámara de 16 fps")]:
    matriz = []       # una fila por experimento, una columna por zona
    numeros = []
    for fila in filas:
        r = leer_indicadores(carpeta + "/" + fila["experimento"] + "_colectivo.csv")
        matriz.append([r[f"zona_{z}_velocidad_relativa"] for z in range(5)])
        numeros.append(numero_experimento(fila["experimento"]))
    imagen = eje.imshow(matriz, cmap="RdBu", vmin=0.7, vmax=1.3, aspect="auto")
    for i in range(len(matriz)):
        for z in range(5):
            eje.text(z, i, f"{matriz[i][z]:.2f}", ha="center", va="center", fontsize=8)
    eje.set_xticks(range(5))
    eje.set_xticklabels(["0\nentrada", "1", "2", "3", "4\nsalida"])
    eje.set_yticks(range(len(numeros)))
    eje.set_yticklabels(numeros)
    eje.set_ylabel("Experimento")
    eje.set_title(titulo)
fig.colorbar(imagen, ax=ejes, label="Velocidad de la zona / velocidad general")
fig.savefig(carpeta_salida + "/figura5_zonas.png", dpi=200, bbox_inches="tight")
plt.close(fig)

datos_16 = {}
for fila in comparacion_16:
    datos_16[numero_experimento(fila["experimento"])] = fila

fig, (izq, der) = plt.subplots(1, 2, figsize=(9, 4))
for eje, clave, titulo, limite in [(izq, "densidad_media_p_m2", "Densidad media (p/m²)", 3.2),
                                (der, "flujo_p_s", "Flujo (p/s)", 7)]:
    eje.plot([0, limite], [0, limite], color="gray", linestyle="--")   # línea de igualdad
    for fila in comparacion_25:
        numero = numero_experimento(fila["experimento"])
        if numero in datos_16:
            x = float(fila[clave])
            y = float(datos_16[numero][clave])
            if numero == 8 or numero == 9:
                color = "#d03b3b"   # rojo: grabación de 25 fps incompleta
            else:
                color = color_25
            eje.scatter(x, y, color=color, s=50)
            eje.annotate(str(numero), (x, y), xytext=(5, 3), textcoords="offset points")
    eje.set_xlim(0, limite)
    eje.set_ylim(0, limite)
    eje.set_xlabel("Cámara de 25 fps")
    eje.set_ylabel("Cámara de 16 fps")
    eje.set_title(titulo)
    eje.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(carpeta_salida + "/figura9_camaras.png", dpi=200, bbox_inches="tight")
plt.close(fig)

print(f"Gráficos guardados en la carpeta {carpeta_salida}/")