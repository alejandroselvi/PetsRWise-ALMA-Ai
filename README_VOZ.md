# ALMA Web v0.5 Voz — PetsRWise (prueba interna)

Este paquete añade **grabación de preguntas y respuestas habladas** a tu Streamlit ya existente, conservando los logos originales PetsRWise, OpenAI, Vector Stores y Web Search.

## Limitaciones importantes
- La voz NO es una persona real y **NO hay avatar con labios sincronizados en este ZIP**. La integración de **HeyGen LiveAvatar** se describe en `INTEGRACION_LIVEAVATAR.md`.
- Sólo casos inventados, sin datos de pacientes ni consulta médica. No es una aplicación clínica.
- La grabación va a OpenAI para transcripción y el texto de respuesta a OpenAI para síntesis de voz; ambos pueden generar gastos API.
- El modo de voz es por turnos, no conversación simultánea de baja latencia.
- El endpoint `gpt-4o-mini-tts` se ha anunciado en ruta de deprecación para enero 2027; para producción usar OpenAI Realtime con WebRTC.

## Instalación Mac / VS Code
1. Descarga el ZIP y déjalo en `~/Downloads`.
2. Desde Terminal de VS Code, copia y ejecuta:

```bash
cd ~/Desktop/"ALMA beta"
cp app.py app_v0_4_respaldo.py
unzip -o ~/Downloads/ALMA_Web_v0_5_Voz_PetsRWise.zip -d .
source .venv/bin/activate
python -m pip install -r requirements_alma_web.txt
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

3. Visita `http://localhost:8501` y en la barra lateral activa **Habilitar micrófono y audio**.
4. Ingresa una pregunta por texto y presiona **Escuchar respuesta**, o graba una pregunta y presiona **Enviar pregunta grabada**. Opcional: activa **Hablar después de responder**.
5. El navegador puede solicitar permiso de micrófono.

## Protecciones
Este ZIP NO contiene `.env`, `alma_chat.py` ni claves privadas. No los borres. Mantén la app en localhost; no uses datos de mascotas reales ni información personal. El aviso de urgencia es ilustrativo y no una validación veterinaria.

Para regresar a la interfaz previa:
```bash
cd ~/Desktop/"ALMA beta"
cp app_v0_4_respaldo.py app.py
python -m streamlit run app.py
```
