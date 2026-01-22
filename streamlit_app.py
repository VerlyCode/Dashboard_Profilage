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
# 🔐 MOT DE PASSE SIMPLE
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
# 📂 CHARGEMENT DES DONNÉES (UNE FOIS)
# ===============================
if "df" not in st.session_state:
    st.sidebar.info("📂 Charger les données (1 seule fois)")

    uploaded_file = st.sidebar.file_uploader(
        "Fichier DigiPay (Excel)",
        type=["xlsx"]
    )

    if uploaded_file is None:
        st.warning("⛔ Données non disponibles")
        st.stop()

    df = pd.read_excel(uploaded_file)
    df['TxnDate'] = pd.to_datetime(df['TxnDate'])
    st.session_state.df = df
else:
    df = st.session_state.df

# ===============================
# FILTRE ANNÉE 2025
# ===============================
df = df[df['TxnDate'].dt.year == 2025].copy()

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
    return df[df['TxnDate'] >= df['TxnDate'].max() - pd.Timedelta(days=j)]['Sender Name'].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Clients", df['Sender Name'].nunique())
c2.metric("🔥 Actifs 30j", actifs(30))
c3.metric("📆 Actifs 60j", actifs(60))
c4.metric("📅 Actifs 90j", actifs(90))

st.divider()

# ===============================
# SEGMENTATION CLIENT
# ===============================
tx = (
    df.groupby(['Sender Name', 'Agence'])
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

fig = px.bar(
    tx.groupby('Segment').size().reset_index(name='Clients'),
    x='Segment',
    y='Clients',
    text='Clients',
    color='Segment',
    title="📊 Segmentation des clients – 2025",
    template="plotly_dark"
)

fig.update_layout(title_x=0.5)
st.plotly_chart(fig, use_container_width=True)

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
df['YearMonth'] = df['TxnDate'].dt.to_period('M')

clients_12_mois = (
    df.groupby(['Sender Name', 'Agence'])['YearMonth']
    .nunique()
    .reset_index(name='Mois_Actifs')
)

clients_12_mois = clients_12_mois[clients_12_mois['Mois_Actifs'] == 12]

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
