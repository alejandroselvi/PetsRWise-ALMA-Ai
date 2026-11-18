# ALMA con persona digital realista que habla y mueve los labios

## Solución recomendada: LiveAvatar de HeyGen

### Objetivo
La cara y los labios NO se crean ni se animan con OpenAI File Search o Streamlit: necesitas un servicio de video-avatar en tiempo real. La voz y el conocimiento de ALMA seguirán conectados a las bibliotecas veterinarias existentes.

### Paso 1 — Crear avatar
- Entra a https://app.liveavatar.com/ (no la sección habitual de generación de videos de HeyGen).
- Utiliza un avatar de biblioteca para las pruebas, o crea uno propio de **una actriz o persona con consentimiento expreso**. LiveAvatar documenta creación por foto o video, sujeto a sus requisitos y plan.
- Selecciona una voz en español latinoamericano y prueba expresiones, acento y calidad.
- Identifica siempre a ALMA como **asistente IA**, aunque el avatar sea humano y use una bata.

### Paso 2 — Elegir modo
- **FULL**: el proveedor gestiona voz y diálogo. Es más rápido para una prueba de persona digital, pero **no hereda** automáticamente tu código ni tus Vector Stores.
- **LITE**: conectar tu propia capa de OpenAI (incluyendo File Search, Web Search, rutas a veterinarios y seguridad) con el avatar por SDK/API. Es la arquitectura indicada para ALMA.

### Paso 3 — Integrar en un frontend con WebRTC
El stack recomendado para voz en vivo es una app web en React/TypeScript, con OpenAI Realtime (o la canalización propia de audio), y el Web SDK de LiveAvatar para mostrar video/labios. Streamlit v0.5 sirve como demostración de voz **por turnos**, pero no sustituye la integración de WebRTC.

Arquitectura:
```
Usuario en web/móvil/kiosco (micrófono + pantalla)
   ↓
Backend PetsRWise (autenticación + permisos + supervisión)
   ↓
OpenAI: interpretación + conocimiento (Vector Stores) + búsqueda web
   ↓
Audio conversacional en tiempo real
   ↓
HeyGen LiveAvatar LITE (rostro humano y labios sincronizados)
   ↓
Usuario recibe respuesta audiovisual
```

### Paso 4 — Reglas de producto
- No presentar el avatar como veterinario licenciado, profesional de carne y hueso ni doctorado.
- Para emergencias, priorizar alerta y escalamiento de forma independiente del avatar.
- Requiere revisión por veterinarios habilitados para cada país/estado, evaluación y privacidad antes de uso real.
- La transferencia a **una persona real** requiere otro componente: teleconsulta con veterinario licenciado, verificación de disponibilidad, consentimiento y reglas locales.

## Documentación
- LiveAvatar: https://help.heygen.com/en/articles/12758516-introducing-liveavatar
- Web SDK LiveAvatar: https://help.heygen.com/en/articles/10035615-how-to-get-started-with-liveavatar
- OpenAI Realtime WebRTC: https://developers.openai.com/api/docs/guides/voice-webrtc
