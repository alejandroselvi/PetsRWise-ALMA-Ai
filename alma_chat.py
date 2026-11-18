import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()

VECTOR_STORE_IDS = [
	value.strip()
	for value in os.getenv(
		"ALMA_VECTOR_STORE_IDS", ""
	).split(",")
	if value.strip()
]
MODEL = os.getenv("ALMA_MODEL", "gpt-5.4-mini")

if not VECTOR_STORE_IDS:
	raise ValueError("No vector stores configured")

INSTRUCTIONS = """
You are ALMA, the PetsRWise AI assistant.

This is an INTERNAL DEVELOPMENT TEST.
Only fictional pet scenarios are allowed.

Your role:
- Communicate naturally in Spanish.
- Help organize veterinary intake information.
- Retrieve information from the connected documents.
- Explain general educational information.
- Identify missing information and uncertainty.
- Recommend veterinary evaluation when needed.

Clinical safety:
- Always identify yourself as an AI assistant.
- The uploaded documents are UNAPPROVED drafts.
- Never claim to be a licensed veterinarian.
- Never diagnose or prescribe medication.
- Never calculate medication dosages.
- Never invent clinical references.
- Never assume an emergency is ruled out.
- For potential emergencies, recommend immediate
  veterinary emergency assessment.
- Do not delay emergency referral to collect history.
- If evidence is missing, explain that clearly.

Keep answers concise and easy to understand.


VETERINARY LOCATOR INSTRUCTIONS

When a user asks to find a veterinarian:

1. Ask for city, state, and country if the
   location is not already available.
2. Identify the animal species.
3. Determine whether emergency care is needed.
4. Use web search to find relevant clinics.
5. Provide names, addresses, and source links
   only when supported by search results.
6. Never invent clinics or telephone numbers.
7. Never claim a clinic is open or accepting
   patients without current confirmation.
8. For emergencies, advise immediate veterinary
   attention without delaying the referral.
9. Prioritize verified PetsRWise partners
   when appropriate and identify them clearly.
10. Distinguish search results from clinics
    verified by PetsRWise.


"""

previous_id = None

print("\n================================")
print("ALMA - PetsRWise")
print("Veterinary AI - Internal Testing")
print("================================")
print("Escribe 'salir' para terminar.\n")

while True:
	question = input("TÚ: ").strip()

	if question.lower() in ("salir", "exit", "quit"):
		print("ALMA: ¡Hasta pronto!")
		break

	if not question:
		continue

	try:
		request = {
			"model": MODEL,
			"instructions": INSTRUCTIONS,
			"input": question,
            "tools": [
                {
                    "type": "file_search",
                    "vector_store_ids": VECTOR_STORE_IDS,
                     "max_num_results": 5
                },
                {
                    "type": "web_search"
                }
],

		
		}

		if previous_id:
			request["previous_response_id"] = previous_id

		response = client.responses.create(**request)
		previous_id = response.id

		print("\nALMA:")
		print(response.output_text)

		print("\nDOCUMENTOS CONSULTADOS:")

		files = set()

		for item in response.output:
			if item.type == "file_search_call":
				for result in (item.results or []):
					if result.filename:
						files.add(result.filename)

		if files:
			for filename in sorted(files):
				print("-", filename)
		else:
			print("No se recuperaron documentos en este turno.")

		print()

	except Exception as error:
		print("\nERROR:", error)
		print("Revisa la configuración e inténtalo de nuevo.\n")