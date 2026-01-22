import streamlit as st
import pandas as pd
import plotly.express as px

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
    df['TxnDate'] = pd.to_datetime(df['TxnDate'])
    return df

df = load_data()

# ===============================
# FILTRE ANNÉE 2025
# ===============================
df = df[df['TxnDate'].dt.year == 2025].copy()

# ===============================
# SIDEBAR – FILTRES
# ===============================
st.sidebar.markdown("## 🔎 Filtres")

agences = sorted(df['Agence'].dropna().unique())
agence_sel = st.sidebar.multiselect(
    "Agence",
    agences,
    default=agences
)

df_filtree = df[df['Agence'].isin(agence_sel)]

# ===============================
# HEADER
# ===============================
col1, col2 = st.columns([1, 6])

with col1:
    st.image("Logo.png", width=85)

with col2:
    st.markdown("""
        <h1 style='margin-bottom:0;'>Clients Profilage Dashboard</h1>
        <h4 style='color:#9CA3AF;margin-top:0;'>
        DigiPay – Analyse & Segmentation Clients 2025
        </h4>
    """, unsafe_allow_html=True)

st.divider()

# ===============================
# KPI
# ===============================
def actifs(j):
    return df_filtree[
        df_filtree['TxnDate'] >= df_filtree['TxnDate'].max() - pd.Timedelta(days=j)
    ]['Sender Name'].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Clients", df_filtree['Sender Name'].nunique())
c2.metric("🔥 Actifs 30j", actifs(30))
c3.metric("📆 Actifs 60j", actifs(60))
c4.metric("📅 Actifs 90j", actifs(90))

st.divider()

# ===============================
# SEGMENTATION CLIENT
# ===============================
tx = (
    df_filtree
    .groupby(['Sender Name', 'Agence'])
    .size()
    .reset_index(name='Nombre_Envois')
)

def segment(n):
    if n == 1:
        return "1 transaction"
    elif n <= 3:
        return "Rare"
    elif n <= 11:
        return "Occasionnel"
    else:
        return "Régulier"

tx['Segment'] = tx['Nombre_Envois'].apply(segment)

seg_fig = px.bar(
    tx.groupby('Segment').size().reset_index(name='Clients'),
    x='Segment',
    y='Clients',
    text='Clients',
    color='Segment',
    title="📊 Segmentation des clients – 2025",
    template="plotly_dark"
)

seg_fig.update_layout(title_x=0.5)
st.plotly_chart(seg_fig, use_container_width=True)

# ===============================
# TOP CLIENTS
# ===============================
st.subheader("🏆 Top clients par volume")
st.dataframe(
    tx.sort_values('Nombre_Envois', ascending=False).head(20),
    use_container_width=True
)

# ===============================
# CLIENTS RÉGULIERS (12 MOIS)
# ===============================
df_filtree['YearMonth'] = df_filtree['TxnDate'].dt.to_period('M')

clients_12_mois = (
    df_filtree
    .groupby(['Sender Name', 'Agence'])['YearMonth']
    .nunique()
    .reset_index(name='Mois_Actifs')
)

clients_12_mois = clients_12_mois[
    clients_12_mois['Mois_Actifs'] == 12
]

st.subheader("🔁 Clients réguliers (12 mois actifs)")
st.dataframe(clients_12_mois, use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.markdown("""
<hr style='margin-top:40px;'>
<p style='text-align:center;color:#6B7280;'>
© 2025 DigiPay – Direction Commerciale
</p>
<p style='text-align:center;color:#6B7280;'>
Verly BOUMBOU KIMBATSA – Responsable Opérations Commerciales
</p>
""", unsafe_allow_html=True)
