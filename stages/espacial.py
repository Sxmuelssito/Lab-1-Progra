"""Etapa de análisis espacial, densidad y flujo."""

from models.experimento import Experimento
from pipeline.contexto import ContextoPipeline
from pipeline.etapa import EtapaPipeline

num_zonas = 5
umbral_zona_lenta = 0.90
zona_medicion = num_zonas // 2
ventana_tiempo = 10

inicio_corredor = -4
fin_corredor = 4
ancho_corredor = 5
linea_flujo = 0
largo_zona = (fin_corredor - inicio_corredor) / num_zonas



class AnalisisEspacial(EtapaPipeline[list[Experimento], list[Experimento]]):
    """Agrupa el análisis por zonas y los cálculos de densidad y flujo."""

    def ejecutar(self, experimentos: list[Experimento], contexto: ContextoPipeline,) -> list[Experimento]:
        """Analiza las zonas, la densidad y el flujo de cada experimento."""
        # self.fps = contexto.fps
        # for experimento in experimentos:
        #     eje = self._eje_principal(experimento)
        #     inicio, fin = self._limites_corredor(experimento, eje)
        #     largo_zona = (fin - inicio) / num_zonas
        #     print(f"{experimento.nombre}: se camina en el eje {eje}, de {round(inicio,2)} a {round(fin,2)} m")
        #     print(f"  {num_zonas} zonas de {round(largo_zona,2)} m cada una")
        #     print('-'*15)
        #     zonas = self._analizar_zonas(experimento)
        #     for clave in zonas:
        #         print(f"  {clave}: {round(zonas[clave],2)}")
        #     print('-'*15)
        #     densidad = self._calcular_densidad(experimento)
        #     for clave in densidad:
        #         print(f" {clave}: {round(densidad[clave],2)}")
        #     print('-'*15)
        #     flujo = self._calcular_flujo(experimento, self.fps)
        #     for clave in flujo:
        #         print(f"  {clave}: {round(flujo[clave],2)}")
        #return experimentos

        self.fps = contexto.fps
        for experimento in experimentos:
            self.eje, self.sentido = self._direccion_caminata(experimento)
            if self.sentido == 1:
                texto_sentido = "hacia valores positivos"
            else:
                texto_sentido = "hacia valores negativos"
            print(f"{experimento.nombre}: se camina en el eje {self.eje}, {texto_sentido}")

            zonas = self._analizar_zonas(experimento)
            densidad = self._calcular_densidad(experimento)
            flujo = self._calcular_flujo(experimento, self.fps)

            for parcial in [zonas, densidad, flujo]:
                for clave in parcial.keys():
                    experimento.resultados_colectivos[clave] = parcial[clave]


            resultados = experimento.resultados_colectivos
            print(f"{experimento.nombre}: densidad media {round(resultados['densidad_media_p_m2'], 2)} p/m², flujo {round(resultados['flujo_p_s'], 2)} p/s")
        return experimentos

    def _direccion_caminata(self, experimento: Experimento):
        avance_x = 0
        avance_y = 0
        for t in experimento.trayectorias:
            avance_x = avance_x + (t.observaciones[-1].x - t.observaciones[0].x)
            avance_y = avance_y + (t.observaciones[-1].y - t.observaciones[0].y)
        if abs(avance_x) > abs(avance_y):
            eje = "x"
            avance = avance_x
        else:
            eje = "y"
            avance = avance_y
        if avance > 0:
            sentido = 1
        else:
            sentido = -1
        return eje, sentido

    def _avance(self, obs):
        if self.eje == "x":
            return self.sentido * obs.x
        return self.sentido * obs.y
    

    def _analizar_zonas(self, experimento: Experimento) -> dict[str, float]:
        velocidades_zona = [[] for z in range(num_zonas)]
        todas = []
        tiempo_zona = [{} for z in range(num_zonas)]
        for t in experimento.trayectorias:
            velocidades = t.calcular_velocidades(self.fps)
            for i in range(len(velocidades)):
                posicion = self._avance(t.observaciones[i])
                if inicio_corredor <= posicion < fin_corredor:
                    zona = int((posicion - inicio_corredor) / largo_zona)
                    velocidades_zona[zona].append(velocidades[i])
                    todas.append(velocidades[i])
                    dt = (t.observaciones[i + 1].frame - t.observaciones[i].frame) / self.fps
                    if t.id_peaton not in tiempo_zona[zona]:
                        tiempo_zona[zona][t.id_peaton] = 0
                    tiempo_zona[zona][t.id_peaton] = tiempo_zona[zona][t.id_peaton] + dt
        velocidad_general = sum(todas) / len(todas)
        resultados = {}
        for z in range(num_zonas):
            lista = velocidades_zona[z]
            if len(lista) > 0:
                resultados[f"zona_{z}_velocidad_media_m_s"] = sum(lista) / len(lista)
            else:
                resultados[f"zona_{z}_velocidad_media_m_s"] = 0

            tiempos = list(tiempo_zona[z].values())
            resultados[f"zona_{z}_peatones"] = len(tiempos)
            if len(tiempos) > 0:
                resultados[f"zona_{z}_tiempo_medio_s"] = sum(tiempos) / len(tiempos)
            else:
                resultados[f"zona_{z}_tiempo_medio_s"] = 0

            relativa = resultados[f"zona_{z}_velocidad_media_m_s"] / velocidad_general
            resultados[f"zona_{z}_velocidad_relativa"] = relativa
            if relativa < umbral_zona_lenta:
                resultados[f"zona_{z}_es_lenta"] = 1
            else:
                resultados[f"zona_{z}_es_lenta"] = 0
        return resultados   

    def _calcular_densidad(self, experimento: Experimento) -> dict[str, float]:
        desde = inicio_corredor + (zona_medicion * largo_zona)
        hasta = desde + largo_zona 
        area = largo_zona * ancho_corredor


        personas_por_frame = {}
        velocidades_por_frame = {}
        for t in experimento.trayectorias:
            velocidades = t.calcular_velocidades(self.fps)
            for i in range(len(t.observaciones)):
                obs = t.observaciones[i]
                if obs.frame not in personas_por_frame:
                    personas_por_frame[obs.frame] = 0
                    velocidades_por_frame[obs.frame] = []
                if desde <= self._avance(obs) < hasta:
                    personas_por_frame[obs.frame] += 1
                    if i < len(velocidades):
                        velocidades_por_frame[obs.frame].append(velocidades[i])

        densidades = [n / area for n in personas_por_frame.values()]
        resultados = {
            "area_medicion_m2": area,
            "densidad_media_p_m2": sum(densidades) / len(densidades),
            "densidad_maxima_p_m2": max(densidades),
        }

        frames = sorted(personas_por_frame.keys())
        primer_frame = frames[0]
        ultimo_frame = frames[-1]
        num_ventanas = int((ultimo_frame - primer_frame) / self.fps / ventana_tiempo) + 1
        densidad_ventana = [[] for k in range(num_ventanas)]
        velocidad_ventana = [[] for k in range(num_ventanas)]
        for frame in frames:
            k = int((frame - primer_frame) / self.fps / ventana_tiempo)
            densidad_ventana[k].append(personas_por_frame[frame] / area)
            velocidad_ventana[k].extend(velocidades_por_frame[frame])

        resultados["num_ventanas_densidad"] = num_ventanas
        for k in range(num_ventanas):
            resultados[f"ventana_{k}_inicio_s"] = primer_frame / self.fps + k * ventana_tiempo
            resultados[f"ventana_{k}_densidad_p_m2"] = sum(densidad_ventana[k]) / len(densidad_ventana[k])
            if len(velocidad_ventana[k]) > 0:
                resultados[f"ventana_{k}_velocidad_m_s"] = sum(velocidad_ventana[k]) / len(velocidad_ventana[k])
            else:
                resultados[f"ventana_{k}_velocidad_m_s"] = 0
        return resultados

    def _calcular_flujo(self, experimento: Experimento, fps: float | None,) -> dict[str, float]:
        tiempos_cruce = []
        for t in experimento.trayectorias:
            i = 0
            cruzo = False
            while i < len(t.observaciones) - 1 and not cruzo:
                a = self._avance(t.observaciones[i])
                b = self._avance(t.observaciones[i + 1])
                if (a < linea_flujo <= b) or (b < linea_flujo <= a):
                    tiempos_cruce.append(t.observaciones[i + 1].frame / fps)
                    cruzo = True
                i += 1
        tiempos_cruce.sort()

        resultados = {
            "linea_flujo_m": linea_flujo,
            "peatones_cruzan_linea": len(tiempos_cruce),
        }
        if len(tiempos_cruce) < 2:
            resultados["flujo_p_s"] = 0
            resultados["num_ventanas_flujo"] = 0
            return resultados

        primer_cruce = tiempos_cruce[0]
        ultimo_cruce = tiempos_cruce[-1]
        resultados["flujo_p_s"] = len(tiempos_cruce) / (ultimo_cruce - primer_cruce)

        num_ventanas = int((ultimo_cruce - primer_cruce) / ventana_tiempo) + 1
        conteo = [0] * num_ventanas
        for tiempo in tiempos_cruce:
            k = int((tiempo - primer_cruce) / ventana_tiempo)
            conteo[k] = conteo[k] + 1

        resultados["num_ventanas_flujo"] = num_ventanas
        for k in range(num_ventanas):
            resultados[f"flujo_ventana_{k}_inicio_s"] = primer_cruce + k * ventana_tiempo
            resultados[f"flujo_ventana_{k}_peatones"] = conteo[k]
            resultados[f"flujo_ventana_{k}_p_s"] = conteo[k] / ventana_tiempo
        return resultados