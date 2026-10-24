"""Etapa de comparación de experimentos."""

from models.experimento import Experimento
from models.resultado_analisis import ResultadoAnalisis
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class ComparacionExperimentos(EtapaPipeline[list[Experimento], ResultadoAnalisis]):
    """Compara resultados de varios experimentos."""
   

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline,) -> ResultadoAnalisis:
        """Retorna los experimentos junto con sus resultados comparativos."""
        for experimento in experimentos:
            self._resumir(experimento)
        comparacion = self._comparar(experimentos)

        print("Experimentos ordenados de menor a mayor densidad:")
        ordenados = sorted(experimentos, key=lambda e: e.resultados_colectivos["densidad_media_p_m2"])
        for e in ordenados:
            r = e.resultados_colectivos
            print(f"  {e.nombre}: densidad {round(r['densidad_media_p_m2'], 2)} p/m², velocidad {round(r['velocidad_media_m_s'], 2)} m/s, flujo {round(r['flujo_p_s'], 2)} p/s")
        return ResultadoAnalisis(experimentos=experimentos, comparacion=comparacion)

    def _promedio_individual(self, experimento: Experimento, clave: str) -> float:
        """Promedio de un indicador individual entre todos los peatones del experimento."""
        valores = [indicadores[clave] for indicadores in experimento.resultados_individuales.values()]
        if len(valores) == 0:
            return 0
        return sum(valores) / len(valores)        

    def _promedio_individual(self, experimento, clave):
        valores = [indicadores[clave] for indicadores in experimento.resultados_individuales.values()]
        if len(valores) == 0:
            return 0
        return sum(valores) / len(valores)

    def _resumir(self, experimento): 
        resultados = experimento.resultados_colectivos
        resultados["cantidad_peatones"] = len(experimento.trayectorias)
        resultados["velocidad_media_m_s"] = self._promedio_individual(experimento, "velocidad_media_m_s")
        resultados["distancia_media_m"] = self._promedio_individual(experimento, "distancia_total_m")
        resultados["tiempo_medio_s"] = self._promedio_individual(experimento, "tiempo_total_s")
        resultados["eficiencia_media"] = self._promedio_individual(experimento, "eficiencia")
        resultados["porcentaje_detenido_medio"] = self._promedio_individual(experimento, "porcentaje_detenido")
        con_detenciones = list(filter(lambda d: d["cantidad_detenciones"] > 0, experimento.resultados_individuales.values()))
        resultados["peatones_con_detenciones"] = len(con_detenciones)

    def _comparar(self, experimentos: list[Experimento]) -> dict[str, float]:
        por_densidad = sorted(experimentos, key=lambda e: e.resultados_colectivos["densidad_media_p_m2"])
        menos_denso = por_densidad[0].resultados_colectivos
        mas_denso = por_densidad[-1].resultados_colectivos

        por_flujo = sorted(experimentos, key=lambda e: e.resultados_colectivos["flujo_p_s"])
        mayor_flujo = por_flujo[-1].resultados_colectivos

        velocidades = [e.resultados_colectivos["velocidad_media_m_s"] for e in experimentos]
        return {
            "cantidad_experimentos": len(experimentos),
            "velocidad_media_todos_m_s": sum(velocidades) / len(velocidades),
            "densidad_menor_p_m2": menos_denso["densidad_media_p_m2"],
            "densidad_mayor_p_m2": mas_denso["densidad_media_p_m2"],
            "velocidad_con_menor_densidad_m_s": menos_denso["velocidad_media_m_s"],
            "velocidad_con_mayor_densidad_m_s": mas_denso["velocidad_media_m_s"],
            "flujo_con_menor_densidad_p_s": menos_denso["flujo_p_s"],
            "flujo_con_mayor_densidad_p_s": mas_denso["flujo_p_s"],
            "flujo_maximo_p_s": mayor_flujo["flujo_p_s"],
            "densidad_con_flujo_maximo_p_m2": mayor_flujo["densidad_media_p_m2"],
        }