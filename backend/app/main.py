import os
from utils.ingerir import *
from utils.logs import logger
import time

class NexusPJLLM:
    def __init__(self):
        self.index = None
        self.timing_data = []
        logger.info("NexusPJLLM app iniciada")

    def imprimir_opciones(self):
        options = {
            "1": "Consulta a NexusPJ y extracción de jurisprudencia relacionada",
            "2": "Generación inteligente de respuestas con base a jurisprudencia extraída",
            "3": "Top 3 de jurisprudencia más relevante según consulta a base de datos",
            "4": "Salir"
        }
        print("\nSeleccione una opción:")
        for key, value in options.items():
            print(f"{key}. {value}")
        print()

    def verificar_base_datos(self):
        if not os.path.exists("./app/chroma_db"):
            print("Debe ingerir la jurisprudencia primero. Seleccione la opción 1.")
            return False
        return True

    def procesar_consulta(self, consulta, reranker=False):
        try:
            start_time = time.time()
            if not self.index:
                self.index = get_index()
            
            retrieved_nodes = buscar_nodos(
                consulta,
                self.index,
                vector_top_k=20,
                reranker_top_n=3,
                with_reranker_sbert=reranker
            )
            elapsed_time = time.time() - start_time
            self.timing_data.append({"operation": "procesar_consulta", "time": elapsed_time})
            return retrieved_nodes
        except Exception as e:
            logger.error(f"Error al procesar consulta: {str(e)}")
            raise

    def opcion_1(self):
        while True:
            try:
                consulta = input("\nIngrese su consulta sobre un tema jurídico particular: ")
                start_time = time.time()
                
                nodes = extractor(consulta, embedding_model)
                self.index = indexar(nodes)
                retrieved_nodes = self.procesar_consulta(consulta)
                
                imprimir_nodos(retrieved_nodes)
                guardar_nodos(retrieved_nodes)
                
                elapsed_time = time.time() - start_time
                self.timing_data.append({"operation": "opcion_1", "time": elapsed_time})
                logger.info(f"Indexación y guardado de nodos finalizado en {elapsed_time:.2f} segundos")
                
                if not self.continuar_consulta():
                    break
            except Exception as e:
                logger.error(f"Error en opción 1: {str(e)}")
                print(f"Ocurrió un error: {str(e)}")

    def opcion_2(self):
        if not self.verificar_base_datos():
            return

        while True:
            try:
                consulta = input("\nIngrese su consulta: ")
                start_time = time.time()
                
                retrieved_nodes = self.procesar_consulta(consulta, reranker=True)
                imprimir_nodos(retrieved_nodes)
                logger.info("Iniciando síntesis de respuesta...")
                
                respuesta = sintetizador_respuesta(consulta, retrieved_nodes)
                
                elapsed_time = time.time() - start_time
                self.timing_data.append({"operation": "opcion_2", "time": elapsed_time})
                logger.info(f"Respuesta generada en {elapsed_time:.2f} segundos")
                
                self.mostrar_resultado(consulta, respuesta)
                
                if not self.continuar_consulta():
                    break
            except Exception as e:
                logger.error(f"Error en opción 2: {str(e)}")
                print(f"Ocurrió un error: {str(e)}")

    def opcion_3(self):
        if not self.verificar_base_datos():
            return

        while True:
            try:
                consulta = input("\nIngrese su consulta: ")
                start_time = time.time()
                
                retrieved_nodes = self.procesar_consulta(consulta, reranker=True)
                
                elapsed_time = time.time() - start_time
                self.timing_data.append({"operation": "opcion_3", "time": elapsed_time})
                logger.info(f"Búsqueda completada en {elapsed_time:.2f} segundos")
                
                self.mostrar_resultado(consulta, None, retrieved_nodes)
                guardar_nodos(retrieved_nodes)
                
                if not self.continuar_consulta():
                    break
            except Exception as e:
                logger.error(f"Error en opción 3: {str(e)}")
                print(f"Ocurrió un error: {str(e)}")

    def continuar_consulta(self):
        while True:
            opcion = input("\n¿Desea realizar otra consulta? (S/N): ").lower()
            if opcion in ['s', 'n']:
                return opcion == 's'
            print("Opción inválida. Responda S o N.")

    def mostrar_resultado(self, consulta, respuesta=None, nodes=None):
        print("\n" + "-" * 50)
        print(f"Su consulta fue:\n{consulta}")
        print("-" * 50)
        
        if respuesta:
            print(f"Respuesta generada:\n{respuesta}")
        if nodes:
            print("Top 3 de jurisprudencia más relevante:")
            imprimir_nodos(nodes)
        print("-" * 50 + "\n")

    def ejecutar(self):
        try:
            print("Bienvenido a NexusPJLLM\n")
            opciones = {"1": self.opcion_1, "2": self.opcion_2, "3": self.opcion_3}
            
            while True:
                self.imprimir_opciones()
                opcion = input("Ingrese una opción: ")
                
                if opcion == "4":
                    break
                elif opcion in opciones:
                    opciones[opcion]()
                else:
                    print("Opción inválida. Intente nuevamente.")
                    
        except Exception as e:
            logger.error(f"Error general: {str(e)}")
            print(f"Error inesperado: {str(e)}")
        finally:
            logger.info("NexusPJLLM app finalizada")
            logger.info(f"Timing data: {self.timing_data}")

if __name__ == "__main__":
    app = NexusPJLLM()
    app.ejecutar()
