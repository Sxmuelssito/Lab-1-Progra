"""Etapa de preparación de observaciones y trayectorias."""

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa validación, organización y reconstrucción de trayectorias."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        """Prepara las observaciones y trayectorias de cada experimento."""
        for experimento in experimentos: 
            organizadas = self._organizar_observaciones(experimento.observaciones)
            experimento.trayectorias = self._reconstruir_trayectorias(organizadas)
            print(f"{experimento.nombre}: {len(experimento.trayectorias)} trayectorias")
        return experimentos

    def _validar_observaciones(self, observaciones: list[Observacion],) -> list[Observacion]:
        """Valida y retorna las observaciones de un experimento."""
        raise NotImplementedError

    def _organizar_observaciones(self, observaciones: list[Observacion],) -> dict[int, list[Observacion]]:
        """Organiza las observaciones por identificador de peatón."""
        organizadas = {}
        for obs in observaciones:
            if obs.id_peaton not in organizadas: 
                organizadas[obs.id_peaton] = []
            organizadas[obs.id_peaton].append(obs)

        for id_peaton in organizadas:
            organizadas[id_peaton].sort(key=lambda obs: obs.frame)

        return organizadas

    def _reconstruir_trayectorias(self, observaciones_organizadas: dict[int, list[Observacion]],) -> list[Trayectoria]:
        """Construye trayectorias desde las observaciones organizadas."""
        trayectorias = []
        for id_peaton in observaciones_organizadas:
            lista = observaciones_organizadas[id_peaton]
            if len(lista) >= 2:
                trayectoria = Trayectoria(id_peaton=id_peaton, observaciones=lista)
                trayectorias.append(trayectoria)
                
        return trayectorias
    
