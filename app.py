"""ALMA Web v0.7 — PetsRWise branded UX.

INTERNAL DEMO ONLY: fictional pets/scenarios, no clinical decisions, no live vet calls.
Keeps the user's working terminal alma_chat.py and .env untouched.
"""
from __future__ import annotations

import base64
import hashlib
import html
import os
from pathlib import Path
import inspect

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from alma_backend import AlmaProfile, ask_alma, possible_emergency, vector_ids_from_env
from alma_voice import DEFAULT_SPEED, synthesize_reply, transcribe_recording

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")
for secret_name in ("OPENAI_API_KEY", "ALMA_VECTOR_STORE_IDS", "ALMA_VECTOR_STORE_ID", "ALMA_MODEL"):
    if not os.getenv(secret_name):
        try:
            secret_value = st.secrets[secret_name]
            if secret_value:
                os.environ[secret_name] = str(secret_value)
        except Exception:
            pass
ASSETS = ROOT / "assets"
LOGO = ASSETS / "petsrwise_logo_original.png"
ICON = ASSETS / "petsrwise_icon.png"
AVATAR = ASSETS / "portrait_mockup.png"


def uri(filename: str) -> str:
    path = ASSETS / filename
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def tr(es: str, en: str, language: str) -> str:
    return es if language == "Español" else en


st.set_page_config(
    page_title="ALMA | PetsRWise",
    page_icon=Image.open(ICON),
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={"About": "ALMA / PetsRWise — prototipo interno con casos ficticios."},
)

st.markdown("""
<style>
:root{--pink:#EF2990;--pink2:#EE4A9C;--rose:#FFF0F7;--ink:#192036;--muted:#687187;--edge:#EEE9F0;}
.stApp{background-color:#FFFDFC!important;background-image:radial-gradient(circle at 12% 18%,rgba(239,41,144,.055) 0 16px,transparent 17px),radial-gradient(circle at 78% 10%,rgba(239,41,144,.045) 0 12px,transparent 13px),radial-gradient(circle at 88% 72%,rgba(239,41,144,.055) 0 18px,transparent 19px),linear-gradient(135deg,#FFF8FB 0%,#FFFDFC 48%,#FFF4FA 100%)!important;}
[data-testid="stAppViewContainer"]:before{content:"🐾  ·  🐾  ·  🐾";position:fixed;right:34px;top:92px;font-size:2.2rem;color:rgba(239,41,144,.10);letter-spacing:42px;transform:rotate(-18deg);pointer-events:none;z-index:0;}
[data-testid="stSidebar"]{background:white;border-right:1px solid #F0EDF3;}
[data-testid="stSidebar"] .block-container{padding-top:1.5rem;}
[data-testid="stSidebar"] [data-testid="stImage"] img{max-width:174px;object-fit:contain;object-position:left;}
[data-testid="stSidebar"] .stRadio > div{gap:.42rem;}
[data-testid="stSidebar"] [role="radiogroup"] label{background:#FFF;border-radius:13px;padding:.52rem .75rem;}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked){background:#FFF0F7;color:#B61F74;}
.stButton button{border-radius:13px!important;border:1px solid #EDE5EC!important;font-weight:650!important;min-height:41px;}
[data-testid="stChatMessage"]{background:rgba(255,255,255,.96)!important;border:1px solid #F3DDE8!important;border-radius:20px!important;box-shadow:0 6px 18px #A73A7012!important;}
[data-testid="stChatMessage"] p{line-height:1.55;font-family:'Avenir Next',sans-serif!important;}
[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarAssistant"] img,[data-testid="stChatMessage"] [data-testid="stChatMessageAvatarUser"] img{object-fit:cover!important;border-radius:50%!important;}
[data-testid="stChatInput"]{position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:1.35rem!important;max-width:none!important;background:transparent!important;padding:0!important;}
[data-testid="stChatInput"] > div{max-width:none!important;border-radius:26px!important;border:1px solid #E7DFE6!important;background:#FFFFFF!important;box-shadow:0 8px 28px #34213718!important;min-height:58px!important;}
[data-testid="stChatInput"] textarea{min-height:58px!important;max-height:120px!important;border:0!important;border-radius:26px!important;padding:15px 18px!important;font-family:'Avenir Next',sans-serif!important;font-size:.96rem!important;resize:none!important;}
[data-testid="stChatInput"] button{border-radius:50%!important;}
[data-testid="stExpander"]{border:1px solid #EFE6EE;border-radius:14px;background:#fff;}
[data-testid="stAlert"]{border-radius:14px;}
[data-testid="stTextInput"] input,[data-testid="stSelectbox"]>div{border-radius:12px;}
.prw-bar{display:flex;justify-content:flex-start;align-items:center;gap:11px;padding:4px 0 14px;margin-bottom:8px;border-bottom:1px solid #F2EEF3;height:64px;overflow:hidden;}
.prw-brand{display:flex;align-items:center;gap:10px;height:52px;}
.prw-brand-logo{width:48px;height:48px;max-width:48px;max-height:48px;object-fit:contain;border-radius:11px;}
.prw-brand-name{font-size:1.32rem;font-weight:900;color:#24283B;letter-spacing:-.04em;line-height:1;white-space:nowrap;}
.prw-brand-name b{color:#EF2990;}
.prw-brand-lab{display:block;font-size:.62rem;color:#7E6676;font-weight:850;letter-spacing:.12em;text-transform:uppercase;margin-top:5px;}
.prw-hero{background:linear-gradient(110deg,#FCE7F1,#FFF9FC 62%,#FFF0F7);border-radius:25px;padding:23px 26px;display:flex;gap:24px;align-items:center;border:1px solid #F7E1ED;margin-bottom:17px;min-height:215px;}
.prw-face{width:150px!important;height:150px!important;border-radius:28px!important;object-fit:contain!important;background:#FFF;padding:10px;box-shadow:0 10px 22px #D24A8918!important;}
.prw-hero-title{font-size:clamp(1.9rem,3.6vw,3.25rem);font-weight:850;letter-spacing:-.065em;line-height:1.05;margin:0 0 12px;color:#192036;}
.prw-hero-title b{color:#F32588;}
.prw-hero-sub{font-size:1.01rem;color:#3F4354;line-height:1.45;}
.prw-hero-pill{display:inline-block;color:#C82779;background:#FFF0F7;border:1px solid #F8CAE0;border-radius:30px;padding:7px 13px;font-size:.76rem;font-weight:700;margin-top:12px;}
.prw-section{font-size:1.14rem;font-weight:800;letter-spacing:-.03em;margin:15px 0 8px;color:#24283B;}
.prw-muted{color:#788092;font-size:.84rem;line-height:1.5;}
.prw-alert{background:#FFF9FC;border:1px solid #F9DDEB;border-radius:17px;padding:16px 17px;color:#654859;font-size:.81rem;line-height:1.58;margin-top:8px;}
.prw-alert strong{color:#E02079;}
[data-testid="stForm"]{position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:14px!important;width:auto!important;height:72px!important;max-height:72px!important;overflow:hidden!important;background:linear-gradient(100deg,rgba(255,240,247,.98),rgba(255,250,253,.98))!important;border:1px solid #F1C8DE!important;border-radius:22px!important;padding:6px 8px!important;box-shadow:0 8px 28px #A73A701F!important;backdrop-filter:none!important;}
[data-testid="stForm"] [data-testid="stHorizontalBlock"]{height:58px!important;max-height:58px!important;align-items:center!important;overflow:hidden!important;}
[data-testid="stForm"] [data-testid="stColumn"]{height:58px!important;max-height:58px!important;overflow:hidden!important;}
[data-testid="stForm"] [data-testid="stTextInput"] input{height:54px!important;border:1px solid #F2CFE1!important;border-radius:18px!important;background:#FFFFFF!important;box-shadow:none!important;font-size:.96rem!important;padding-left:14px!important;}
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button{height:54px!important;width:54px!important;min-height:54px!important;border-radius:18px!important;background:#EF2990!important;border:0!important;color:white!important;font-size:1.15rem!important;padding:0!important;}
[data-testid="stAudioInput"]{width:60px!important;height:60px!important;max-height:60px!important;border-radius:50%!important;background:linear-gradient(135deg,#FFF0F7,#FFE2F0)!important;border:2px solid #EF2990!important;box-shadow:0 5px 14px #EF299033!important;overflow:hidden!important;}
[data-testid="stAudioInput"] button{width:60px!important;min-width:60px!important;height:60px!important;min-height:60px!important;border-radius:50%!important;border:0!important;background:transparent!important;font-size:1.65rem!important;padding:0!important;color:#C91A70!important;}
[data-testid="stAudioInput"] svg{width:24px!important;height:24px!important;}
[data-testid="stAudioInput"] > div:not(:first-child){display:none!important;}
.main .block-container{padding-bottom:7.5rem!important;}
@media(max-width:1000px){[data-testid="stForm"]{left:1rem!important;right:1rem!important;height:72px!important;}}

div[data-testid="stVerticalBlock"][aria-label="alma_fixed_composer"],
div[data-testid="stElementContainer"]:has(> [aria-label="alma_fixed_composer"]){position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:14px!important;}
[data-key="alma_fixed_composer"]{position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:14px!important;height:72px!important;max-height:72px!important;overflow:hidden!important;background:linear-gradient(100deg,rgba(255,240,247,.98),rgba(255,250,253,.98))!important;border:1px solid #F1C8DE!important;border-radius:22px!important;padding:6px 8px!important;box-shadow:0 8px 28px #A73A701F!important;}

@media(max-width:768px){
  [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2){display:none!important;}
  [data-testid="stMainBlockContainer"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(1){width:100%!important;max-width:100%!important;flex:1 1 100%!important;}
  [data-testid="stSidebar"]{display:none!important;width:0!important;}
  [data-testid="stSidebar"][data-state="expanded"]{display:block!important;width:min(82vw,320px)!important;}
  [data-testid="stChatInput"]{left:.65rem!important;right:.65rem!important;bottom:1.35rem!important;}
  .prw-hero > .prw-face{display:none!important;}
  .prw-hero{min-height:100px!important;padding:16px!important;}
}
</style>
""", unsafe_allow_html=True)

for key, val in {"nav": "chat", "messages": [], "previous_response_id": None, "locator_reply": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Keep navigation simple and left-aligned. The right panel owns the pet profile and voice settings.
with st.sidebar:
    st.image(str(LOGO), width=174)
    st.caption("ALMA · PetsRWise")
    language = st.selectbox("Idioma / Language", ["Español", "English"], key="alma_language")
    routes = {
        "chat": tr("💬 Hablar con ALMA", "💬 Chat with ALMA", language),
        "locator": tr("📍 Buscar veterinario", "📍 Find a veterinarian", language),
        "about": tr("ⓘ Conocer ALMA", "ⓘ About ALMA", language),
    }
    st.radio("Navegación" if language == "Español" else "Navigation",
             list(routes), format_func=lambda k: routes[k], key="nav", label_visibility="collapsed")
    st.divider()
    if st.button(tr("↻ Nueva conversación", "↻ New conversation", language), use_container_width=True):
        st.session_state.messages = []
        st.session_state.previous_response_id = None
        st.session_state.locator_reply = None
        st.rerun()
    st.caption(tr("🔒 Demostración interna. Usa solamente animales y situaciones ficticias.",
                  "🔒 Internal prototype. Use fictional animals and scenarios only.", language))
    st.caption("© PetsRWise · ALMA Web v0.7")

left, right = st.columns([2.42, 1.1], gap="large")

# Right settings panel. These are the same values your existing OpenAI backend expects.
with right:
    st.markdown(f"<div class='prw-panel-title'>🐾 {tr('Perfil de mascota','Pet profile',language)}</div>", unsafe_allow_html=True)
    st.caption(tr("Personaliza el caso ficticio antes de conversar.", "Set up a fictional case before chatting.", language))
    species_choices = {
        "Perro": "Dog", "Gato": "Cat", "Caballo": "Horse", "Bovino": "Cattle",
        "Oveja": "Sheep", "Cabra": "Goat", "Cerdo": "Pig", "Conejo": "Rabbit",
        "Ave": "Bird", "Reptil": "Reptile",
    }
    species = st.selectbox(tr("Especie", "Species", language), list(species_choices),
                           format_func=lambda s: s if language == "Español" else species_choices[s], key="prw_species")
    pet_name = st.text_input(tr("Nombre ficticio", "Fictional pet name", language), value="Max", max_chars=50)

    breed_options = {
        "Perro": ["Criollo / Mestizo", "Golden Retriever", "Labrador Retriever", "Pastor Alemán", "Bulldog", "French Poodle", "Chihuahua", "Beagle", "Otra / No sé"],
        "Gato": ["Criollo / Mestizo", "Persa", "Siamés", "Maine Coon", "Ragdoll", "Bengalí", "Otra / No sé"],
        "Caballo": ["Criollo", "Cuarto de Milla", "Paso Fino", "Árabe", "Frisón", "Otra / No sé"],
        "Bovino": ["Criollo", "Holstein", "Brahman", "Hereford", "Angus", "Otra / No sé"],
        "Oveja": ["Criollo", "Dorper", "Merino", "Otra / No sé"],
        "Cabra": ["Criolla", "Saanen", "Boer", "Alpina", "Otra / No sé"],
        "Cerdo": ["Criollo", "Yorkshire", "Landrace", "Duroc", "Otra / No sé"],
        "Conejo": ["Criollo / Mestizo", "Holandés", "Mini Lop", "Angora", "Otra / No sé"],
        "Ave": ["Mestiza", "Canario", "Periquito", "Papagayo", "Gallina", "Otra / No sé"],
        "Reptil": ["Desconocida", "Gecko", "Iguana", "Serpiente", "Tortuga", "Otra / No sé"],
    }
    breed_es = breed_options.get(species, ["Otra / No sé"])
    breed = st.selectbox(tr("Raza", "Breed", language), breed_es,
                         format_func=lambda b: b if language == "Español" else {
                             "Criollo / Mestizo":"Mixed / Creole", "Criollo":"Creole", "Criolla":"Creole",
                             "Otra / No sé":"Other / Unknown", "Desconocida":"Unknown", "Mestiza":"Mixed",
                         }.get(b, b), key="prw_breed")

    age, sex = st.columns(2)
    with age:
        pet_age = st.number_input(tr("Edad (años)", "Age (years)", language), min_value=0.0, max_value=100.0, value=3.0, step=0.5)
    with sex:
        sex_es = ["Hembra", "Macho", "No sé"]
        pet_sex = st.selectbox(tr("Sexo", "Sex", language), sex_es,
                               format_func=lambda s: s if language == "Español" else {"Hembra":"Female", "Macho":"Male", "No sé":"Unknown"}[s])

    st.markdown(f"<div class='prw-section'>📍 {tr('Ubicación','Location',language)}</div>", unsafe_allow_html=True)
    country = st.selectbox(tr("País", "Country", language), ["Estados Unidos", "Venezuela"])

    state_options = {
        "Estados Unidos": ["Florida", "California", "Texas", "New York", "New Jersey", "Illinois", "Pennsylvania", "Washington", "Georgia", "Arizona", "Otro estado"],
        "Venezuela": ["Distrito Capital", "Miranda", "Zulia", "Carabobo", "Aragua", "Lara", "Anzoátegui", "Bolívar", "Táchira", "Falcón", "Otro estado"],
    }
    region = st.selectbox(tr("Estado / región", "State / region", language), state_options[country],
                          format_func=lambda s: s if language == "Español" or country == "Estados Unidos" else s)
    city = st.text_input(tr("Ciudad", "City", language), value="Miami" if country == "Estados Unidos" else "Caracas", max_chars=70)
    st.caption(tr("Ubicación escrita manualmente; no utilizamos GPS.",
                  "Manually entered location; GPS isn't enabled.", language))
    st.divider()
    st.markdown(f"<div class='prw-section'>🎙️ {tr('Voz de ALMA','ALMA voice',language)}</div>", unsafe_allow_html=True)
    speech_on = st.toggle(tr("Activar voz y micrófono", "Enable voice and microphone", language), value=st.session_state.get("alma_voice_enabled", True), key="alma_voice_toggle")
    st.session_state.alma_voice_enabled = speech_on
    voice_choice = st.selectbox(tr("Timbre", "Voice", language), ["Marin", "Coral", "Shimmer"], disabled=not speech_on)
    speed = st.slider(tr("Velocidad", "Speech speed", language), .80, 1.60, DEFAULT_SPEED, .05, disabled=not speech_on)
    auto_speak = st.toggle(tr("Reproducir automáticamente", "Auto-play answers", language), value=st.session_state.get("alma_autoplay_enabled", True), disabled=not speech_on, key="alma_autoplay_toggle")
    st.session_state.alma_autoplay_enabled = auto_speak
    if speech_on and st.button(tr("▶ Probar voz", "▶ Preview voice", language), use_container_width=True):
        test_text = tr("Hola, soy ALMA, la asistente de inteligencia artificial de PetsRWise.",
                       "Hello, I'm ALMA, the PetsRWise AI assistant.", language)
        try:
            with st.spinner(tr("Generando audio…", "Generating audio…", language)):
                preview = synthesize_reply(OpenAI(timeout=60, max_retries=1),
                                           test_text, language, voice_choice.lower(), speed)
            st.audio(preview, format="audio/mp3")
        except Exception as ex:
            st.warning(tr("No fue posible generar audio.", "Couldn't generate audio.", language))
            st.caption(type(ex).__name__)
    st.caption(tr("Español latinoamericano / inglés estadounidense. Voz sintética, por turnos.",
                  "LatAm Spanish / US English. Synthetic, turn-based speech.", language))
    st.divider()
    st.markdown(f"<div class='prw-section'>📚 {tr('Fuentes de información','Information sources',language)}</div>", unsafe_allow_html=True)
    web_on = st.toggle(tr("Permitir búsqueda web", "Allow web search", language), value=True)
    vectors = vector_ids_from_env()
    st.caption(f"{len(vectors)} Vector Store(s) " + tr("configurados", "configured", language))
    if not vectors:
        st.warning(tr("No hay vectores configurados.", "No vector stores configured.", language))
    st.markdown(f"<div class='prw-alert'><strong>⚠️ {tr('Importante','Important',language)}</strong><p>"
                + tr("ALMA no es veterinaria ni reemplaza una consulta. En una emergencia real, acude inmediatamente a un centro veterinario. No ingreses información personal ni casos reales en esta demo.",
                     "ALMA is not a veterinarian or a substitute for a consultation. For real emergencies, seek veterinary care immediately. Don't enter real cases or personal information in this demo.",language)
                + "</p></div>",unsafe_allow_html=True)

profile_values = {
    "species": species.lower(),
    "pet_name": pet_name,
    "breed": breed,
    "age": float(pet_age),
    "sex": pet_sex,
    "language": language,
    "country": country,
    "state": region,
    "city": city,
}
profile_parameters = inspect.signature(AlmaProfile).parameters
profile = AlmaProfile(**{name: value for name, value in profile_values.items() if name in profile_parameters})
model = os.getenv("ALMA_MODEL", "gpt-5.4-mini")
profile_breed = getattr(profile, "breed", breed)
profile_age = getattr(profile, "age", float(pet_age))
profile_sex = getattr(profile, "sex", pet_sex)
signature = (profile.species, profile.pet_name, profile_breed, profile_age, profile_sex,
             profile.language, profile.country, profile.state, profile.city,
             tuple(vectors), model, web_on)
if st.session_state.get("profile_signature") not in (None, signature):
    st.session_state.messages = []
    st.session_state.previous_response_id = None
    st.session_state.locator_reply = None
st.session_state.profile_signature = signature


def sources_panel(sources: list[dict], key: str) -> None:
    with st.expander(tr("Fuentes consultadas", "Sources consulted",language) + f" · {len(sources)}"):
        if not sources:
            st.caption(tr("No se recuperaron fuentes en este turno. No se ha verificado la información.",
                          "No sources retrieved this turn. Information isn't verified.", language))
        for index, source in enumerate(sources):
            title = source.get("title", "") or "Referencia"
            st.write(("📄 " if source.get("type") == "file" else "🌐 ") + title)
            url = source.get("url")
            if isinstance(url, str) and url.startswith(("https://", "http://")):
                st.link_button(tr("Abrir fuente", "Open source",language), url)


def ask(question: str, do_web: bool, previous: str | None):
    return ask_alma(OpenAI(timeout=60, max_retries=1), question, profile, vectors,
                    previous_response_id=previous, use_web_search=do_web, model=model)

with left:
    st.markdown(f"""<header class="prw-bar"><div class="prw-brand"><img class="prw-brand-logo" src="{uri('petsrwise_icon.png')}" alt="PetsRWise"><div><span class="prw-brand-name">PetsRWise <b>Alma</b></span><span class="prw-brand-lab">Veterinary AI LAB</span></div></div></header>""",unsafe_allow_html=True)
    st.markdown(f"""<section class="prw-hero"><img class="prw-face" src="{uri('petsrwise_icon.png')}" alt="Logo oficial de PetsRWise">
    <div><div class="prw-hero-title">{tr('Hola, soy','Hello, I’m',language)} <b>ALMA</b></div>
    <div class="prw-hero-sub">{tr('Tu asistente de IA para bienestar animal, información y orientación hacia atención veterinaria.','Your AI assistant for animal wellness information and finding veterinary services.',language)}</div>
    <span class="prw-hero-pill">✦ {tr('Avatar ilustrativo · No es médica veterinaria','Illustrative avatar · Not a veterinarian',language)}</span></div></section>""",unsafe_allow_html=True)
    if st.session_state.nav == "chat":
        if not st.session_state.messages:
            st.markdown(f"<div class='prw-section'>👋 {tr('¿Qué te gustaría hacer hoy?','How can I help today?',language)}</div>",unsafe_allow_html=True)
            st.markdown(f"<div class='prw-muted'>{tr('Elige una opción o escribe una pregunta sobre un caso ficticio.','Choose an option or ask about a fictional case.',language)}</div>",unsafe_allow_html=True)
            actions = [
                ("dog_mockup.png", "🩺 " + tr("Síntomas", "Symptoms",language),
                 tr("¿Qué preguntas debo preparar sobre los síntomas de mi perro ficticio?", "What questions should I prepare about my fictional dog's symptoms?",language)),
                ("cat_mockup.png", "♡ " + tr("Cuidados", "Care",language),
                 tr("¿Qué cuidados preventivos generales son apropiados para esta especie?", "What general preventive care applies to this species?",language)),
                ("hospital_mockup.png", "📍 " + tr("Buscar veterinario", "Find a veterinarian",language), "__locator__"),
                ("pets_mockup.png", "🐾 " + tr("Mis mascotas", "My pets",language), "__profile__"),
            ]
            cols = st.columns(4, gap="small")
            suggestion = None
            for idx, (pic, title, question) in enumerate(actions):
                with cols[idx]:
                    st.markdown(f"<img class='prw-card-image' src='{uri(pic)}' alt='{esc(title)}'>",unsafe_allow_html=True)
                    if question == "__locator__":
                        # Streamlit callbacks execute before keyed widgets are instantiated.
                        st.button(title, key=f"action_{idx}", use_container_width=True,
                                  on_click=lambda: st.session_state.update(nav="locator"))
                    elif st.button(title, key=f"action_{idx}", use_container_width=True):
                        if question == "__profile__":
                            st.info(tr("El perfil de prueba está a la derecha. La gestión real de mascotas llegará más adelante.",
                                       "Your test profile is on the right. Actual pet-account management is not connected.",language))
                        else:
                            suggestion = question
            st.divider()
        else:
            suggestion = None
        for idx, item in enumerate(st.session_state.messages):
            avatar = str(ICON) if item["role"] == "assistant" else "👤"
            with st.chat_message(item["role"], avatar=avatar):
                st.markdown(item["content"])
                if item["role"] == "assistant":
                    sources_panel(item.get("sources", []), f"source_{idx}")
                    if speech_on and not item.get("emergency"):
                        sig = (language, voice_choice, speed)
                        if item.get("audio") and item.get("audio_sig") == sig:
                            st.audio(item["audio"], format="audio/mp3")
                        elif st.button(tr("🔊 Escuchar", "🔊 Listen", language), key=f"listen_{idx}"):
                            try:
                                with st.spinner(tr("Generando voz…", "Generating speech…", language)):
                                    audio = synthesize_reply(OpenAI(timeout=60, max_retries=1), item["content"], language, voice_choice.lower(), speed)
                                item["audio"], item["audio_sig"] = audio, sig
                                st.audio(audio, format="audio/mp3")
                            except Exception as ex:
                                st.warning(tr("La voz no está disponible.", "Voice is unavailable.", language))
                                st.caption(type(ex).__name__)
        chat_value = st.chat_input(
            tr("Pregúntale a ALMA…", "Ask ALMA…", language),
            key="alma_native_chat",
            accept_audio=speech_on,
            submit_mode="submit",
        )

        question = None
        if chat_value is not None:
            question_text = getattr(chat_value, "text", None)
            question_audio = getattr(chat_value, "audio", None)
            if question_audio is not None:
                try:
                    with st.spinner(tr("Transcribiendo y enviando…", "Transcribing and sending…", language)):
                        question = transcribe_recording(OpenAI(timeout=60, max_retries=1), question_audio, language)
                except Exception as ex:
                    st.error(tr("No se pudo transcribir la grabación.", "Unable to transcribe recording.", language))
                    st.caption(type(ex).__name__)
            elif isinstance(question_text, str) and question_text.strip():
                question = question_text.strip()

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)
            with st.chat_message("assistant", avatar=str(ICON)):
                if possible_emergency(question):
                    msg = tr("⚠️ Si este caso fuera real, busca atención veterinaria de emergencia inmediatamente. Esta demo no puede evaluar pacientes.",
                             "⚠️ If this were a real case, seek emergency veterinary care immediately. This demo cannot assess patients.",language)
                    st.error(msg)
                    st.session_state.messages.append({"role":"assistant", "content":msg, "emergency":True, "sources":[]})
                elif not os.getenv("OPENAI_API_KEY"):
                    st.error(tr("Agrega OPENAI_API_KEY a .env.", "Add OPENAI_API_KEY to .env.",language))
                    st.session_state.messages.pop()
                else:
                    try:
                        with st.spinner(tr("ALMA está preparando tu respuesta…", "ALMA is preparing your answer…", language)):
                            result = ask(question, web_on, st.session_state.previous_response_id)
                        st.markdown(result.text)
                        sources_panel(result.sources, "latest_sources")
                        entry = {"role":"assistant", "content":result.text, "sources":result.sources}
                        st.session_state.messages.append(entry)
                        st.session_state.previous_response_id = result.response_id
                        if speech_on:
                            try:
                                speech = synthesize_reply(OpenAI(timeout=60, max_retries=1), result.text, language, voice_choice.lower(), speed)
                                entry["audio"], entry["audio_sig"] = speech, (language,voice_choice,speed)
                                st.audio(speech, format="audio/mp3", autoplay=True)
                            except Exception as ex:
                                st.caption(tr("Respuesta de texto lista; audio no disponible.", "Text reply is ready; audio unavailable.",language))
                                st.caption(f"{type(ex).__name__}: {str(ex)[:500]}")
                    except Exception as ex:
                        st.error(tr("Error de conexión a OpenAI; revisa credenciales, vectores o red.",
                                    "OpenAI connection error; check credentials, vector stores or internet.",language))
                        st.caption(type(ex).__name__)
                        st.session_state.messages.pop()
    elif st.session_state.nav == "locator":
        st.markdown(f"<div class='prw-section'>📍 {tr('Encuentra un veterinario','Find a veterinarian',language)}</div>",unsafe_allow_html=True)
        st.markdown(f"<p class='prw-muted'>{tr('ALMA busca resultados públicos por ciudad y especie. No confirma horarios ni disponibilidad.', 'ALMA searches public listings by city and species. Hours and availability are not confirmed.',language)}</p>",unsafe_allow_html=True)
        with st.form("vet_search"):
            c1,c2 = st.columns(2)
            with c1:
                search_city = st.text_input(tr("Ciudad", "City",language), value=city)
                search_species = st.selectbox(tr("Especie", "Species",language), list(species_choices),
                                               index=list(species_choices).index(species),
                                               format_func=lambda s: s if language=="Español" else species_choices[s])
            with c2:
                search_state = st.text_input(tr("Estado / región", "State / region",language), value=region)
                service = st.selectbox(tr("Necesidad", "Need",language),
                                       [tr("Consulta general", "General care",language),
                                        tr("Especialista", "Specialist",language),
                                        tr("Hospital de emergencias", "Emergency hospital",language)])
            submitted = st.form_submit_button(tr("Buscar opciones", "Search options",language), type="primary", use_container_width=True)
        if submitted:
            if not search_city.strip():
                st.warning(tr("Escribe una ciudad.", "Enter a city.",language))
            elif not os.getenv("OPENAI_API_KEY"):
                st.warning(tr("Primero configura tu API key.", "Configure your API key first.",language))
            else:
                query = (f"INTERNAL FICTIONAL VET LOCATOR TEST. Search web for up to three real veterinary facilities "
                         f"for {search_species} in {search_city}, {search_state}, {country}; care type: {service}. "
                         "Only include results with sources. Provide grounded address and URL. Do not invent services, hours, "
                         "availability, phone numbers, partnerships or bookings. Recommend contacting clinics to confirm "
                         f"species suitability. Respond in {'Spanish' if language == 'Español' else 'English'}.")
                try:
                    with st.spinner(tr("Buscando fuentes públicas…", "Searching public sources…",language)):
                        st.session_state.locator_reply = ask(query, True, None)
                except Exception as ex:
                    st.error(tr("La búsqueda no pudo completarse.", "Search failed.",language))
                    st.caption(type(ex).__name__)
        res = st.session_state.locator_reply
        if res:
            st.markdown(res.text)
            sources_panel(res.sources, "locator_sources")
            st.info(tr("Los resultados no son socios verificados de PetsRWise. Verifica por teléfono que atiendan la especie y estén disponibles.",
                       "Results are not verified PetsRWise partners. Call to confirm species coverage and availability.",language))
        st.caption(tr("Sin GPS ni reservas automáticas. Para una emergencia real, no demores buscando en esta demo.",
                      "No GPS or automatic bookings. For a real emergency, don't delay care to use this demo.", language))
    else:
        st.markdown(f"<div class='prw-section'>✨ {tr('Conoce ALMA','About ALMA',language)}</div>",unsafe_allow_html=True)
        st.write(tr("ALMA es una asistente de IA de PetsRWise para educación general, organización de preguntas y descubrimiento de opciones de atención veterinaria.",
                    "ALMA is a PetsRWise AI assistant for general education, organizing questions, and finding veterinary services.",language))
        st.info(tr("Esta versión utiliza bibliotecas clínicas en borrador. No equivale a un veterinario ni está lista para atender casos reales.",
                   "This build uses draft clinical knowledge. It is not a veterinarian and is not ready for real cases.",language))
        st.markdown(tr("**Próximas funciones:** videopersona sincronizada, directorio de clínicas verificadas y transferencia a profesionales acreditados.",
                       "**Upcoming:** lip-synced avatar, verified hospital directory, and handoff to licensed professionals.",language))
    st.markdown("<div class='prw-footer'>© PetsRWise · ALMA Web v0.7 · "
                "<a href='https://www.petsrwise.com/' target='_blank' rel='noopener noreferrer'>petsrwise.com</a></div>",unsafe_allow_html=True)
