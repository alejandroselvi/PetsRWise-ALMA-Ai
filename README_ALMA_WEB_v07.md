# ALMA Web v0.7 — Diseño PetsRWise

**Estado:** demostración interna de desarrollo, solo mascotas y casos ficticios. Los archivos de conocimiento veterinario existentes no han sido aprobados clínicamente. ALMA no es un veterinario ni ofrece diagnóstico, prescripciones o confirmación de citas.

## Qué cambió

- Experiencia inspirada en el mockup aprobado: identidad rosa/blanco, logo oficial original de PetsRWise, menú lateral, cabecera ALMA, avatar ilustrativo y botones de acción rápida.
- Panel derecho: especie, mascota ficticia, ubicación escrita manualmente, idioma/voz, velocidad por defecto 1.20×, biblioteca y alertas.
- Conversación con memoria de sesión a través de Responses API. Recuperación de múltiples Vector Stores y búsqueda web mediante el backend actual.
- Búsqueda de clínicas en pantalla propia; **resultados web no verificados**, sin reservas ni ubicación GPS.
- Micrófono opcional y síntesis de voz por turnos en español latinoamericano e inglés estadounidense.
- Botón «Nueva conversación». Pantallas de explicación y avisos de uso interno.

## Instalación (Mac, VS Code)

### Antes de actualizar

1. Detén Streamlit en Terminal con `Control+C`.
2. En VS Code, abre la carpeta `ALMA beta` que contiene tu `alma_chat.py` y `.env`.
3. Haz una copia de seguridad. En Terminal:

```bash
cd ~/Desktop/"ALMA beta"
mkdir -p respaldos
cp -n app.py respaldos/app_antes_v07.py 2>/dev/null || true
cp -n alma_backend.py respaldos/backend_antes_v07.py 2>/dev/null || true
cp -n alma_voice.py respaldos/voice_antes_v07.py 2>/dev/null || true
```

### Instala v0.7

Descarga `ALMA_Web_v0_7_UX_PetsRWise.zip` a Descargas y ejecuta:

```bash
cd ~/Desktop/"ALMA beta"
unzip -o ~/Downloads/ALMA_Web_v0_7_UX_PetsRWise.zip -d .
source .venv/bin/activate
python -m pip install -r requirements_alma_web.txt
python -m unittest test_alma_backend.py
python -m streamlit run app.py
```

Si tu entorno se llama `.venx`, utiliza `source .venx/bin/activate`.

Después abre **http://localhost:8501**. Asegúrate de no tener otro Streamlit abierto en ese mismo puerto.

**IMPORTANTE:** Este ZIP deliberadamente **NO** incluye `.env` ni `alma_chat.py`; el comando `unzip -o` actualiza la interfaz y su backend de apoyo, no tus claves ni tu chat terminal. El ZIP se extrae directamente al directorio del proyecto (no hay una carpeta extra en la raíz del ZIP).

### Configuración reutilizada

El proyecto conserva tu `.env` con las variables:

```dotenv
OPENAI_API_KEY=tu_clave_ya_configurada
ALMA_VECTOR_STORE_IDS=vs_primero,vs_segundo,vs_tercero
ALMA_MODEL=gpt-5.4-mini
```

También se admite el formato anterior `ALMA_VECTOR_STORE_ID=vs_unico`.

**Nunca compartas tu `.env` ni la clave API.** En cualquier repositorio, ignora `.env` y `.venv`.

## Prueba rápida

1. Entra en **Hablar con ALMA** y haz una pregunta ficticia sobre cuidado animal. Verifica la respuesta y expande «Fuentes consultadas».
2. Selecciona **Buscar veterinario**, escribe una ciudad (por ejemplo, Miami) y comprueba que haya enlaces reales cuando el motor encuentra resultados.
3. Activa la voz en el panel derecho; haz clic en **Probar voz** (requiere OpenAI API y puede generar costes).
4. Cambia entre **Español** e **English**. Cambiar el perfil reinicia la conversación para evitar mezclar especies/casos.

## Material visual

Los logos en `assets/petsrwise_logo_original.png` y `assets/petsrwise_icon.png` provienen de los archivos que proporcionó PetsRWise. El retrato de ALMA y las imágenes pequeñas de tarjetas son recortes del **mockup generado y aprobado**; no representan a una veterinaria real ni una conexión LiveAvatar. No existe sincronización labial en v0.7.

## Seguridad y próximos pasos

- **No usar casos reales, datos privados, citas, reservas o expedientes clínicos** en este prototipo.
- La detección por frases es solo una demostración, no un sistema de triaje validado.
- Los nombres/direcciones de clínicas vienen de búsqueda web y pueden estar desactualizados; confirmar antes de acudir.
- Para producción: revisión clínica de expertos por especie y jurisdicción, controles independientes de urgencias, protección de datos, sistema de clínicas verificadas, evaluación y aprobaciones.

## Comprobaciones realizadas

- Sintaxis de Python comprobada y pruebas unitarias offline ejecutadas.
- No se ejecutó Streamlit contra tu cuenta de OpenAI ni se generó voz real desde este entorno. Debes probarlo en tu Mac.
