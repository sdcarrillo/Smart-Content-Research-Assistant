# Smart-Content-Research-Assistant

Asistente de investigación multi-agente hecho en **Python** con **LangGraph** y **Azure OpenAI**.  
Funciona por consola: el usuario ingresa un tema, el sistema genera subtemas, pide aprobación humana y produce un informe final en texto estructurado.

## Estructura del sistema

- **Investigator** --> propone subtemas y fuentes iniciales.  
- **Supervisor** --> muestra resultados, recibe comandos (`approve`, `reject`, `modify`, `add`).  
- **Curator** --> analiza los subtemas aprobados.  
- **Reporter** --> redacta el informe final.  

El flujo completo se orquesta con **LangGraph**, usando un único punto de intervención humana.  
Cada agente utiliza un modelo distinto según la complejidad de la tarea (cheap / standard / premium).
La complejidad del modelo utilizado por Curator se define a partir de la complejidad semántica del tópico. 

## Como correrlo

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt

Crear un archivo .env con tus credenciales de Azure:
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_API_VERSION=2024-02-01
AZURE_OPENAI_CHEAP_DEPLOYMENT=gpt-4o-mini
AZURE_OPENAI_STANDARD_DEPLOYMENT=gpt-4o
AZURE_OPENAI_PREMIUM_DEPLOYMENT=gpt-4o

python src/main.py
```

## Comandos disponibles

- approve 1,3
- reject 2
- modify 1 to "Nuevo título"
- add "Nuevo subtema"

Podes combinar comandos con ';'.
Si no usás 'approve', se asume que todo lo no 'reject' se mantiene.


## Notas

Desarrollado como demostración de diseño de sistemas de IA con LangGraph y Azure OpenAI.


