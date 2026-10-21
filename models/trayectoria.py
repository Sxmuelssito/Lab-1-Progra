"""Modelo básico de una trayectoria peatonal."""

from dataclasses import dataclass, field
from .observacion import Observacion
from math import sqrt


@dataclass
class Trayectoria:
    """Representa las observaciones y cálculos propios de un peatón."""

    id_peaton: int
    observaciones: list[Observacion] = field(default_factory=list)

    #Inciso 5.2.1
    def obtener_posicion_inicial(self):
        primera = self.observaciones[0]
        return primera.x, primera.y, primera.z

    #Inciso 5.2.2
    def obtener_posicion_final(self):
        ultima = self.observaciones[-1]
        return ultima.x, ultima.y, ultima.z

    #Inciso 5.2.3
    def calcular_tiempo_total_ob(self, fps):
        frame_inicial = self.observaciones[0].frame
        frame_final = self.observaciones[-1].frame
        return (frame_final - frame_inicial) / fps

    #Inciso 5.2.4
    def calcular_distancia_total(self) -> float:
        """Calcula la distancia total recorrida por el peatón."""
        total = 0 
        for i in range(len(self.observaciones)-1):
            actual = self.observaciones[i]
            siguiente = self.observaciones[i+1]
            d = sqrt((siguiente.x - actual.x)**2 + (siguiente.y - actual.y)**2)
            total += d 
        return total

    #Inciso 5.2.5
    def calcular_desplazamiento(self) -> float:
        """Calcula el desplazamiento entre el inicio y el final."""
        x_inicial = self.observaciones[0].x
        x_final = self.observaciones[-1].x
        y_inicial = self.observaciones[0].y
        y_final = self.observaciones[-1].y
        return sqrt(((x_final-x_inicial)**2) + ((y_final-y_inicial)**2))

    #Inciso 5.2.6
    def calcular_velocidad_media(self, fps: float) -> float:
        """Calcula la velocidad media usando la frecuencia del experimento."""
        tiempo = self.calcular_tiempo_total_ob(fps)
        if tiempo == 0:
            return 0
        return self.calcular_distancia_total() / tiempo

    #Inciso 5.2.7
    def calcular_velocidades(self,fps):
        velocidades = []
        for i in range(len(self.observaciones) - 1):
            actual = self.observaciones[i]
            siguiente = self.observaciones[i+1]
            d = sqrt((siguiente.x - actual.x)**2 + (siguiente.y - actual.y)**2)
            dt = (siguiente.frame - actual.frame) / fps
            velocidades.append(d / dt )
        return velocidades 

    def velocidad_max(self,fps):
        return max(self.calcular_velocidades(fps))

    #Inciso 5.2.8
    def calcular_eficiencia(self):
        distancia = self.calcular_distancia_total()
        if distancia == 0:
            return 0
        return self.calcular_desplazamiento() / distancia 
