import streamlit as st
import pandas as pd

# ===============================
# CONFIG PAGE
# ===============================
st.set_page_config(
    page_title="DigiPay | Profilage Clients 2025",
    page_icon="📊",
    layout="wide"
)

# ===============================
# 🔐 MOT DE PASSE
# ===============================
PASSWORD = "DIGIPAY2025"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("🔐 Mot de passe", type="password")
    if pwd == PASSWORD:
        st.session_state.auth = True
        st.rerun()
    elif pwd:
        st.error("Mot de passe incorrect")
    st.stop()

# ===============================
# 📊 DONNÉES – GOOGLE SHEETS
# ===============================
SHEET_ID = "1K25ZIJ2Dq947rp2IXOdfPQFUlvTA7JK7"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

@st.cache_data
def load_data():
    df = pd.read_csv(CSV_URL)
    df["TxnDate"] = pd.to_datetime(df["TxnDate"])
    return df

df = load_data()

# ===============================
# FILTRE ANNÉE 2025
# ===============================
df = df[df["TxnDate"].dt.year == 2025].copy()

# ===============================
#  EXCLUSION EMPLOYÉS DIGIPAY
# ===============================
clients_internes = [
    "KIHOULOU Mesmin omer",
    "NGASSAKI-ZONI Gachlem zepharos"
]
df = df[~df["Sender Name"].isin(clients_internes)]

# ===============================
# SIDEBAR – FILTRES
# ===============================
st.sidebar.header("🔎 Filtres")
agences = sorted(df["Agence"].dropna().unique())
agence_sel = st.sidebar.multiselect("Agence", agences, default=agences)
df = df[df["Agence"].isin(agence_sel)]

# ===============================
# HEADER AVEC LOGO
# ===============================
col1, col2 = st.columns([1, 6])

with col1:
    st.image("Logo.png", width=90)

with col2:
    st.markdown("""
        <h1 style='margin-bottom:0;'>📊 Profilage Clients – 2025</h1>
        <h4 style='color:#9CA3AF;margin-top:0;'>
        DigiPay – Analyse & Segmentation Clients
        </h4>
    """, unsafe_allow_html=True)

st.divider()

# ===============================
# STYLE KPI (SEXY)
# ===============================
st.markdown("""
<style>
.kpi-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 26px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0 8px 20px rgba(0,0,0,0.35);
}
.kpi-title {
    color: #9CA3AF;
    font-size: 14px;
    letter-spacing: 1px;
}
.kpi-value {
    font-size: 40px;
    font-weight: 700;
    color: #F9FAFB;
}
</style>
""", unsafe_allow_html=True)

# ===============================
# KPI
# ===============================
date_max = df["TxnDate"].max()

def clients_actifs(jours):
    return df[df["TxnDate"] >= date_max - pd.Timedelta(days=jours)]["Sender Name"].nunique()

k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">👥 CLIENTS</div>
    <div class="kpi-value">{df["Sender Name"].nunique()}</div>
</div>
""", unsafe_allow_html=True)

k2.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">🔥 ACTIFS 30 JOURS</div>
    <div class="kpi-value">{clients_actifs(30)}</div>
</div>
""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">📆 ACTIFS 60 JOURS</div>
    <div class="kpi-value">{clients_actifs(60)}</div>
</div>
""", unsafe_allow_html=True)

k4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">📅 ACTIFS 90 JOURS</div>
    <div class="kpi-value">{clients_actifs(90)}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===============================
# FONCTION TABLE CLIENTS
# ===============================
def table_clients(df, date_min=None):
    if date_min is not None:
        df = df[df["TxnDate"] >= date_min]

    return (
        df.groupby(["Sender Name", "Agence"])
        .agg(Nombre_Envois=("TxnDate", "count"))
        .reset_index()
        .sort_values("Nombre_Envois", ascending=False)
    )

# ===============================
# LISTES CLIENTS
# ===============================
st.subheader("🟢 Clients actifs – 30 jours")
st.dataframe(table_clients(df, date_max - pd.Timedelta(days=30)), use_container_width=True)

st.subheader("🟡 Clients actifs – 60 jours")
st.dataframe(table_clients(df, date_max - pd.Timedelta(days=60)), use_container_width=True)

st.subheader("🔵 Clients actifs – 90 jours")
st.dataframe(table_clients(df, date_max - pd.Timedelta(days=90)), use_container_width=True)

st.subheader("🏆 Top clients – Année 2025")
st.dataframe(table_clients(df).head(50), use_container_width=True)

# ===============================
# CLIENTS ACTIFS CHAQUE MOIS
# ===============================
df["YearMonth"] = df["TxnDate"].dt.to_period("M")

clients_12_mois = (
    df.groupby(["Sender Name", "Agence"])["YearMonth"]
    .nunique()
    .reset_index(name="Mois_Actifs")
)

clients_12_mois = clients_12_mois[clients_12_mois["Mois_Actifs"] == 12]
clients_12_mois = clients_12_mois.merge(
    table_clients(df),
    on=["Sender Name", "Agence"],
    how="left"
)

st.subheader("📆 Clients actifs chaque mois (12 mois)")
st.dataframe(clients_12_mois, use_container_width=True)

# ===============================
# CLIENTS 1 TRANSACTION
# ===============================
st.subheader("⚠️ Clients avec une seule transaction")
one_tx = table_clients(df)
one_tx = one_tx[one_tx["Nombre_Envois"] == 1]
st.dataframe(one_tx, use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.markdown("""
<hr>
<p style='text-align:center;color:#6B7280;'>
© 2025 DigiPay – Direction Commerciale<br>
Verly BOUMBOU KIMBATSA - Responsable des Opérations Commerciales
</p>
""", unsafe_allow_html=True)
