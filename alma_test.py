import os
from dotenv import load_dotenv
from openai import OpenAI

# Read private configuration
load_dotenv()

vector_store_id = os.getenv("ALMA_VECTOR_STORE_ID")
model = os.getenv("ALMA_MODEL", "gpt-5.4-mini")

if not vector_store_id:
    raise ValueError("Missing ALMA_VECTOR_STORE_ID")

client = OpenAI()

# Ask ALMA about a fictional veterinary case
response = client.responses.create(
    model=model,
    instructions="""
    You are ALMA, the AI assistant of PetsRWise.
    This is an internal development test only.

    Answer in Spanish.
    Use the uploaded veterinary documents.
    The documents are unapproved drafts.
    Do not diagnose or prescribe medication.
    Identify missing information.
    Do not invent medical facts.
    Explain when veterinary review is needed.
    """,
    input=(
        "Según el protocolo de intake de "
        "PetsRWise, ¿qué información debe "
        "recopilar ALMA sobre un perro?"
    ),
    tools=[
        {
            "type": "file_search",
            "vector_store_ids": [vector_store_id]
        }
    ],
    include=["file_search_call.results"]
)

print("\n--- RESPUESTA DE ALMA ---\n")
print(response.output_text)

print("\n--- DOCUMENTOS CONSULTADOS ---\n")

found = False

for item in response.output:
    if item.type == "file_search_call":
        for result in (item.results or []):
            print(result.filename)
            found = True

if not found:
    print("No se encontraron resultados de archivos.")