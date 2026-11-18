# ALMA Web v0.6 — Voz rápida (Español Latinoamérica / English USA)

## Cambios respecto a v0.5
- Voz predeterminada `marin` (calidad natural; puedes volver a `coral`, voz anterior).
- Velocidad predeterminada **1.20×**, ajustable entre **0.80× y 1.60×** desde Streamlit.
- Español: instrucción de acento **latinoamericano neutro**, evitando pronunciación de España.
- Inglés: instrucción de pronunciación de **Estados Unidos / General American**.
- Botón de **probar voz** sin enviar una pregunta a tus vectores.
- Los audios antiguos de la sesión se vuelven a generar al modificar voz o velocidad.
- Mantiene los logos originales, File Search, búsqueda web, transcripción y chat existentes.

> Los acentos se solicitan al modelo; la pronunciación exacta no está garantizada. El resultado es una voz generada por IA, no un profesional real ni un avatar. Las pruebas siguen limitadas a casos ficticios.

## Instalar en Mac / Visual Studio Code
1. Guarda el ZIP en la carpeta Downloads.
2. En Terminal de VS Code:

```bash
cd ~/Desktop/"ALMA beta"
# Respaldo de la interfaz previa
cp app.py app_antes_voz_v0_6.py
cp alma_voice.py alma_voice_antes_v0_6.py
# Actualiza únicamente app y voz; no toques tu .env ni alma_chat.py
unzip -o ~/Downloads/ALMA_Web_v0_6_Voz_LatAm_USA_PetsRWise.zip app.py alma_voice.py test_voice.py
source .venv/bin/activate
python -m pip install -r requirements_alma_web.txt
python -m unittest test_voice.py
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

3. Abre **http://localhost:8501**. En la barra lateral activa **Habilitar micrófono y audio**, selecciona voz `Marin (natural)`, y ajusta **Velocidad / Speech speed** (valor inicial: `1.20×`).
4. Cambia **Idioma / Language** entre Español y English. Pulsa **Probar voz / Preview voice**.
5. Si tu Mac tiene `.venx` en vez de `.venv`, usa `source .venx/bin/activate`.

**Si aún no tienes ALMA Web v0.5 instalado:** el ZIP también contiene todos los archivos de esa versión, incluyendo `assets/`, `alma_backend.py`, `.streamlit/config.toml` y `requirements_alma_web.txt`. Puedes extraer el ZIP completo con `unzip -n`, que no sobrescribe archivos existentes; después sobrescribe específicamente `app.py` y `alma_voice.py` con `unzip -o`.

## Cómo funciona
El audio se genera mediante `client.audio.speech.create(..., instructions=..., speed=...)` con un modelo OpenAI TTS. Estas instrucciones permiten solicitar pronunciación regional, y `speed` cambia la velocidad del audio sintetizado. La calidad real debe validarse en tu Mac con tu cuenta OpenAI.

## Seguridad y roadmap
- Los audios son sintéticos; deben presentarse claramente como generados por IA.
- No uses pacientes reales ni una consulta de emergencia en esta demo.
- Mantén `.env` fuera de ZIP, GitHub y el repositorio compartido.
- La API `gpt-4o-mini-tts` tiene retiro anunciado para **6 de enero de 2027**. Para producto final, planifica migración a OpenAI Realtime compatible antes de esa fecha.
- No se ha realizado síntesis de voz en vivo con tus credenciales durante la preparación de este paquete.
