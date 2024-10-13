from flask import Flask, request, jsonify
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import re

app = Flask(__name__)

# Ollama API endpoint
OLLAMA_API_URL = "https://c749-35-240-242-84.ngrok-free.app"  # Update this if your Ollama instance is running elsewhere

# Initialize Ollama model
model = OllamaLLM(model="mistral:7b-instruct-v0.2-q4_0", base_url=OLLAMA_API_URL, temperature=0)

# Define the template
template = """Extrayez l'événement principal et listez les détails suivants et reponder en francais :
- Qui :
- Quand (jj-mm-aaaa) : (sous format sou format jj-mm-aaaa et indiquez la date de l'événement principale, pas celle de la source. s'il existe pas d'une date de l'événement indiquez la date de la source  )
- Où : (affichez uniquement la ville si elle est précisée, sinon le pays uniquement )

Texte : {text}

Exemple :
Texte : Les autorités turques ont arrêté 33 personnes soupçonnées de s'être livrées à des activités d'espionnage pour le compte du Mossad, le service de renseignement extérieur israélien, selon des sources sécuritaires. Ces arrestations font suite à une enquête menée par le Bureau d'enquête sur le terrorisme et les crimes organisés du Bureau du procureur d'Istanbul, axée sur l'espionnage international. Les suspects auraient été impliqués dans des activités telles que le renseignement, la surveillance, l'agression et l'enlèvement pour le compte du Mossad. Une opération antiterroriste, organisée conjointement par l'Organisation nationale du renseignement (MIT) et la police d'Istanbul, a permis d'appréhender les suspects. Des « descentes » simultanées à 57 adresses dans huit provinces ont permis de capturer les suspects, tandis que des opérations de recherche de 13 autres suspects sont en cours. Se faisant passer pour des employés d'une société de conseil basée à Istanbul, les suspects ont fourni au Mossad des informations sur les Palestiniens en Turquie en échange d'argent. Israël n'a pas réagi à ces allégations. (La voix de la Turquie, le 02-01-2024)

Sortie :
- Qui : Les autorités turques
- Quand (jj-mm-aaaa) : 02-01-2024
- Où : Istanbul

Texte : Deux attentats terroristes à Kerman, dans le sud-est du pays, ont fait mercredi 3 janvier 73 morts et 170 blessés, selon l'Organisation des urgences iranienne. Les explosions se sont produites près de la sépulture du général martyr iranien, Qassem Soleimani, où les gens s'étaient rassemblés pour participer à la cérémonie du quatrième anniversaire de sa mort en martyr. (Press TV, le 03-01-2024)

Sortie :
- Qui : Deux attentats terroristes
- Quand (jj-mm-aaaa) : 03-01-2024
- Où : Kerman

Texte : Taïwan a détecté quatre ballons chinois avant la présidentielle. C'est ce qu'a indiqué le ministère taïwanais de la Défense. Les ballons chinois ont été repérés au-dessus de la ligne médiane du détroit de Taïwan qui sépare l'île de la Chine continentale. Les observations de ballons chinois à Taïwan ont débuté le mois dernier et interviennent à moins de deux semaines de la présidentielle très cruciale dans l'île, le 13 janvier. Le ministère taïwanais de la Défense a signalé avoir observé des ballons à six reprises en décembre. (Deutsche Welle, le 03-01-2024)

Sortie :
- Qui : Le ministère taïwanais de la Défense
- Quand (jj-mm-aaaa) : 12-01-2024
- Où : Taïwan


Texte : {text}


Sortie :
- Qui :
- Quand (jj-mm-aaaa) :
- Où :
"""

prompt = ChatPromptTemplate.from_template(template)

print(prompt)

# Create the chain
chain = prompt | model

def parse_ollama_response(response):
    print(response)
    # Extract who, when, and where using regex
    who_match = re.search(r'- Who: (.+)', response)
    when_match = re.search(r'- When \(mm-dd-yyyy\): (.+)', response)
    where_match = re.search(r'- Where: (.+)', response)

    # Extract the values or use None if not found
    who = who_match.group(1).strip() if who_match else None
    when = when_match.group(1).strip() if when_match else None
    where = where_match.group(1).strip() if where_match else None

    return {
        "who": who,
        "when": when,
        "where": where
    }

@app.route('/analyze', methods=['POST'])
def analyze_text():
    data = request.json
    text = data.get('text')

    if not text:
        return jsonify({"error": "No text provided"}), 400

    try:
        # Call the chain with the provided text
        result = chain.invoke({"text": text})

        # Parse the Ollama response
        parsed_result = parse_ollama_response(result)

        return jsonify(parsed_result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
