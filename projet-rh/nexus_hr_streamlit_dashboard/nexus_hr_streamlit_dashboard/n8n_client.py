import os
import uuid
import requests
import streamlit as st

def get_webhook_url():
    return os.getenv("N8N_WEBHOOK_URL", "").strip()

def send_to_n8n(action, source_type, data, user_id="hr-manager", attempt=1, hr_feedback=""):
    url = get_webhook_url()
    if not url:
        return {
            "ok": False,
            "error": "URL du Webhook non configurée.",
            "details": "Ajoutez N8N_WEBHOOK_URL dans le fichier .env puis redémarrez Streamlit."
        }

    payload = {
        "request_id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "source_type": source_type,
        "data": data,
        "attempt": attempt,
        "hr_feedback": hr_feedback,
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        try:
            result = response.json()
        except ValueError:
            result = response.text
        return {"ok": True, "data": result, "request_id": payload["request_id"]}
    except requests.exceptions.Timeout:
        return {"ok": False, "error": "Le workflow n8n n'a pas répondu dans le délai prévu.", "details": "Vérifiez les exécutions n8n. Le workflow peut être encore en cours."}
    except requests.exceptions.ConnectionError as exc:
        return {"ok": False, "error": "Impossible de joindre n8n.", "details": f"Vérifiez que Docker/n8n fonctionne et que l'URL est correcte. {exc}"}
    except requests.exceptions.HTTPError as exc:
        body = response.text[:2000] if "response" in locals() else str(exc)
        return {"ok": False, "error": f"n8n a retourné HTTP {response.status_code}.", "details": body}
    except requests.exceptions.RequestException as exc:
        return {"ok": False, "error": "Erreur pendant l'appel à n8n.", "details": str(exc)}
