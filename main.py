from flask import Flask, request
import requests
import os

app = Flask(__name__)

BRAZE_API_KEY = os.environ.get("BRAZE_API_KEY")
BRAZE_URL = os.environ.get("BRAZE_URL")

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    
    try:
        criteria = data["analysis"]["evaluation_criteria_results"]
        called_number = data["conversation_initiation_client_data"]["dynamic_variables"]["system__called_number"]
        
        perfil = criteria.get("perfil_riesgo", {}).get("rationale", "")
        acepto = criteria.get("acepto_llamada", {}).get("result", "")
        completada = criteria.get("llamada_completada", {}).get("result", "")

        payload = {
            "attributes": [{
                "phone": f"+{called_number}",
                "perfil_riesgo_gbm": perfil,
                "gbm_acepto_llamada": acepto,
                "gbm_llamada_completada": completada
            }]
        }

        headers = {
            "Authorization": f"Bearer {BRAZE_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(BRAZE_URL, json=payload, headers=headers)
        return {"status": "ok", "braze": response.status_code}, 200

    except Exception as e:
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
