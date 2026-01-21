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
# HEADER AVEC LOGO
# ===============================
col_logo, col_title = st.columns([1, 5])

with col_logo:
    st.image("Logo.png", width=120)

with col_title:
    st.markdown(
        """
        <h1 style='margin-bottom:0;'>Clients Profilage Dashboard</h1>
        <h4 style='color:#9CA3AF;margin-top:0;'>DigiPay – Analyse & Segmentation Clients 2025</h4>
        """,
        unsafe_allow_html=True
    )

st.divider()

# ===============================
# CHARGEMENT DONNÉES
# ===============================
@st.cache_data
def load_data():
    df = pd.read_excel("bss_cleannn.xlsx")
    df['TxnDate'] = pd.to_datetime(df['TxnDate'])
    return df

df = load_data()

# ===============================
# FILTRE ANNÉE 2025
# ===============================
df = df[df['TxnDate'].dt.year == 2025].copy()

# ===============================
# KPI CALCULS
# ===============================
nb_clients = df['Sender Name'].nunique()

def count_clients_actifs(jours):
    date_limite = df['TxnDate'].max() - pd.Timedelta(days=jours)
    return df[df['TxnDate'] >= date_limite]['Sender Name'].nunique()

actifs_30j = count_clients_actifs(30)
actifs_60j = count_clients_actifs(60)
actifs_90j = count_clients_actifs(90)

# ===============================
# SIDEBAR FILTRES
# ===============================
st.sidebar.markdown("## 🔎 Filtres")
agences = sorted(df['Agence'].dropna().unique())
agence_sel = st.sidebar.multiselect("Agence", agences, default=agences)

df = df[df['Agence'].isin(agence_sel)]

# ===============================
# KPI CARDS (CUSTOM STYLE)
# ===============================
st.markdown("""
<style>
.kpi-box {
    background: #161B22;
    padding: 25px;
    border-radius: 18px;
    text-align: center;
}
.kpi-title {
    color: #9CA3AF;
    font-size: 16px;
}
.kpi-value {
    font-size: 38px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

k1, k2, k3, k4 = st.columns(4)

k1.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">👥 Clients</div>
    <div class="kpi-value">{nb_clients}</div>
</div>
""", unsafe_allow_html=True)

k2.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">🔥 Actifs 30 jours</div>
    <div class="kpi-value">{actifs_30j}</div>
</div>
""", unsafe_allow_html=True)

k3.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">📆 Actifs 60 jours</div>
    <div class="kpi-value">{actifs_60j}</div>
</div>
""", unsafe_allow_html=True)

k4.markdown(f"""
<div class="kpi-box">
    <div class="kpi-title">📅 Actifs 90 jours</div>
    <div class="kpi-value">{actifs_90j}</div>
</div>
""", unsafe_allow_html=True)

st.divider()

# ===============================
# SEGMENTATION CLIENT
# ===============================
tx_par_client = (
    df.groupby(['Sender Name', 'Agence'])
    .size()
    .reset_index(name='Nombre_Envois')
)

def segment(n):
    if n == 1:
        return "1 transaction"
    elif 2 <= n <= 3:
        return "Rare"
    elif 4 <= n <= 11:
        return "Occasionnel"
    else:
        return "Régulier"

tx_par_client['Segment'] = tx_par_client['Nombre_Envois'].apply(segment)

seg_fig = px.bar(
    tx_par_client.groupby('Segment').size().reset_index(name='Clients'),
    x='Segment',
    y='Clients',
    text='Clients',
    color='Segment',
    title="📊 Segmentation des clients – 2025",
)

seg_fig.update_layout(
    template="plotly_dark",
    title_x=0.5
)

st.plotly_chart(seg_fig, use_container_width=True)

# ===============================
# TOP CLIENTS
# ===============================
st.subheader("🏆 Top clients par volume")

st.dataframe(
    tx_par_client.sort_values('Nombre_Envois', ascending=False).head(20),
    use_container_width=True
)

# ===============================
# CLIENTS RÉGULIERS (12 MOIS)
# ===============================
df['YearMonth'] = df['TxnDate'].dt.to_period('M')

clients_toute_annee = (
    df.groupby(['Sender Name', 'Agence'])['YearMonth']
    .nunique()
    .reset_index(name='Mois_Actifs')
)

clients_toute_annee = clients_toute_annee[clients_toute_annee['Mois_Actifs'] == 12]

st.subheader("🔁 Clients réguliers (12 mois actifs)")
st.dataframe(clients_toute_annee, use_container_width=True)

# ===============================
# FOOTER
# ===============================
st.markdown(
    "<hr style='margin-top:40px;'>"
    "<p style='text-align:center;color:#6B7280;'>© 2025 DigiPay – Direction Data & Analytics</p>",
    unsafe_allow_html=True
)
