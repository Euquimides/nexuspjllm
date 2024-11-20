# NEXUSPJLLM

### Descripción

**NEXUSPJLLM** es una aplicación creada en Python que a través de la API de **NexusPJ** (https://nexuspj.poder-judicial.go.cr/), permite obtener jurisprudencia relevante a un tema específico e insumos legales útiles para juristas y abogados, esto por medio del uso de técnicas modernas de aprendizaje automático.

Para mayor privacidad, la aplicación - fuera de la consulta a la API - está construida para funcionar principalmente de manera local, con el uso de modelos de vectorización y clasificación previamente entrenados, al igual que modelos grandes de lenguaje optimizados para correr en CPU.

### Instalación

Para instalar la aplicación, se debe clonar el repositorio y crear un entorno virtual con Python 3.7+. Luego, se debe instalar las dependencias del archivo `requirements.txt`.

```pip install -r requirements.txt```

Luego, descargue **Ollama** (https://ollama.com/) para poder utilizar modelos grandes de lenguaje de manera local con la aplicación. Ésta aplicación ha sido probada principalmene con el modelo Llama3.2 `https://ollama.com/library/llama3.2`, dado a que está optimizado para correr en computación edge, por lo que se recomienda su uso.

### Uso

Inicialice primero el servidor de **Ollama** con el modelo de lenguaje que desea utilizar, con las configuraciones sea por defecto o personalizadas. Esto puede hacerlo a través del comando en su termina.

```bash
ollama serve
```

Descargue el modelo que vaya a utilizar de la página de  **Ollama**, por ejemolo, para Llama3.2 utilice el siguiente comando:

```bash
ollama run llama3.2
```

A continuación, debe ejecutar el archivo `app/main.py` con Python 3.7+.

```bash
python app/main.py
```

La aplicación le brindará varias opciones a utilizar las cuales se explican a continuación:
1. **Consulta a NexusPJ y extracción de jurisprudencia relacionada**: Esta opción le permite realizar una consulta al API de NexusPJ y extraer jurisprudencia relevante a un tema específico. Para esto, debe ingresar el tema de interés. La aplicación le mostrará los documentos extraídos y los guardará en un archivo de texto plano.
2. **Generación inteligente de respuestas con base a jurisprudencia extraída**: Esta opción le permite generar respuestas con base a la jurisprudencia extraída en el paso anterior utilizando un modelo grande de lenguaje de su elección. Dado a que corre en CPU localmente, la generación de respuestas puede tardar varios minutos. *IMPORTANTE: La generación de respuestas se realiza con base a la jurisprudencia extraída en la opción anterior, por lo que se recomienda utilizar esta opción luego de haber utilizado la opción 1.*
3. **Top 3 de jurisprudencia más relevante según consulta a base de datos**: Esta opción le permite obtener los 3 documentos de jurisprudencia más relevantes según una consulta a la base de datos vectorial de jurisprudencia. Para esto, debe ingresar el tema de interés o su consulta específica. La aplicación le mostrará los documentos extraídos y los guardará en un archivo de texto plano en todo caso que quiera evaluar el material posteriormente. 

### Consideraciones

* Revise las respuestas generadas por la aplicación, ya que pueden contener errores en su contenido por tratarse de modelos generativos.
* La aplicación fue desarrollada con fines de aprendizaje, por lo que no se garantiza su correcto funcionamiento en todos los casos.
* La aplicación fue desarrollada para funcionar en CPU, por lo que se recomienda utilizar un equipo con al menos 16GB de RAM y un procesador de 8 núcleos o más. Puede correr incluso en 8GB de RAM siempre y cuando utilice un modelo como el recomendado. Si quiere correrlo en VRAM, lo ideal es tener como mínimo 4GB.
* La aplicación fue desarrollada para funcionar en Windows 11, por lo que no se garantiza su correcto funcionamiento en otros sistemas operativos.
* No se garantiza el funcionamiento de la API de NexusPJ por tratarse de un servicio externo a cargo del Poder Judicial de Costa Rica, por lo que la aplicación puede dejar de funcionar en cualquier momento.

### TODO
- [ ] Refactorizar ya que algunas secciones son legacy code.
- [ ] Agregar una interfaz gráfica en Gradio, NextJS u framework.
- [ ] Cambiar a un gestor de paquetes más sólido como por ejemplo Poetry. 