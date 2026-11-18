# ALMA Web v0.4 — PetsRWise (demo interna)

Esta aplicación es una **demo local** desarrollada en Python + Streamlit. Mantiene la identidad visual de [PetsRWise](https://www.petsrwise.com/) (rosa, blanco, tarjetas redondeadas y logos originales del usuario incluidos dentro de `assets/`). Se apoya en los mismos **Vector Stores** y **OpenAI Web Search** de tu `alma_chat.py`, sin editarlo ni importarlo.

> **No es una aplicación clínica aprobada.** Solo usa mascotas y casos ficticios. No recopiles historias clínicas, datos reales de clientes, documentos sensibles ni información de urgencias reales. Los materiales en los vectores siguen pendientes de revisión veterinaria. No publiques la app sin controles de acceso, evaluación clínica, gestión de privacidad y autorización legal.

## 1. Instalar sobre tu proyecto ALMA actual (Mac + VS Code)

1. Descomprime `ALMA_Web_v0_4_PetsRWise_Logo_Original.zip` en **Descargas**.
2. Abre tu proyecto existente: `~/Desktop/ALMA` en VS Code.
3. Puedes instalar los archivos nuevos automáticamente, sin borrar `alma_chat.py` ni `.env`, ejecutando en el terminal:

```bash
cd ~/Desktop/ALMA
unzip -n ~/Downloads/ALMA_Web_v0_4_PetsRWise_Logo_Original.zip -d .
```

Si el ZIP se descargó en otra carpeta, actualiza la ruta. La opción `-n` no sobrescribe archivos existentes. **Si instalaste una versión anterior de `app.py`, utiliza el procedimiento de actualización al final de esta guía**, ya que `-n` mantendrá la versión anterior. También puedes copiar manualmente `app.py`, `alma_backend.py`, `requirements_alma_web.txt` y la carpeta oculta `.streamlit/` a la raíz `ALMA`, al lado de `alma_chat.py`. Pulsa `Command + Shift + .` en Finder para mostrar archivos ocultos. **No reemplaces el `.env` actual y no muevas `.venv`**.
4. Abre **Terminal → New Terminal** y ejecuta:

```bash
cd ~/Desktop/ALMA
source .venv/bin/activate
python -m pip install -r requirements_alma_web.txt
```

Si tu entorno se llama `.venx`, cambia `.venv` por `.venx`.

## 2. Revisar `.env` (se reutiliza el existente)

Abre tu `.env` actual y verifica que incluya tus valores privados:

```dotenv
OPENAI_API_KEY=TU_CLAVE_PRIVADA
ALMA_VECTOR_STORE_IDS=vs_PRIMER_ID,vs_SEGUNDO_ID,vs_TERCER_ID
ALMA_MODEL=gpt-5.4-mini
```

Si solo usas un vector, también se reconoce la variable anterior `ALMA_VECTOR_STORE_ID=vs_...`. No publiques este archivo. El modelo es configurable: puedes conservar el mismo modelo que ya funciona en tu entorno.

## 3. Ejecutar ALMA Web

```bash
cd ~/Desktop/ALMA
source .venv/bin/activate
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

Abre **http://127.0.0.1:8501** (o **http://localhost:8501**) en tu navegador. Para detener el servidor, vuelve al Terminal y pulsa **Control + C**.

## 4. Qué incluye

- Diseño inspirado en la identidad visual del sitio PetsRWise; el logotipo original aportado por el usuario está en `assets/`, por lo que aparece incluso sin conexión a Internet.
- Configuración de **idioma** (ES/EN), **especie** (perro, gato, caballo, bovino, oveja, cabra, cerdo, conejo, ave, reptil) y **mascota ficticia**.
- Campos de **país, estado/región y ciudad manual** (todavía **no** pide GPS ni accede a ubicación del navegador).
- **Chat por turnos** con memoria de la conversación mediante `previous_response_id` de OpenAI.
- **File Search** en todos los vectores configurados y **Web Search** opcional.
- Panel expandible con **nombres de archivos recuperados** y **enlaces web cuando la API los proporciona**.
- Aviso preliminar para ciertas expresiones de emergencia: **no es un detector médico validado**.
- Botón **Nueva conversación** y reseteo de contexto al cambiar la configuración.
- **Sin** agenda real, reservas, GPS, subida de historias clínicas ni datos de pacientes.

## 5. Verificaciones y solución de problemas

| Problema | Qué revisar |
|---|---|
| `ModuleNotFoundError: No module named 'streamlit'` | Activa `.venv` y ejecuta `python -m pip install -r requirements_alma_web.txt` |
| `401` | API key y proyecto de OpenAI; nunca compartas la clave |
| `404` en vector store | Confirma los `vs_...` del proyecto OpenAI correcto |
| `429` | Configuración de facturación, límites y consumo de API |
| El sitio aparece, pero no responde | Revisa el error mostrado, modelo, ID de vector y conexión |
| Aparecen menos archivos de los esperados | El modelo no tiene por qué consultar cada vector por pregunta; inspecciona fuentes y prueba consultas específicas |
| El logo no aparece | Comprueba que copiaste la carpeta `assets/` y que contiene `petsrwise_icon.png` y `petsrwise_logo_original.png` |

### Pruebas locales sin API

Con los archivos del paquete, ejecuta en la raíz:

```bash
python -m unittest discover -s tests -v
python -m py_compile app.py alma_backend.py
```

Estas pruebas **no** sustituyen validación de interface, conexión a API, o evaluación veterinaria. La interfaz requiere instalar Streamlit; el entorno donde se creó este paquete no pudo instalar dependencias de red, por lo que no se probó visualmente el servidor real.

## 6. Próxima versión y despliegue seguro

ALMA Web 0.4 se ejecuta **solo localmente en tu Mac**. Antes de publicar o probar con propietarios reales hacen falta un backend seguro con autenticación y gestión de acceso; aprobación clínica por especie/país/estado; evaluación del triaje y del manejo de riesgos; políticas de privacidad y retención; base independiente de socios verificados; consultas con profesionales licenciados cuando corresponda; cumplimiento de términos de contenido y API.

**Nunca subas `.env`, vectores privados o datos de pacientes a GitHub.**

### Documentación
- [OpenAI Responses API](https://developers.openai.com/api/reference/resources/responses/methods/create)
- [OpenAI File Search](https://developers.openai.com/api/docs/guides/tools-file-search)
- [OpenAI Web Search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Streamlit Chat](https://docs.streamlit.io/develop/api-reference/chat)
- [Sitio oficial PetsRWise](https://www.petsrwise.com/)


## Actualizar solo el diseño y logo si ALMA Web ya estaba instalado

Si ya tienes un `app.py` anterior funcionando en tu carpeta `ALMA`, **no basta con `unzip -n` para actualizarlo**. Primero guarda una copia:

```bash
cd ~/Desktop/ALMA
cp app.py app_antes_del_logo.py
unzip -o ~/Downloads/ALMA_Web_v0_4_PetsRWise_Logo_Original.zip app.py 'assets/*'
```

Esto actualiza solo la interfaz y los logos. No modifica `alma_chat.py`, `.env` ni tus Vector Stores. Reinicia Streamlit después. Si es la primera instalación, usa `unzip -n` con este ZIP.
