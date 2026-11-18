"""PetsRWise ALMA Web v0.6: LatAm Spanish / US English synthetic voice."""
from __future__ import annotations

import os
import base64
from pathlib import Path

from PIL import Image
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

from alma_backend import AlmaProfile, ask_alma, possible_emergency, vector_ids_from_env
from alma_voice import transcribe_recording, synthesize_reply, DEFAULT_SPEED, DEFAULT_VOICE

load_dotenv()

ASSETS_DIR = Path(__file__).resolve().parent / 'assets'
ICON_FILE = ASSETS_DIR / 'petsrwise_icon.png'
WORDMARK_FILE = ASSETS_DIR / 'petsrwise_logo_original.png'
ICON_DATA_URI = ('data:image/png;base64,' + base64.b64encode(ICON_FILE.read_bytes()).decode('ascii'))

st.set_page_config(
    page_title='ALMA | PetsRWise',
    page_icon=Image.open(ICON_FILE),
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={'About': 'ALMA · PetsRWise — desarrollo interno, no uso clínico.'},
)

# Brand styling follows PetsRWise pink/white direction.
# Logos below use user-provided image files stored locally in assets/.
st.markdown('''
<style>
:root {--prw-pink:#EF4A9B;--prw-ink:#262332;--prw-pale:#FFF2F8;--prw-line:#F4DDE9;}
html, body, [class*="css"] {font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;}
.stApp {background:linear-gradient(180deg,#FFF9FC 0%,#FFFFFF 28%,#FFFFFF 100%);color:var(--prw-ink);}
.block-container {max-width:1080px;padding-top:1.25rem;padding-bottom:4rem;}
[data-testid="stSidebar"] {background:#FFF8FC;border-right:1px solid #F6E6EE;}
[data-testid="stSidebar"] .block-container {padding-top:1.4rem;}
.stButton>button[kind="primary"], .stButton>button[data-testid="stBaseButton-primary"] {background:#EF4A9B;border-color:#EF4A9B;border-radius:999px;}
.stButton>button {border-radius:999px;border-color:#EFD8E5;}
.stButton>button:hover {border-color:#ED4097;color:#D62F83;}
.stChatInput textarea {border-radius:18px!important;}
[data-testid="stChatMessage"] {border-radius:18px;border:1px solid #F0E7ED;background:#fff;margin-bottom:12px;box-shadow:0 3px 18px #2E183C08;}
[data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {line-height:1.65;}
.prw-brand {position:sticky;top:28px;z-index:1001;display:flex;align-items:center;gap:12px;margin:28px 0 8px;padding:8px 12px;border:1px solid #F4DFE9;border-radius:18px;background:rgba(255,255,255,.97);box-shadow:0 8px 24px #5A24490D;backdrop-filter:blur(12px);}
.prw-brand img {width:57px;height:57px;border-radius:14px;object-fit:contain;}
.prw-wordmark {font-size:1.55rem;font-weight:820;letter-spacing:-.045em;color:#24212C;line-height:1.05;}
.prw-subbrand {font-size:.73rem;letter-spacing:.12em;color:#A25B85;font-weight:750;margin-top:3px;}
.prw-hero {position:sticky;top:116px;z-index:1000;overflow:hidden;border:1px solid #F7DDEB;border-radius:28px;padding:18px 32px 16px;
 background:linear-gradient(110deg,#FFF0F7 0%,#FFF9FC 67%,#FFFFFF 100%);margin:0 0 16px;box-shadow:0 9px 30px #ED409711;backdrop-filter:blur(12px);}
.prw-hero:after {content:'🐾';position:absolute;right:22px;top:12px;font-size:92px;opacity:.10;transform:rotate(-12deg);}
.prw-kicker {font-size:.74rem;font-weight:820;letter-spacing:.15em;color:#C92D7E;margin-bottom:8px;}
.prw-title {font-weight:840;font-size:2.35rem;line-height:1.12;letter-spacing:-.055em;margin:0 0 11px;color:#262332;}
.prw-title span {color:#E53991;}
.prw-description {font-size:1rem;color:#615968;line-height:1.55;max-width:670px;margin:0;}
.prw-chips {display:flex;gap:8px;flex-wrap:wrap;margin-top:17px;}
.prw-chip {display:inline-block;border:1px solid #F0CDDF;border-radius:999px;background:white;padding:6px 12px;font-size:.79rem;color:#5B5160;font-weight:650;}
.prw-section {font-size:1.08rem;font-weight:770;margin:15px 0 6px;color:#322A37;letter-spacing:-.02em;}
.prw-note {font-size:.77rem;color:#7D7480;line-height:1.5;}
.prw-legal {font-size:.76rem;color:#867D89;text-align:center;margin-top:20px;padding:12px 0;border-top:1px solid #F4E6ED;}

[data-testid="stChatInput"] {position:fixed!important;left:286px!important;right:24px!important;bottom:18px!important;z-index:1002!important;width:auto!important;max-width:none!important;padding:8px 12px!important;border-radius:22px!important;background:rgba(255,255,255,.97)!important;border:1px solid #EED8E4!important;box-shadow:0 10px 32px #5A244912!important;backdrop-filter:blur(12px)!important;}
[data-testid="stChatInput"] textarea {min-height:58px!important;font-size:1rem!important;border-radius:18px!important;line-height:1.5!important;padding:14px 16px!important;}
.block-container {padding-bottom:110px!important;}
</style>
''', unsafe_allow_html=True)

# Exact user-provided PetsRWise icon, served locally without external requests.
st.markdown(f'''<div class="prw-brand">
<img src="{ICON_DATA_URI}" alt="PetsRWise — logotipo original"/>
<div><div class="prw-wordmark">PetsRWise <span style="color:#EF4A9B">ALMA</span></div>
<div class="prw-subbrand">VETERINARY AI · LAB</div></div></div>''', unsafe_allow_html=True)

with st.sidebar:
    st.image(str(WORDMARK_FILE), width=145)
    language = st.selectbox('Idioma / Language', ['Español', 'English'], index=0)
    st.markdown('### 🐾 ' + ('Perfil de prueba' if language == 'Español' else 'Test profile'))

    es = language == 'Español'

    species_es = ['Perro', 'Gato', 'Caballo', 'Bovino', 'Oveja', 'Cabra', 'Cerdo', 'Conejo', 'Ave', 'Reptil']
    species_en = ['Dog', 'Cat', 'Horse', 'Cattle', 'Sheep', 'Goat', 'Pig', 'Rabbit', 'Bird', 'Reptile']
    species = st.selectbox('Especie / Species', species_es if es else species_en, index=0)

    breeds_es = {
        'Perro': ['Mestizo', 'Labrador Retriever', 'Golden Retriever', 'Bulldog Francés', 'Chihuahua', 'Pastor Alemán', 'Poodle', 'Beagle', 'Shih Tzu', 'Yorkshire Terrier', 'Otra raza'],
        'Gato': ['Mestizo', 'Persa', 'Siamés', 'Maine Coon', 'British Shorthair', 'Ragdoll', 'Bengalí', 'Otra raza'],
        'Caballo': ['Criollo', 'Cuarto de Milla', 'Árabe', 'Pura Sangre', 'Paso Fino', 'Otra raza'],
        'Bovino': ['Brahman', 'Holstein', 'Angus', 'Cebú', 'Otra raza'],
        'Oveja': ['Criolla', 'Dorper', 'Merina', 'Otra raza'],
        'Cabra': ['Criolla', 'Saanen', 'Nubia', 'Boer', 'Otra raza'],
        'Cerdo': ['Criollo', 'Duroc', 'Yorkshire', 'Otra raza'],
        'Conejo': ['Criollo', 'Mini Rex', 'Dutch', 'Angora', 'Otra raza'],
        'Ave': ['Canario', 'Periquito', 'Loro', 'Gallina', 'Codorniz', 'Otra raza'],
        'Reptil': ['Iguana verde', 'Gecko', 'Pitón', 'Serpiente', 'Tortuga', 'Otra raza'],
    }
    breeds_en = {
        'Dog': ['Mixed breed', 'Labrador Retriever', 'Golden Retriever', 'French Bulldog', 'Chihuahua', 'German Shepherd', 'Poodle', 'Beagle', 'Shih Tzu', 'Yorkshire Terrier', 'Other breed'],
        'Cat': ['Mixed breed', 'Persian', 'Siamese', 'Maine Coon', 'British Shorthair', 'Ragdoll', 'Bengal', 'Other breed'],
        'Horse': ['Mixed breed', 'American Quarter Horse', 'Arabian', 'Thoroughbred', 'Paso Fino', 'Other breed'],
        'Cattle': ['Mixed breed', 'Brahman', 'Holstein', 'Angus', 'Zebu', 'Other breed'],
        'Bird': ['Canary', 'Parakeet', 'Parrot', 'Chicken', 'Quail', 'Other breed'],
        'Reptile': ['Green Iguana', 'Gecko', 'Python', 'Snake', 'Turtle', 'Other breed'],
    }
    breed_list = (breeds_es if es else breeds_en).get(species, ['Mestizo / Mixed breed', 'Otra raza / Other breed'])
    breed = st.selectbox('Raza / Breed', breed_list, index=0)

    pet_name = st.text_input('Nombre ficticio / Fictitious name', value='Max', max_chars=50)

    usa_states = ['Florida', 'California', 'Texas', 'New York', 'New Jersey', 'Georgia', 'Illinois', 'Pennsylvania', 'Virginia', 'Washington', 'Arizona', 'Colorado', 'North Carolina', 'South Carolina', 'Ohio', 'Michigan', 'Massachusetts', 'Otro estado']
    venezuela_states = ['Distrito Capital', 'Miranda', 'Zulia', 'Carabobo', 'Aragua', 'Lara', 'Anzoátegui', 'Bolívar', 'Táchira', 'Mérida', 'Monagas', 'Sucre', 'Falcón', 'Portuguesa', 'Otro estado']

    usa_cities = {
        'Florida': ['Miami', 'Orlando', 'Tampa', 'Jacksonville', 'Fort Lauderdale', 'West Palm Beach'],
        'California': ['Los Angeles', 'San Diego', 'San Francisco', 'Sacramento', 'Fresno'],
        'Texas': ['Houston', 'Dallas', 'Austin', 'San Antonio', 'Fort Worth'],
        'New York': ['New York City', 'Buffalo', 'Albany', 'Rochester'],
        'New Jersey': ['Newark', 'Jersey City', 'Trenton', 'Atlantic City'],
        'Georgia': ['Atlanta', 'Savannah', 'Augusta', 'Columbus'],
        'Illinois': ['Chicago', 'Springfield', 'Naperville'],
    }
    venezuela_cities = {
        'Distrito Capital': ['Caracas'], 'Miranda': ['Los Teques', 'Petare', 'Guarenas', 'Guatire'],
        'Zulia': ['Maracaibo', 'Cabimas', 'Ciudad Ojeda'], 'Carabobo': ['Valencia', 'Puerto Cabello', 'Naguanagua'],
        'Aragua': ['Maracay', 'Turmero', 'El Limón'], 'Lara': ['Barquisimeto', 'Cabudare'],
        'Anzoátegui': ['Barcelona', 'Puerto La Cruz', 'Lechería'], 'Bolívar': ['Ciudad Bolívar', 'Ciudad Guayana'],
        'Táchira': ['San Cristóbal', 'Táriba'], 'Mérida': ['Mérida', 'El Vigía'],
        'Monagas': ['Maturín'], 'Sucre': ['Cumaná', 'Carúpano'],
        'Falcón': ['Coro', 'Punto Fijo'], 'Portuguesa': ['Acarigua', 'Guanare'],
    }

    country = st.selectbox('País / Country', ['Estados Unidos', 'Venezuela', 'Otro'] if es else ['United States', 'Venezuela', 'Other'], index=0)
    if country in ('Estados Unidos', 'United States'):
        state = st.selectbox('Estado / State', usa_states, index=0)
        city = st.selectbox('Ciudad / City', usa_cities.get(state, ['Otra ciudad / Other city']), index=0)
    elif country == 'Venezuela':
        state = st.selectbox('Estado / State', venezuela_states, index=0)
        city = st.selectbox('Ciudad / City', venezuela_cities.get(state, ['Otra ciudad / Other city']), index=0)
    else:
        state = st.text_input('Estado / región / State', value='', max_chars=70)
        city = st.text_input('Ciudad / City', value='', max_chars=70)

    st.divider()
    use_web_search = st.toggle('Habilitar búsqueda web', value=True,
                               help='Consulta fuentes públicas y puede generar cargos de API. No verifica disponibilidad clínica.')
    st.divider()
    st.markdown('### 🎙️ Voz de ALMA · Demo')
    enable_voice = st.toggle('Habilitar micrófono y audio', value=False,
                             help='La transcripción y la síntesis de voz usan la API de OpenAI y generan consumo.')
    autoplay_reply = st.toggle('Hablar después de responder', value=False,
                               disabled=not enable_voice,
                               help='Puede requerir interacción del navegador para reproducir automáticamente.')
    voice_label = st.selectbox(
        'Voz de ALMA / Voice', ['Marin (natural)', 'Coral (original)', 'Shimmer (alternativa)'],
        index=0, disabled=not enable_voice,
        help='La misma voz sintética para español latinoamericano e inglés estadounidense.'
    )
    speech_voice = {'Marin (natural)': 'marin', 'Coral (original)': 'coral',
                    'Shimmer (alternativa)': 'shimmer'}[voice_label]
    speech_speed = st.slider(
        'Velocidad / Speech speed', min_value=0.80, max_value=1.60,
        value=DEFAULT_SPEED, step=0.05, disabled=not enable_voice,
        help='1.00× = velocidad normal. 1.20× = más ágil, sin perder claridad.'
    )
    st.caption(('Español latinoamericano neutro' if language == 'Español' else
                'United States English') + f' · {speech_speed:.2f}× · Voz IA')
    if enable_voice and st.button('▶ Probar voz / Preview voice', use_container_width=True):
        demo_text = ('Hola, soy ALMA, la asistente de inteligencia artificial de PetsRWise. '
                     'Puedo ayudarte a preparar tus preguntas para un veterinario.'
                     if language == 'Español' else
                     'Hello, I am ALMA, the PetsRWise AI assistant. '
                     'I can help you prepare questions for your veterinarian.')
        if not os.getenv('OPENAI_API_KEY'):
            st.error('Configura OPENAI_API_KEY para escuchar la prueba.')
        else:
            try:
                with st.spinner('Preparando demostración de voz…'):
                    preview_audio = synthesize_reply(
                        OpenAI(timeout=55.0, max_retries=1), demo_text,
                        language, voice=speech_voice, speed=speech_speed)
                st.audio(preview_audio, format='audio/mp3', autoplay=True)
            except Exception as exc:
                st.warning('No se pudo generar la demostración de voz.')
                st.caption(f'Tipo: {type(exc).__name__}')
    st.caption('La voz es sintética. Avatar con labios sincronizados requiere integración adicional.')
    if st.button('↻ Nueva conversación', use_container_width=True):
        st.session_state['voice_widget_rev'] = st.session_state.get('voice_widget_rev', 0) + 1
        st.session_state['messages'] = []
        st.session_state['previous_response_id'] = None
        st.rerun()
    st.divider()
    st.caption('🛡️ Uso interno · Los documentos clínicos siguen pendientes de aprobación veterinaria.')
    st.caption('🔐 No ingreses historias clínicas, datos de clientes ni información sensible.')
    st.markdown('[Visitar PetsRWise ↗](https://www.petsrwise.com/)')

profile = AlmaProfile(species=species.lower(), breed=breed, pet_name=pet_name,
                      language=language, country=country, state=state, city=city)
vector_ids = vector_ids_from_env()
model = os.getenv('ALMA_MODEL', 'gpt-5.4-mini')

settings_signature = (profile.species,profile.breed,profile.pet_name,profile.language,profile.country,
                      profile.state,profile.city,use_web_search,tuple(vector_ids),model)
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'previous_response_id' not in st.session_state:
    st.session_state.previous_response_id = None
if st.session_state.get('settings_signature') != settings_signature:
    st.session_state.messages = []
    st.session_state.previous_response_id = None
    st.session_state.settings_signature = settings_signature

st.markdown('''<section class="prw-hero">
<div class="prw-kicker">PETSRWISE · TU MASCOTA EN EL CENTRO</div>
<h1 class="prw-title">Hola, soy <span>ALMA.</span></h1>
<p class="prw-description">Tu asistente de inteligencia artificial para explorar cuidados veterinarios,
organizar preguntas y descubrir servicios para tu mascota. Juntos, con responsabilidad.</p>
</section>''', unsafe_allow_html=True)

st.warning('**DEMO INTERNA.** No es un veterinario, no diagnostica ni prescribe. '
           'Los documentos siguen siendo borradores; no uses casos reales ni esta demo para emergencias.')

if not os.getenv('OPENAI_API_KEY'):
    st.error('Falta OPENAI_API_KEY en tu archivo .env del directorio ALMA. No compartas la clave.')
if not vector_ids:
    st.warning('No se detectaron Vector Stores. Configura ALMA_VECTOR_STORE_IDS o ALMA_VECTOR_STORE_ID en .env.')

st.markdown('<div class="prw-section">Conversemos sobre tu mascota</div>', unsafe_allow_html=True)
st.caption(f'Perfil ficticio: {pet_name or "Mascota"} · {species} · {city}, {state} · {language} · '
           f'{len(vector_ids)} biblioteca(s) configurada(s) · '
           f'Web Search {"activo" if use_web_search else "desactivado"}')

suggested = [
    '¿Qué información necesitas para una consulta veterinaria?',
    '¿Qué cuidados preventivos existen para esta especie?',
    f'Busca hospitales veterinarios para {species.lower()} en {city}, {state}, {country}.',
] if language == 'Español' else [
    'What information do you need before a veterinary appointment?',
    'What preventive care topics are relevant for this species?',
    f'Find veterinary hospitals for a {species.lower()} in {city}, {state}, {country}.',
]

selected_prompt = None
if not st.session_state.messages:
    st.markdown('<div class="prw-note">Prueba una de estas preguntas ficticias:</div>', unsafe_allow_html=True)
    buttons = st.columns(3)
    for i, label in enumerate(suggested):
        if buttons[i].button(label, key=f'suggest_{i}', use_container_width=True):
            selected_prompt = label

for message_i, message in enumerate(st.session_state.messages):
    with st.chat_message(message['role'], avatar='🐾' if message['role']=='assistant' else '👤'):
        if message.get('warning'):
            st.error(message['warning'])
        st.markdown(message['content'])
        if message['role'] == 'assistant':
            sources = message.get('sources', [])
            with st.expander(f'Fuentes consultadas ({len(sources)})'):
                if sources:
                    for source in sources:
                        icon = '📄' if source['type'] == 'file' else '🌐'
                        if source['url']:
                            st.markdown(f"{icon} [{source['title']}]({source['url']})")
                        else:
                            st.write(f"{icon} {source['title']}")
                else:
                    st.caption('No se recuperaron referencias verificables en este turno.')
            if enable_voice:
                audio_signature = (language, speech_voice, round(speech_speed, 2))
                if message.get('audio_mp3') and message.get('audio_signature') == audio_signature:
                    st.audio(message['audio_mp3'], format='audio/mp3')
                elif st.button('🔊 Escuchar respuesta', key=f'listen_{message_i}'):
                    try:
                        with st.spinner('Generando voz de ALMA…'):
                            audio_bytes = synthesize_reply(OpenAI(timeout=55.0, max_retries=1),
                                                           message['content'], language,
                                                           voice=speech_voice, speed=speech_speed)
                        message['audio_mp3'] = audio_bytes
                        message['audio_signature'] = audio_signature
                        st.audio(audio_bytes, format='audio/mp3')
                    except Exception as exc:
                        st.warning('No se pudo generar la voz. Revisa la API y la facturación.')
                        st.caption(f'Tipo: {type(exc).__name__}')

chat_value = st.chat_input(
    'Escribe tu pregunta para ALMA…' if language == 'Español'
    else 'Ask ALMA a question…',
    accept_audio=enable_voice,
    key='alma_chat_composer',
)

prompt = None
if chat_value:
    if isinstance(chat_value, str):
        prompt = chat_value.strip()
    else:
        prompt = (getattr(chat_value, 'text', '') or '').strip()
        recorded = getattr(chat_value, 'audio', None)
        if recorded is not None:
            if not os.getenv('OPENAI_API_KEY'):
                st.error('Falta OPENAI_API_KEY en el archivo .env.')
            else:
                try:
                    with st.spinner('Transcribiendo tu audio…' if language == 'Español'
                                    else 'Transcribing your audio…'):
                        transcript = transcribe_recording(
                            OpenAI(timeout=60.0, max_retries=1), recorded, language)
                    if transcript:
                        prompt = transcript
                        st.caption(('Transcripción: ' if language == 'Español' else 'Transcript: ') + transcript)
                    else:
                        st.warning('La grabación no produjo una transcripción.' if language == 'Español'
                                   else 'The recording did not produce a transcript.')
                except Exception:
                    st.error('No fue posible transcribir el audio.' if language == 'Español'
                             else 'Could not transcribe the audio.')

if selected_prompt:
    prompt = selected_prompt

if prompt:
    st.session_state.messages.append({'role':'user','content':prompt})
    with st.chat_message('user', avatar='👤'):
        st.markdown(prompt)

    # Show immediate non-clinical warning before ANY potentially slower model/web call.
    imminent_warning = possible_emergency(prompt)
    with st.chat_message('assistant', avatar='🐾'):
        if imminent_warning:
            st.error('⚠️ Posible urgencia: contacta a un veterinario de emergencia AHORA. '
                     'Esta demo no ofrece evaluación clínica ni derivación confirmada.')
        if not os.getenv('OPENAI_API_KEY'):
            st.error('Configura OPENAI_API_KEY primero.')
            st.stop()
        try:
            with st.spinner('ALMA está consultando las fuentes…'):
                reply = ask_alma(
                    client=OpenAI(timeout=45.0, max_retries=1),
                    prompt=prompt,
                    profile=profile,
                    vector_ids=vector_ids,
                    previous_response_id=st.session_state.previous_response_id,
                    use_web_search=use_web_search,
                    model=model,
                )
            st.markdown(reply.text)
            with st.expander(f'Fuentes consultadas ({len(reply.sources)})'):
                if not reply.sources:
                    st.caption('No se recuperaron referencias verificables en este turno.')
                for source in reply.sources:
                    if source['url']:
                        st.markdown(f"🌐 [{source['title']}]({source['url']})")
                    else:
                        st.write(f"📄 {source['title']}")
            message_record = {
                'role':'assistant','content':reply.text,
                'warning': reply.warning if not imminent_warning else None,
                'sources': reply.sources,
            }
            st.session_state.messages.append(message_record)
            st.session_state.previous_response_id = reply.response_id
            if enable_voice and autoplay_reply:
                try:
                    with st.spinner('ALMA está preparando la respuesta hablada…'):
                        audio_bytes = synthesize_reply(OpenAI(timeout=55.0, max_retries=1),
                                                       reply.text, language,
                                                       voice=speech_voice, speed=speech_speed)
                    message_record['audio_mp3'] = audio_bytes
                    message_record['audio_signature'] = (language, speech_voice, round(speech_speed, 2))
                    st.audio(audio_bytes, format='audio/mp3', autoplay=True)
                except Exception as exc:
                    st.warning('ALMA respondió en texto, pero el audio no pudo generarse.')
                    st.caption(f'Tipo: {type(exc).__name__}')
        except Exception as exc:
            # Do not expose potentially sensitive error payloads or credentials in the UI.
            st.error('No se completó la solicitud. Revisa conexión, facturación, modelo y Vector Stores.')
            st.caption(f'Tipo de error: {type(exc).__name__}. Puedes revisar el detalle localmente en VS Code.')
            st.session_state.messages.pop()  # do not chain an unanswered user turn

st.markdown('<div class="prw-legal">PetsRWise · ALMA Web v0.6 Voz LatAm / USA · Laboratorio privado · '
            'Sin diagnósticos, recetas, GPS ni reservas activas · '
            '<a href="https://www.petsrwise.com/">petsrwise.com</a></div>',
            unsafe_allow_html=True)
