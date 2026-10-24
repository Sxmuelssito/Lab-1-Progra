"""Etapa de carga de varios experimentos."""

from pathlib import Path

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline
from models.observacion import Observacion


experimentos_25fps = [1, 2, 3, 4, 5, 6, 7, 8, 9]
experimentos_16fps = [1, 3, 4, 5, 6, 7, 8, 9]

fps_x_defecto = 25


class CargaExperimentos(EtapaPipeline[None, list[Experimento]]):
    """Carga una colección de experimentos desde la ruta configurada."""

    def ejecutar(self, entrada: None, contexto: ContextoPipeline,) -> list[Experimento]:
        """Carga los experimentos indicados por la configuración."""
        experimentos = self._cargar_experimentos(contexto.ruta_entrada)
        print()
        print(f"Se encontraron {len(experimentos)} experimentos")
        for experimento in experimentos:
            print(f"Se cargó el experimento {experimento.nombre} con {len(experimento.observaciones)} observaciones")

        if contexto.fps is None:
            if self.fps_archivo is None:
                contexto.fps = fps_por_defecto
                print(f"No se indicó --fps ni aparece en los archivos: se usa {contexto.fps}")
            else:
                contexto.fps = self.fps_archivo
                print(f"No se indicó --fps: se usa el de los archivos ({contexto.fps})")
        elif self.fps_archivo is not None and contexto.fps != self.fps_archivo:
            print(f"ADVERTENCIA: se indicó --fps {contexto.fps}, pero los archivos dicen {self.fps_archivo}")
        return experimentos

    def _cargar_experimentos(self, ruta_entrada: Path) -> list[Experimento]:
        """Carga los experimentos disponibles en la ruta recibida."""
        self.fps_archivo = None
        carpeta = str(ruta_entrada)
        experimentos = []
        if carpeta == "data_16fps":
            nombres = [f"uni_corr_500_{numero}.txt" for numero in experimentos_16fps]
        else:
            nombres = [f"UNI_CORR_500_0{numero}.txt" for numero in experimentos_25fps]
        for nombre in nombres:
            ruta_archivo = carpeta + "/" + nombre
            experimentos.append(self.leer_archivo(ruta_archivo, nombre))
        return experimentos

    def leer_archivo(self, ruta_archivo, nombre):
        observaciones = []
        arch = open(ruta_archivo, 'r')
        for linea in arch:
            linea = linea.strip()
            if linea.startswith("# framerate"):
                partes = linea.split()
                self.fps_archivo = float(partes[-1])
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
        arch.close()
        nombre_experimento = nombre.replace(".txt", "")
        return Experimento(nombre = nombre_experimento, observaciones=observaciones)
