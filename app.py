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
import json

import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image

from alma_backend import AlmaProfile, ask_alma, possible_emergency, emergency_message, vector_ids_from_env
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
SPECIES_CHOICES = {
    "Perro": "Dog", "Gato": "Cat", "Caballo": "Horse", "Bovino": "Cattle",
    "Oveja": "Sheep", "Cabra": "Goat", "Cerdo": "Pig", "Conejo": "Rabbit",
    "Ave": "Bird", "Reptil": "Reptile",
}


def uri(filename: str) -> str:
    path = ASSETS / filename
    mime = "image/jpeg" if path.suffix.lower() in {".jpg", ".jpeg"} else "image/png"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"



def follow_chat_response(enabled: bool) -> None:
    """Follow new response content; let readers scroll up without being pulled back."""
    components.html(
        """<script>
        (() => {
            const doc = window.parent.document;
            const host = window.parent;
            if (host.__almaChatFollowCleanup) host.__almaChatFollowCleanup();
            let following = FOLLOW_ENABLED;
            let frame = 0;
            let disposed = false;
            const reducedMotion = host.matchMedia('(prefers-reduced-motion: reduce)').matches;
            const messages = () => doc.querySelectorAll('[data-testid="stChatMessage"]');
            function follow() {
                frame = 0;
                if (!following || disposed) return;
                const list = messages();
                const latest = list[list.length - 1];
                if (latest) latest.scrollIntoView({block: 'end', behavior: reducedMotion ? 'instant' : 'smooth'});
            }
            function schedule() {
                if (following && !frame) frame = host.requestAnimationFrame(follow);
            }
            const observed = new WeakSet();
            const resize = new host.ResizeObserver(schedule);
            function watchMessages() {
                messages().forEach(message => {
                    message.style.scrollMarginBottom = '140px';
                    if (!observed.has(message)) { resize.observe(message); observed.add(message); }
                });
            }
            const root = doc.querySelector('[data-testid="stMain"]') || doc.querySelector('[data-testid="stAppViewContainer"]');
            if (!root) return;
            const mutations = new host.MutationObserver(() => { watchMessages(); schedule(); });
            mutations.observe(root, {childList: true, subtree: true, characterData: true});
            const wheel = event => { if (event.deltaY < 0) following = false; };
            const keyboard = event => {
                if (event.target.closest('input, textarea, [contenteditable="true"]')) return;
                if (['ArrowUp', 'PageUp', 'Home'].includes(event.key)) following = false;
            };
            let touchY = null;
            const touchStart = event => { touchY = event.touches[0]?.clientY ?? null; };
            const touchMove = event => {
                if (touchY !== null && event.touches[0]?.clientY > touchY + 5) following = false;
            };
            doc.addEventListener('wheel', wheel, {passive: true});
            doc.addEventListener('keydown', keyboard);
            doc.addEventListener('touchstart', touchStart, {passive: true});
            doc.addEventListener('touchmove', touchMove, {passive: true});
            const cleanup = () => {
                disposed = true;
                mutations.disconnect(); resize.disconnect(); host.cancelAnimationFrame(frame);
                doc.removeEventListener('wheel', wheel); doc.removeEventListener('keydown', keyboard);
                doc.removeEventListener('touchstart', touchStart); doc.removeEventListener('touchmove', touchMove);
                if (host.__almaChatFollowCleanup === cleanup) delete host.__almaChatFollowCleanup;
            };
            host.__almaChatFollowCleanup = cleanup;
            window.addEventListener('pagehide', cleanup, {once: true});
            watchMessages(); schedule();
        })();
        </script>""".replace("FOLLOW_ENABLED", "true" if enabled else "false"),
        height=0,
    )


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

wordmark_font = base64.b64encode((ASSETS / "HeyComic.otf").read_bytes()).decode("ascii")
st.markdown(
    "<style>@font-face{font-family:PetsRWiseHeyComics;src:url(data:font/otf;base64,"
    + wordmark_font
    + ") format('opentype');font-weight:400;font-style:normal;font-display:swap;}"
    + ".prw-wordmark{font-size:1.12em;color:#EF4A9B!important;font-family:PetsRWiseHeyComics,sans-serif!important;font-weight:400!important;letter-spacing:0;line-height:1.15;}</style>",
    unsafe_allow_html=True,
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
.prw-sidebar-brand{display:flex;align-items:center;gap:12px;margin:0 0 20px;}
.prw-sidebar-brand img{width:60px;height:60px;object-fit:contain;flex-shrink:0;}
.prw-sidebar-brand-name{font-size:21px;font-weight:750;line-height:1.2;color:#262332;}
.prw-sidebar-brand-name b{color:#2563EB;font-family:PetsRWiseHeyComics,sans-serif!important;font-weight:400!important;letter-spacing:0;}
.prw-sidebar-brand-lab{font-size:13px;font-weight:600;letter-spacing:.04em;color:#62596B;margin-top:5px;}
.prw-brand-logo{width:56px;height:56px;max-width:56px;max-height:56px;object-fit:contain;border-radius:11px;}
.prw-brand-name{font-size:1.32rem;font-weight:900;color:#24283B;letter-spacing:-.04em;line-height:1;white-space:nowrap;}
.prw-brand-name b{color:#2563EB;font-family:PetsRWiseHeyComics,sans-serif!important;font-weight:400!important;letter-spacing:0;}
.prw-brand-lab{display:block;font-size:.62rem;color:#7E6676;font-weight:850;letter-spacing:.12em;text-transform:uppercase;margin-top:5px;}
.prw-hero{background:linear-gradient(110deg,#FCE7F1,#FFF9FC 62%,#FFF0F7);border-radius:25px;padding:23px 26px;display:flex;gap:24px;align-items:center;border:1px solid #F7E1ED;margin-bottom:17px;min-height:215px;}
.prw-face{width:150px!important;height:150px!important;border-radius:28px!important;object-fit:contain!important;background:#FFF;padding:10px;box-shadow:0 10px 22px #D24A8918!important;}
.prw-hero-title{font-size:clamp(1.9rem,3.6vw,3.25rem);font-weight:850;letter-spacing:-.065em;line-height:1.05;margin:0 0 12px;color:#192036;}
.prw-hero-title b{color:#F32588;}
.prw-hero-sub{font-size:1.01rem;color:#3F4354;line-height:1.45;}
.prw-hero-pill{display:inline-block;color:#C82779;background:#FFF0F7;border:1px solid #F8CAE0;border-radius:30px;padding:7px 13px;font-size:.76rem;font-weight:700;margin-top:12px;}
.st-key-vet_search,[data-testid="stForm"]{position:relative;height:auto;max-height:none;overflow:visible;background:#FFFFFF;border:1px solid #F2C7DC!important;border-radius:20px!important;padding:24px!important;}
[data-testid="stForm"] [data-testid="stWidgetLabel"] p{font-size:1rem!important;font-weight:700!important;color:#262332!important;}
[data-testid="stFormSubmitButton"] button{min-height:48px!important;width:100%!important;background:#EF2990!important;color:white!important;border-radius:12px!important;}
.prw-locator-intro{padding:24px;margin:12px 0 22px;background:#FFF0F7;border:1px solid #F2C7DC;border-radius:20px;}
.prw-locator-label{color:#A91E60;font-size:.8rem;font-weight:800;letter-spacing:.08em;}
.prw-locator-intro h1{font-size:clamp(1.7rem,3vw,2.3rem);line-height:1.15;color:#192036;margin:10px 0 14px;}
.prw-locator-intro p{font-size:1rem;color:#3F4354;line-height:1.6;}
.prw-locator-steps{font-size:.9rem;font-weight:700;line-height:1.7;color:#263D80;margin-top:16px;}
.prw-section{font-size:1.14rem;font-weight:800;letter-spacing:-.03em;margin:15px 0 8px;color:#24283B;}
.prw-muted{color:#788092;font-size:.84rem;line-height:1.5;}
.prw-alert{background:#FFF9FC;border:1px solid #F9DDEB;border-radius:17px;padding:16px 17px;color:#654859;font-size:.81rem;line-height:1.58;margin-top:8px;}
.prw-alert strong{color:#E02079;}
[data-testid="stForm"] [data-testid="stTextInput"] input{height:54px!important;border:1px solid #F2CFE1!important;border-radius:18px!important;background:#FFFFFF!important;box-shadow:none!important;font-size:.96rem!important;padding-left:14px!important;}
[data-testid="stAudioInput"]{width:60px!important;height:60px!important;max-height:60px!important;border-radius:50%!important;background:linear-gradient(135deg,#FFF0F7,#FFE2F0)!important;border:2px solid #EF2990!important;box-shadow:0 5px 14px #EF299033!important;overflow:hidden!important;}
[data-testid="stAudioInput"] button{width:60px!important;min-width:60px!important;height:60px!important;min-height:60px!important;border-radius:50%!important;border:0!important;background:transparent!important;font-size:1.65rem!important;padding:0!important;color:#C91A70!important;}
[data-testid="stAudioInput"] svg{width:24px!important;height:24px!important;}
[data-testid="stAudioInput"] > div:not(:first-child){display:none!important;}
.main .block-container{padding-bottom:7.5rem!important;}

div[data-testid="stVerticalBlock"][aria-label="alma_fixed_composer"],
div[data-testid="stElementContainer"]:has(> [aria-label="alma_fixed_composer"]){position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:14px!important;}
[data-key="alma_fixed_composer"]{position:fixed!important;z-index:1000!important;left:calc(19rem + 2.1rem)!important;right:2.1rem!important;bottom:14px!important;height:72px!important;max-height:72px!important;overflow:hidden!important;background:linear-gradient(100deg,rgba(255,240,247,.98),rgba(255,250,253,.98))!important;border:1px solid #F1C8DE!important;border-radius:22px!important;padding:6px 8px!important;box-shadow:0 8px 28px #A73A701F!important;}

@media(max-width:768px){
  [data-testid="stForm"]{padding:16px!important;}
  [data-testid="stForm"] [data-testid="stHorizontalBlock"]{flex-direction:column!important;gap:1rem!important;}
  [data-testid="stForm"] [data-testid="stColumn"]{width:100%!important;min-width:0!important;flex:1 1 auto!important;}
  [data-testid="stSidebar"][aria-expanded="true"]{width:min(88vw,350px)!important;max-width:min(88vw,350px)!important;z-index:1002!important;box-shadow:8px 0 32px #26233226;}
  [data-testid="stSidebar"][aria-expanded="false"]{width:0!important;min-width:0!important;max-width:0!important;visibility:hidden;}
  [data-testid="stExpandSidebarButton"]{min-width:44px!important;min-height:44px!important;border-radius:12px!important;background:#FFF0F7!important;color:#A91E60!important;}
  [data-testid="stExpandSidebarButton"] svg,[data-testid="stExpandSidebarButton"] span{display:none!important;}
  [data-testid="stExpandSidebarButton"]::before{content:"☰";font-size:26px;line-height:1;}
  [data-testid="stSidebarCollapseButton"], [data-testid="stSidebarCollapseButton"] button{min-width:44px!important;min-height:44px!important;}
  [data-testid="stMainBlockContainer"]{padding-left:1rem!important;padding-right:1rem!important;padding-bottom:8rem!important;}
  .prw-brand-name{font-size:1.15rem;}
  .prw-brand-logo{width:48px;height:48px;max-width:48px;max-height:48px;}
  .prw-hero-title{font-size:1.8rem;}
  .prw-hero-sub{font-size:.95rem;}
  .st-key-alma_main_content{width:100%;min-width:0;}
  [data-testid="stSidebar"][aria-expanded="true"] ~ [data-testid="stMain"]{margin-left:0!important;}
  [data-testid="stSidebar"] .block-container{padding:1rem 1.1rem 2rem!important;}
  [data-testid="stSidebar"] [data-testid="stExpander"]{margin:.25rem 0!important;}
  [data-testid="stChatInput"]{left:.65rem!important;right:.65rem!important;bottom:calc(.75rem + env(safe-area-inset-bottom))!important;z-index:999!important;}
  .prw-hero > .prw-face{display:block!important;width:82px!important;height:82px!important;border-radius:18px!important;object-fit:cover!important;padding:0!important;}
  .prw-hero{min-height:100px!important;padding:16px!important;}
}
</style>
""", unsafe_allow_html=True)

for key, val in {"nav": "chat", "messages": [], "previous_response_id": None, "locator_reply": None}.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Safe defaults for hamburger controls.
mobile_species = "Perro"
mobile_pet_name = "Max"
mobile_breed = "Criollo / Mestizo"
mobile_pet_age = 3.0
mobile_sex_choice = "Hembra"
mobile_country = "Estados Unidos"
mobile_region = "Florida"
mobile_city = "Miami"
mobile_speech_on = True
mobile_voice_choice = "Marin"
mobile_speed = DEFAULT_SPEED
mobile_auto_speak = True
mobile_web_on = True

# Keep navigation simple and left-aligned. The right panel owns the pet profile and voice settings.
with st.sidebar:
    st.markdown(f"""<div class="prw-sidebar-brand"><a href="https://www.petsrwise.com/" target="_blank" rel="noopener noreferrer" aria-label="PetsRWise website"><img src="{uri('petsrwise_website_logo.png')}" alt="PetsRWise"></a><div><div class="prw-sidebar-brand-name"><span class="prw-wordmark">PetsRWise</span> <b>Alma</b></div><div class="prw-sidebar-brand-lab">Veterinary Lab</div></div></div>""", unsafe_allow_html=True)
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

    with st.expander(tr("🐾 Perfil de mascota", "🐾 Pet profile", language), expanded=False):
        mobile_species = st.selectbox(tr("Especie", "Species", language), list(SPECIES_CHOICES),
                                      format_func=lambda s: s if language == "Español" else SPECIES_CHOICES[s],
                                      key="mobile_species")
        mobile_pet_name = st.text_input(tr("Nombre ficticio", "Fictional pet name", language), value="Max", max_chars=50, key="mobile_pet_name")
        mobile_breeds = {
            "Perro": ["Criollo / Mestizo", "Golden Retriever", "Labrador Retriever", "Pastor Alemán", "Bulldog", "Otra / No sé"],
            "Gato": ["Criollo / Mestizo", "Persa", "Siamés", "Maine Coon", "Ragdoll", "Otra / No sé"],
            "Caballo": ["Criollo", "Paso Fino", "Árabe", "Frisón", "Otra / No sé"],
            "Bovino": ["Criollo", "Holstein", "Brahman", "Hereford", "Angus", "Otra / No sé"],
            "Ave": ["Mestiza", "Canario", "Periquito", "Papagayo", "Gallina", "Otra / No sé"],
        }
        mobile_breed = st.selectbox(tr("Raza", "Breed", language), mobile_breeds.get(mobile_species, ["Otra / No sé"]), key="mobile_breed")
        mobile_age, mobile_sex = st.columns(2)
        with mobile_age:
            mobile_pet_age = st.number_input(tr("Edad", "Age", language), 0.0, 100.0, 3.0, 0.5, key="mobile_age")
        with mobile_sex:
            mobile_sex_choice = st.selectbox(tr("Sexo", "Sex", language), ["Hembra", "Macho", "No sé"],
                                             format_func=lambda s: s if language == "Español" else {"Hembra":"Female", "Macho":"Male", "No sé":"Unknown"}[s],
                                             key="mobile_sex")

    with st.expander(tr("📍 Ubicación", "📍 Location", language), expanded=False):
        mobile_country = st.selectbox(tr("País", "Country", language), ["Estados Unidos", "Venezuela"], key="mobile_country")
        mobile_states = {
            "Estados Unidos": ["Florida", "California", "Texas", "New York", "New Jersey", "Illinois", "Pennsylvania", "Washington", "Georgia", "Arizona", "Otro estado"],
            "Venezuela": ["Distrito Capital", "Miranda", "Zulia", "Carabobo", "Aragua", "Lara", "Anzoátegui", "Bolívar", "Táchira", "Falcón", "Otro estado"],
        }
        mobile_region = st.selectbox(tr("Estado / región", "State / region", language), mobile_states[mobile_country], key="mobile_region")
        mobile_city = st.text_input(tr("Ciudad", "City", language), value="Miami" if mobile_country == "Estados Unidos" else "Caracas", key="mobile_city")

    with st.expander(tr("🎙️ Voz de ALMA", "🎙️ ALMA voice", language), expanded=False):
        mobile_speech_on = st.toggle(tr("Activar voz y micrófono", "Enable voice and microphone", language), value=True, key="mobile_speech_on")
        mobile_voice_choice = st.selectbox(tr("Voz", "Voice", language), ["Marin", "Coral", "Shimmer"], disabled=not mobile_speech_on, key="mobile_voice_choice")
        mobile_speed = st.slider(tr("Velocidad", "Speed", language), .80, 1.60, DEFAULT_SPEED, .05, disabled=not mobile_speech_on, key="mobile_speed")
        mobile_auto_speak = st.toggle(tr("Reproducir automáticamente", "Auto-play answers", language), value=True, disabled=not mobile_speech_on, key="mobile_auto_speak")

    with st.expander(tr("📚 Fuentes", "📚 Sources", language), expanded=False):
        mobile_web_on = st.toggle(tr("Permitir búsqueda web", "Allow web search", language), value=True, key="mobile_web_on")

species = mobile_species
pet_name = mobile_pet_name
breed = mobile_breed
pet_age = mobile_pet_age
pet_sex = mobile_sex_choice
country = mobile_country
region = mobile_region
city = mobile_city
speech_on = mobile_speech_on
voice_choice = mobile_voice_choice
speed = mobile_speed
auto_speak = mobile_auto_speak
web_on = mobile_web_on
vectors = vector_ids_from_env()

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

with st.container(key="alma_main_content"):
    st.markdown(f"""<header class="prw-bar"><div class="prw-brand"><img class="prw-brand-logo" src="{uri('petsrwise_icon.png')}" alt="PetsRWise"><div><span class="prw-brand-name"><span class="prw-wordmark">PetsRWise</span> <b>Alma</b></span><span class="prw-brand-lab">Veterinary AI LAB</span></div></div></header>""",unsafe_allow_html=True)
    if st.session_state.nav == "locator":
        st.markdown(f"""<section class="prw-locator-intro">
        <div class="prw-locator-label">{tr('BUSCADOR VETERINARIO', 'VETERINARY SEARCH', language)}</div>
        <h1>{tr('Encuentra opciones veterinarias en tu ciudad', 'Find veterinary options in your city', language)}</h1>
        <p>{tr('Alma te ayuda a localizar clínicas y hospitales según la especie y el tipo de atención que buscas. Completa el formulario y pulsa Buscar veterinarios.', 'Alma helps you find clinics and hospitals for your animal’s species and care needs. Complete the form and select Find veterinarians.', language)}</p>
        </section>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""<section class="prw-hero"><img class="prw-face" src="{uri('portrait_mockup.png')}" alt="Foto ilustrativa de ALMA">
        <div><div class="prw-hero-title">{tr('Hola, soy','Hello, I’m',language)} <b>ALMA</b></div>
        <div class="prw-hero-sub">{tr('Tu asistente de IA para bienestar animal, información y orientación hacia atención veterinaria.','Your AI assistant for animal wellness information and finding veterinary services.',language)}</div>
        <span class="prw-hero-pill">✦ {tr('Avatar ilustrativo · No es médica veterinaria','Illustrative avatar · Not a veterinarian',language)}</span></div></section>""",unsafe_allow_html=True)
    if st.session_state.nav == "chat":
        if not st.session_state.messages:
            welcome = tr(
                f"Hola, soy ALMA. Estoy aquí para ayudarte con {pet_name} paso a paso.",
                f"Hi, I’m ALMA. I’m here to help you with {pet_name}, step by step.", language)
            st.markdown(f"<p class='prw-hero-sub'>{esc(welcome)}</p>", unsafe_allow_html=True)
            st.markdown(tr(
                "Puedo ayudarte a:\n\n- entender qué podría estar pasando\n- ver si puede ser urgente\n- buscar una clínica\n\n**¿Qué notaste primero?**",
                "I can help you:\n\n- understand what might be happening\n- recognize possible urgency\n- find a clinic\n\n**What did you notice first?**", language))
            actions = [
                ("dog_mockup.png", tr("Tiene síntomas", "Has symptoms", language),
                 tr("Mi mascota tiene síntomas. Ayúdame a ordenarlos, una pregunta a la vez.", "My pet has symptoms. Help me organize them, one question at a time.", language)),
                ("pets_mockup.png", tr("Quiero saber si es urgente", "Could it be urgent?", language), "__emergency_info__"),
                ("hospital_mockup.png", tr("Buscar clínica", "Find a clinic", language), "__locator__"),
                ("cat_mockup.png", tr("Solo necesito orientación", "I just need guidance", language),
                 tr("Solo necesito orientación general para mi mascota. Pregúntame sobre qué tema.", "I just need general guidance for my pet. Ask which topic.", language)),
            ]
            cols = st.columns(2, gap="small")
            suggestion = None
            for idx, (pic, title, question) in enumerate(actions):
                with cols[idx % 2]:
                    st.markdown(f"<img class='prw-card-image' src='{uri(pic)}' alt='{esc(title)}'>",unsafe_allow_html=True)
                    if question == "__locator__":
                        # Streamlit callbacks execute before keyed widgets are instantiated.
                        st.button(title, key=f"action_{idx}", use_container_width=True,
                                  on_click=lambda: st.session_state.update(nav="locator"))
                    elif st.button(title, key=f"action_{idx}", use_container_width=True):
                        if question == "__emergency_info__":
                            st.warning(tr(
                                "Si notas dificultad para respirar, colapso, convulsiones, imposibilidad de orinar, un traumatismo grave o posible ingestión tóxica, busca atención veterinaria de emergencia ahora. No esperes a responder preguntas aquí.",
                                "For breathing difficulty, collapse, seizures, inability to urinate, major trauma or possible toxic ingestion, seek emergency veterinary care now. Do not wait to answer questions here.", language))
                        elif question == "__profile__":
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

        question = suggestion
        if chat_value is not None:
            question_text = chat_value if isinstance(chat_value, str) else getattr(chat_value, "text", None)
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

        follow_chat_response(enabled=bool(question))

        if question:
            st.session_state.messages.append({"role": "user", "content": question})
            with st.chat_message("user", avatar="👤"):
                st.markdown(question)
            with st.chat_message("assistant", avatar=str(ICON)):
                if possible_emergency(question):
                    msg = emergency_message(language)
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
        with st.container(border=True, key="vet_search"):
            st.caption(tr("Completa los datos y pulsa Buscar veterinarios.", "Enter your details and select Find veterinarians.", language))
            search_country = st.selectbox(tr("País", "Country", language),
                                          ["Estados Unidos", "Venezuela"],
                                          index=0 if country == "Estados Unidos" else 1,
                                          format_func=lambda value: "United States" if language == "English" and value == "Estados Unidos" else value,
                                          key="vet_country")
            locations = json.loads((ASSETS / "vet_locations.json").read_text())
            state_options = list(locations[search_country]) + ["__other__"]
            state_key = f"vet_state_{search_country}"
            selected_state = st.selectbox(tr("Estado / región", "State / region", language), state_options,
                index=state_options.index(region) if region in state_options else 0,
                format_func=lambda value: tr("Otro estado / región", "Other state / region", language) if value == "__other__" else value,
                key=state_key)
            search_state = selected_state
            if selected_state == "__other__":
                search_state = st.text_input(tr("Escribe el estado / región", "Enter state / region", language), key=f"vet_custom_state_{search_country}")
            city_options = locations[search_country].get(selected_state, []) + ["__other__"]
            selected_city = st.selectbox(tr("Ciudad *", "City *", language), city_options,
                index=city_options.index(city) if city in city_options else 0,
                format_func=lambda value: tr("Otra ciudad", "Other city", language) if value == "__other__" else value,
                key=f"vet_city_{search_country}_{selected_state}")
            search_city = selected_city
            if selected_city == "__other__":
                search_city = st.text_input(tr("Escribe la ciudad *", "Enter city *", language), key=f"vet_custom_city_{search_country}_{selected_state}")
            st.caption(tr("Listas de ciudades frecuentes. Si no aparece la tuya, elige Otra ciudad.",
                          "Common cities are listed. If yours is missing, select Other city.", language))
            c1, c2 = st.columns(2)
            with c1:
                search_species = st.selectbox(tr("Especie", "Species", language), list(SPECIES_CHOICES),
                                               index=list(SPECIES_CHOICES).index(species),
                                               format_func=lambda value: value if language == "Español" else SPECIES_CHOICES[value],
                                               key="vet_species")
            with c2:
                service = st.selectbox(tr("Tipo de atención", "Care type", language),
                                       [tr("Consulta general", "General care", language),
                                        tr("Especialista", "Specialist", language),
                                        tr("Hospital de emergencias", "Emergency hospital", language)], key="vet_service")
            st.caption(tr("* Ciudad obligatoria. Se buscarán hasta 3 opciones con fuentes públicas.",
                          "* City is required. Search for up to 3 options with public sources.", language))
            submitted = st.button(tr("Buscar veterinarios", "Find veterinarians", language), key="vet_search_submit", type="primary", use_container_width=True)
        if submitted:
            st.session_state.locator_reply = None
            st.session_state.pop("locator_search_details", None)
            if not search_state.strip():
                st.warning(tr("Escribe un estado o región.", "Enter a state or region.", language))
            elif not search_city.strip():
                st.warning(tr("Escribe una ciudad.", "Enter a city.",language))
            elif not os.getenv("OPENAI_API_KEY"):
                st.warning(tr("Primero configura tu API key.", "Configure your API key first.",language))
            else:
                query = (f"INTERNAL FICTIONAL VET LOCATOR TEST. Search web for up to three real veterinary facilities "
                         f"for {search_species} in {search_city}, {search_state}, {search_country}; care type: {service}. "
                         "Only include results with sources. Provide grounded address and URL. Do not invent services, hours, "
                         "availability, phone numbers, partnerships or bookings. Recommend contacting clinics to confirm "
                         f"species suitability. Respond in {'Spanish' if language == 'Español' else 'English'}.")
                try:
                    with st.spinner(tr("Buscando fuentes públicas…", "Searching public sources…",language)):
                        st.session_state.locator_reply = ask(query, True, None)
                        st.session_state.locator_search_details = " · ".join([
                            search_city.strip(), search_state.strip(), search_country,
                            search_species if language == "Español" else SPECIES_CHOICES[search_species], service,
                        ])
                except Exception as ex:
                    st.error(tr("La búsqueda no pudo completarse.", "Search failed.",language))
                    st.caption(type(ex).__name__)
        res = st.session_state.locator_reply
        if not res and not submitted:
            st.info(tr("Aquí aparecerán hasta 3 opciones con sus fuentes. Después de buscar, revisa los datos y contacta directamente a la clínica para confirmar que atiende a tu especie y tiene disponibilidad.",
                       "Up to 3 options and their sources will appear here. After searching, review the details and contact the clinic directly to confirm species coverage and availability.", language))
        if res:
            st.subheader(tr("Resultados de búsqueda", "Search results", language))
            if st.session_state.get("locator_search_details"):
                st.caption(st.session_state.locator_search_details)
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
