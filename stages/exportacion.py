"""Etapa de exportación de resultados."""

from pathlib import Path

from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


columnas_comparacion = [
    "cantidad_peatones",
    "densidad_media_p_m2",
    "densidad_maxima_p_m2",
    "velocidad_media_m_s",
    "flujo_p_s",
    "distancia_media_m",
    "tiempo_medio_s",
    "eficiencia_media",
    "porcentaje_detenido_medio",
    "peatones_con_detenciones",    
]

class ExportacionResultados(EtapaPipeline[ResultadoAnalisis, None]):
    """Exporta los resultados de los experimentos y su comparación."""

    def ejecutar(self, resultados: ResultadoAnalisis, contexto: ContextoPipeline,) -> None:
        """Guarda los resultados en la ruta de salida configurada."""
        self._exportar(resultados, contexto.ruta_salida)
        print(f"Resultados guardados en la carpeta {contexto.ruta_salida}")
    
    def _exportar(self, resultados: ResultadoAnalisis, ruta_salida: Path) -> None:
        """Exporta los resultados a la ruta indicada."""
        ruta_salida.mkdir(parents=True, exist_ok=True)
        carpeta = str(ruta_salida)

        filas = []
        for experimento in resultados.experimentos:
            fila = [experimento.nombre] + [experimento.resultados_colectivos[c] for c in columnas_comparacion]
            filas.append(fila)
        self._escribir_csv(carpeta + "/comparacion_experimentos.csv", ["experimento"] + columnas_comparacion, filas)

        filas = [[clave, resultados.comparacion[clave]] for clave in resultados.comparacion]
        self._escribir_csv(carpeta + "/comparacion_general.csv", ["indicador", "valor"], filas)


        for experimento in resultados.experimentos:
            individuales = experimento.resultados_individuales
            primer_peaton = list(individuales.keys())[0]
            columnas = list(individuales[primer_peaton].keys())
            filas = []
            for id_peaton in individuales:
                fila = [id_peaton] + [individuales[id_peaton][c] for c in columnas]
                filas.append(fila)
            self._escribir_csv(carpeta + "/" + experimento.nombre + "_individual.csv", ["id_peaton"] + columnas, filas)


            colectivos = experimento.resultados_colectivos
            filas = [[clave, colectivos[clave]] for clave in colectivos]
            self._escribir_csv(carpeta + "/" + experimento.nombre + "_colectivo.csv", ["indicador", "valor"], filas)

    def _escribir_csv(self, ruta_archivo, encabezados, filas):
        arch = open(ruta_archivo, 'w')
        arch.write(",".join(encabezados) + "\n")
        for fila in filas:
            textos = []
            for valor in fila: 
                if type(valor) == float:
                    valor = round(valor, 4)
                textos.append(str(valor))
            arch.write(",".join(textos) + "\n")
        arch.close()