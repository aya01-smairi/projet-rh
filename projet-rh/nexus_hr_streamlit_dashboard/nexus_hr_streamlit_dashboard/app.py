import streamlit as st
import pandas as pd
from datetime import datetime
from n8n_client import send_to_n8n, get_webhook_url

st.set_page_config(
    page_title="Nexus HR | Command Center",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Styling ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { --bg:#0b1020; --panel:#121a2d; --panel2:#17223a; --line:#26334f; --muted:#91a0bb; --text:#edf2ff; --purple:#8b5cf6; --blue:#4f8cff; --cyan:#48c6d9; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(circle at 85% 0%, #1c1c45 0, transparent 30%), var(--bg); color:var(--text); }
.block-container { padding-top:1.6rem; padding-bottom:2.5rem; max-width:1450px; }
[data-testid="stSidebar"] { background:#0e1628; border-right:1px solid var(--line); }
[data-testid="stSidebar"] * { color:var(--text); }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.04em; }
h1 { font-size:2.25rem !important; font-weight:800 !important; }
h2 { font-size:1.45rem !important; font-weight:700 !important; }
p, label, .stCaption { color:var(--muted); }
.hero { padding:25px 28px; border:1px solid #2d3a5a; border-radius:20px; background:linear-gradient(115deg,rgba(105,75,210,.22),rgba(45,105,190,.12)),#121a2d; margin-bottom:22px; }
.eyebrow { color:#a99aff; text-transform:uppercase; letter-spacing:.16em; font-size:.72rem; font-weight:700; }
.hero-title { font-family:Manrope,sans-serif; font-size:2rem; font-weight:800; color:#f4f6ff; margin:.3rem 0; }
.hero-sub { color:#a8b5ce; font-size:.95rem; }
.metric { background:linear-gradient(145deg,#17233b,#111a2c); border:1px solid #2a3856; padding:17px 19px; border-radius:16px; min-height:112px; }
.metric-label { color:#9eacc6; font-size:.78rem; font-weight:600; }
.metric-value { color:#f2f5ff; font-family:Manrope,sans-serif; font-size:1.8rem; font-weight:800; margin-top:8px; }
.metric-note { color:#8c9bb8; font-size:.75rem; margin-top:3px; }
.panel { background:#121a2d; border:1px solid #263550; border-radius:16px; padding:18px 20px; }
.pill { display:inline-block; padding:5px 10px; border-radius:99px; background:#24214a; color:#c6b8ff; font-size:.75rem; font-weight:700; }
.small-muted { color:#8e9db8; font-size:.82rem; }
div.stButton > button, div.stFormSubmitButton > button { border-radius:10px; border:1px solid #6751bd; background:linear-gradient(100deg,#7656dd,#416fd4); color:white; font-weight:700; min-height:2.7rem; }
div.stButton > button:hover, div.stFormSubmitButton > button:hover { border-color:#a99aff; color:white; }
.stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] { background:#101a2d !important; color:#edf2ff !important; border-color:#30405f !important; border-radius:10px !important; }
[data-testid="stMetric"] { background:#121a2d; padding:15px; border:1px solid #263550; border-radius:14px; }
hr { border-color:#273550; }
</style>
""", unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None

def metric_card(label, value, note):
    st.markdown(f"""<div class="metric"><div class="metric-label">{label}</div>
    <div class="metric-value">{value}</div><div class="metric-note">{note}</div></div>""", unsafe_allow_html=True)

def show_result(result):
    st.session_state.last_result = result
    if result.get("ok"):
        st.success("Réponse reçue de n8n.")
        payload = result.get("data")
        if isinstance(payload, (dict, list)):
            st.json(payload)
        else:
            st.write(payload)
    else:
        st.error(result.get("error", "Une erreur inconnue est survenue."))
        if result.get("details"):
            with st.expander("Détails techniques"):
                st.code(str(result["details"]))

def submit_request(action, source_type, data, user_id="hr-manager"):
    result = send_to_n8n(
        action=action,
        source_type=source_type,
        data=data,
        user_id=user_id,
        attempt=1,
        hr_feedback="",
    )
    st.session_state.history.insert(0, {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "action": action,
        "source": source_type,
        "status": "Success" if result.get("ok") else "Failed",
        "request_id": result.get("request_id", ""),
    })
    show_result(result)

# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("## ✦ NEXUS HR")
    st.markdown("<span class='small-muted'>PEOPLE INTELLIGENCE PLATFORM</span>", unsafe_allow_html=True)
    st.divider()
    page = st.radio(
        "NAVIGATION",
        ["Overview", "AI HR Assistant", "CV Analysis", "Email Analysis", "HR Analytics", "Activity History"],
        label_visibility="visible",
    )
    st.divider()
    st.markdown("**WORKSPACE STATUS**")
    webhook = get_webhook_url()
    st.markdown(f"<span class='pill'>● {'Webhook configuré' if webhook else 'Webhook à configurer'}</span>", unsafe_allow_html=True)
    st.caption("n8n local · Supabase · Groq")
    st.caption("Le dashboard conserve l'historique dans la session en cours.")

# ---------- Header ----------
st.markdown(f"""
<div class="hero">
  <div class="eyebrow">HR MANAGEMENT / COMMAND CENTER</div>
  <div class="hero-title">{page}</div>
  <div class="hero-sub">Pilotage intelligent des opérations RH · {datetime.now().strftime('%d %B %Y')}</div>
</div>
""", unsafe_allow_html=True)

if page == "Overview":
    total = len(st.session_state.history)
    success = sum(x["status"] == "Success" for x in st.session_state.history)
    failed = total - success
    c1,c2,c3,c4 = st.columns(4)
    with c1: metric_card("REQUESTS THIS SESSION", total, "Demandes envoyées depuis ce dashboard")
    with c2: metric_card("SUCCESSFUL", success, "Réponses reçues de n8n")
    with c3: metric_card("FAILED", failed, "Requêtes en erreur")
    with c4: metric_card("INTEGRATION", "n8n", "Webhook local")
    st.write("")
    left,right = st.columns([1.35,1])
    with left:
        st.markdown("### Recent activity")
        if st.session_state.history:
            st.dataframe(pd.DataFrame(st.session_state.history).head(8), use_container_width=True, hide_index=True)
        else:
            st.markdown("<div class='panel'><b>Aucune activité pour le moment</b><p class='small-muted'>Envoyez votre première demande via AI HR Assistant, CV Analysis ou Email Analysis.</p></div>", unsafe_allow_html=True)
    with right:
        st.markdown("### Quick actions")
        st.markdown("<div class='panel'><p>Accédez rapidement aux outils de votre espace RH.</p></div>", unsafe_allow_html=True)
        if st.button("✦  Ask the AI HR Assistant", use_container_width=True):
            st.session_state.quick_page = "AI HR Assistant"
            st.rerun()
        if st.button("＋  Analyze a CV", use_container_width=True):
            st.session_state.quick_page = "CV Analysis"
            st.rerun()
        if st.button("✉  Analyze an email", use_container_width=True):
            st.session_state.quick_page = "Email Analysis"
            st.rerun()
    st.info("Les indicateurs de candidatures et d'emails réels seront ajoutés lorsque WF-01 renverra ces données ou qu'une lecture Supabase dédiée sera configurée.")

elif page == "AI HR Assistant":
    st.markdown("### Ask your HR copilot")
    st.markdown("<p class='small-muted'>Posez une question en langage naturel. La demande est envoyée à votre workflow n8n, qui orchestre Supabase et Groq.</p>", unsafe_allow_html=True)
    with st.form("assistant_form"):
        question = st.text_area("Votre question RH", placeholder="Ex. : Résume les candidatures reçues pour le poste de développeur...", height=130)
        context = st.text_input("Contexte supplémentaire (facultatif)", placeholder="Département, poste, période…")
        submitted = st.form_submit_button("Envoyer la question  →", use_container_width=True)
    if submitted:
        if not question.strip():
            st.warning("Veuillez saisir une question.")
        else:
            submit_request("hr_assistant", "dashboard_chat", {"question": question.strip(), "context": context.strip()})
    if st.session_state.last_result:
        st.markdown("### Latest response")
        show_result(st.session_state.last_result)

elif page == "CV Analysis":
    st.markdown("### Candidate application review")
    st.markdown("<p class='small-muted'>Transmettez les informations d'une candidature au workflow d'analyse.</p>", unsafe_allow_html=True)
    with st.form("cv_form"):
        candidate = st.text_input("Nom du candidat")
        position = st.text_input("Poste ciblé")
        email = st.text_input("Email du candidat")
        cv_text = st.text_area("Texte du CV / contenu de la candidature", height=190, placeholder="Collez ici le texte extrait du CV…")
        submitted = st.form_submit_button("Analyser la candidature  →", use_container_width=True)
    if submitted:
        if not cv_text.strip():
            st.warning("Ajoutez le texte du CV ou de la candidature.")
        else:
            submit_request("analyze_application", "cv", {
                "candidate_name": candidate.strip(),
                "position": position.strip(),
                "email": email.strip(),
                "cv_text": cv_text.strip(),
            })

elif page == "Email Analysis":
    st.markdown("### Email intelligence")
    st.markdown("<p class='small-muted'>Analysez un email RH : classification, résumé et éléments nécessitant une action.</p>", unsafe_allow_html=True)
    with st.form("email_form"):
        subject = st.text_input("Objet de l'email")
        sender = st.text_input("Expéditeur")
        email_body = st.text_area("Contenu de l'email", height=200)
        submitted = st.form_submit_button("Analyser l'email  →", use_container_width=True)
    if submitted:
        if not email_body.strip():
            st.warning("Collez le contenu de l'email.")
        else:
            submit_request("analyze_email", "email", {
                "subject": subject.strip(),
                "sender": sender.strip(),
                "email_body": email_body.strip(),
            })

elif page == "HR Analytics":
    st.markdown("### Operational analytics")
    st.markdown("<p class='small-muted'>Indicateurs calculés à partir des requêtes réalisées depuis cette session.</p>", unsafe_allow_html=True)
    hist = st.session_state.history
    if not hist:
        st.info("Aucune donnée analytique disponible. Envoyez d'abord des demandes depuis le dashboard.")
    else:
        df = pd.DataFrame(hist)
        a,b = st.columns(2)
        with a:
            st.markdown("#### Requests by action")
            st.bar_chart(df["action"].value_counts())
        with b:
            st.markdown("#### Execution status")
            st.bar_chart(df["status"].value_counts())
        st.dataframe(df, use_container_width=True, hide_index=True)

elif page == "Activity History":
    st.markdown("### Request log")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download history (CSV)", csv, "hr_activity_history.csv", "text/csv")
        if st.button("Clear session history"):
            st.session_state.history = []
            st.rerun()
    else:
        st.info("Aucune demande n'a encore été envoyée.")
