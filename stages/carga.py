"""Etapa de carga de varios experimentos."""

from pathlib import Path

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from models.observacion import Observacion

numero_experimentos = [5]


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Carga una colección de experimentos desde la ruta configurada."""

    def ejecutar(self, entrada: None, contexto: ContextoPipeline,) -> list[Experimento]:
        """Carga los experimentos indicados por la configuración."""
        experimentos = self._cargar_experimentos(contexto.ruta_entrada)
        print()
        print(f"Se encotraron {len(experimentos)} experimentos")
        for experimento in experimentos:
            print(f"Se cargó el experimento {experimento.nombre} con {len(experimento.observaciones)} observaciones")
        return experimentos

    def _cargar_experimentos(self, ruta_entrada: Path) -> list[Experimento]:
        """Carga los experimentos disponibles en la ruta recibida."""
        carpeta = str(ruta_entrada)
        experimentos = []
        if carpeta == 'data':
            nombres = [f"UNI_CORR_500_0{numero}.txt" for numero in numero_experimentos]
        else:
            nombres = [f"uni_corr_500_{numero}.txt" for numero in numero_experimentos]

        for nombre in nombres: 
            ruta_archivo = carpeta + "/" + nombre
            experimentos.append(self.leer_archivo(ruta_archivo, nombre))
        return experimentos

    def leer_archivo(self, ruta_archivo, nombre):
        observaciones = []
        arch = open(ruta_archivo, 'r')
        for linea in arch:
            linea = linea.strip()
            if linea != "" and not linea.startswith("#"):
                partes = linea.split()
                if len(partes) == 5: 
                    observacion = Observacion(
                        id_peaton = int(partes[0]),
                        frame = int(partes[1]),
                        x = float(partes[2]),
                        y = float(partes[3]),
                        z = float(partes[4]),
                    )
                    observaciones.append(observacion)  
        nombre_experimento = nombre.replace(".txt", "")
        return Experimento(nombre = nombre_experimento, observaciones=observaciones)