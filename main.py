from flask import Flask, request
import requests
import os

app = Flask(__name__)

BRAZE_API_KEY = os.environ.get("BRAZE_API_KEY")
BRAZE_URL = os.environ.get("BRAZE_URL")

def extraer_perfil(texto):
    texto = str(texto).upper()
    if "CONSERVADOR" in texto:
        return "CONSERVADOR"
    elif "MODERADO" in texto:
        return "MODERADO"
    elif "AGRESIVO" in texto:
        return "AGRESIVO"
    return "DESCONOCIDO"

def extraer_booleano(texto):
    texto = str(texto).lower()
    if "true" in texto or "success" in texto or "sí" in texto or "si" in texto or "aceptó" in texto or "acepto" in texto:
        return True
    return False

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    try:
        criteria = data["analysis"]["evaluation_criteria_results"]
        dynamic_vars = data["conversation_initiation_client_data"]["dynamic_variables"]

        called_number = dynamic_vars.get("system__called_number", "")
        external_id = dynamic_vars.get("external_id", None)

        perfil_raw = criteria.get("perfil_riesgo", {}).get("rationale", "")
        acepto_raw = criteria.get("acepto_llamada", {}).get("result", "")
        completada_raw = criteria.get("llamada_completada", {}).get("result", "")

        perfil = extraer_perfil(perfil_raw)
        acepto = extraer_booleano(acepto_raw)
        completada = extraer_booleano(completada_raw)

        attribute = {
            "phone": f"+{called_number}",
            "perfil_riesgo_gbm": perfil,
            "gbm_acepto_llamada": acepto,
            "gbm_llamada_completada": completada
        }

        if external_id and external_id != "unknown":
            attribute["external_id"] = external_id

        payload = {"attributes": [attribute]}

        headers = {
            "Authorization": f"Bearer {BRAZE_API_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.post(BRAZE_URL, json=payload, headers=headers)
        return {"status": "ok", "braze": response.status_code, "attribute_sent": attribute}, 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
