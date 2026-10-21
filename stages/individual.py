"""Etapa de análisis individual de los experimentos."""

from models.experimento import Experimento
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

umbral_detencion = 0.2
duracion_minima_detencion = 0.5


class AnalisisIndividual(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Coordina el análisis de múltiples trayectorias y reúne sus indicadores."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline,) -> list[Experimento]:
        """Analiza las trayectorias de cada experimento."""
        for experimento in experimentos:
            for trayectoria in experimento.trayectorias:
                indicadores = self._calcular_indicadores(trayectoria, contexto.fps)
                experimento.resultados_individuales[trayectoria.id_peaton] = indicadores
            print(f"{experimento.nombre}: indicadores de {len(experimento.resultados_individuales)} peatones")
        return experimentos        


    def _calcular_indicadores(self, trayectoria: Trayectoria, fps: float | None,) -> dict[str, float]:
        """Calcula los indicadores individuales de una trayectoria."""
        inicial = trayectoria.obtener_posicion_inicial()
        final = trayectoria.obtener_posicion_final()
        tiempo_total = trayectoria.calcular_tiempo_total_ob(fps)

        detenciones = self._detectar_detenciones(trayectoria,fps)
        tiempo_detenido = 0
        for inicio, fin in detenciones: 
            tiempo_detenido += (fin - inicio) / fps
        if tiempo_total > 0: 
            porcentaje_detenido = 100*tiempo_detenido /tiempo_total
        else: 
            porcentaje_detenido = 0

        return {
            "x_inicial": inicial[0],
            "y_inicial": inicial[1],
            "x_final": final[0],
            "y_final": final[1],
            "tiempo_total_s": tiempo_total,
            "distancia_total_m": trayectoria.calcular_distancia_total(),
            "desplazamiento_m": trayectoria.calcular_desplazamiento(),
            "velocidad_media_m_s": trayectoria.calcular_velocidad_media(fps),
            "velocidad_maxima_m_s": trayectoria.velocidad_max(fps),
            "eficiencia": trayectoria.calcular_eficiencia(),
            "cantidad_detenciones": len(detenciones),
            "tiempo_detenido_s": tiempo_detenido,
            "porcentaje_detenido": porcentaje_detenido,
        }


    def _detectar_detenciones(self, trayectoria: Trayectoria, fps: float | None,) -> list[tuple[int, int]]:
        """Identifica intervalos de detención de una trayectoria."""
        velocidades = trayectoria.calcular_velocidades(fps)
        obs = trayectoria.observaciones
        detenciones = []
        inicio = None
        fin = None 
        for i in range(len(velocidades)):
            if velocidades[i] < umbral_detencion:
                if inicio is None:
                    inicio = obs[i].frame
                fin = obs[i+1].frame
            else: 
                if inicio is not None:
                    if (fin-inicio) / fps >= duracion_minima_detencion:
                        detenciones.append((inicio,fin))
                inicio = None
        if inicio is not None:
            if (fin-inicio) / fps >= duracion_minima_detencion:
                detenciones.append((inicio,fin))
        return detenciones
