"""Etapa de preparación de observaciones y trayectorias."""

from models.experimento import Experimento
from models.observacion import Observacion
from models.trayectoria import Trayectoria
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

velocidad_maxima_valida = 7


class PreparacionTrayectorias(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa validación, organización y reconstrucción de trayectorias."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline) -> list[Experimento]:
        """Prepara las observaciones y trayectorias de cada experimento."""
        self.fps = contexto.fps 
        for experimento in experimentos: 
            validas = self._validar_observaciones(experimento.observaciones)
            descartadas = len(experimento.observaciones) - len(validas)
            organizadas = self._organizar_observaciones(validas)
            experimento.trayectorias = self._reconstruir_trayectorias(organizadas)
            en_trayectorias = 0
            for t in experimento.trayectorias:
                en_trayectorias += len(t.observaciones)
            #quitadas = len(validas) - en_trayectorias
            print(f"{experimento.nombre}: {descartadas} observaciones descartadas")
            print(f"{experimento.nombre}: {len(experimento.trayectorias)} trayectorias")
        return experimentos

    def _validar_observaciones(self, observaciones: list[Observacion],) -> list[Observacion]:
        """Valida y retorna las observaciones de un experimento."""
        correctas = list(filter(lambda obs: (obs.id_peaton >= 0) and (obs.frame >= 0), observaciones))
        vistas = {}
        sin_repetidas = []
        for obs in correctas:
            clave = (obs.id_peaton, obs.frame)
            if clave not in vistas: 
                vistas[clave] = True 
                sin_repetidas.append(obs)
        return sin_repetidas
                                
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
            lista = self._quitar_saltos(observaciones_organizadas[id_peaton])
            if len(lista) >= 2:
                trayectoria = Trayectoria(id_peaton=id_peaton, observaciones=lista)
                trayectorias.append(trayectoria)      
        return trayectorias
    
    def _quitar_saltos(self, observaciones):
        limpias = [observaciones[0]]
        for obs in observaciones[1:]:
            anterior = limpias[-1]
            d = ((obs.x - anterior.x) ** 2 + (obs.y - anterior.y) ** 2) ** 0.5 
            dt = (obs.frame - anterior.frame) / self.fps
            if d / dt <= velocidad_maxima_valida:
                limpias.append(obs)
        return limpias
