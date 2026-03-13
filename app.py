from flask import Flask, request, jsonify
from groq import Groq
import os

app = Flask(__name__)
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
conversations = {}

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    player_id = data.get("player_id")
    user_message = data.get("message")
    npc_name = data.get("npc_name", "NPC")
    personality = data.get("personality", "Ты дружелюбный житель деревни.")

    if player_id not in conversations:
        conversations[player_id] = [{"role": "system", "content": f"Ты NPC по имени {npc_name}. {personality} Отвечай коротко — 1-2 предложения. Говори на русском."}]

    conversations[player_id].append({"role": "user", "content": user_message})

    if len(conversations[player_id]) > 20:
        conversations[player_id] = [conversations[player_id][0]] + conversations[player_id][-19:]

    response = client.chat.completions.create(
        model="llama3-8b-8192",
        messages=conversations[player_id],
        max_tokens=150
    )

    reply = response.choices[0].message.content
    conversations[player_id].append({"role": "assistant", "content": reply})
    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
