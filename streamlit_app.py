import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ===============================
# CONFIG PAGE
# ===============================
st.set_page_config(
    page_title="Dashboard Profilage Clients 2025",
    page_icon="📊",
    layout="wide"
)

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
# KPI GLOBAUX
# ===============================
nb_clients = df['Sender Name'].nunique()
nb_transactions = len(df)

# ===============================
# CLIENTS ACTIFS 30 / 60 / 90 JOURS
# ===============================
def count_clients_actifs(jours):
    date_limite = df['TxnDate'].max() - pd.Timedelta(days=jours)
    return df[df['TxnDate'] >= date_limite]['Sender Name'].nunique()

actifs_30j = count_clients_actifs(30)
actifs_60j = count_clients_actifs(60)
actifs_90j = count_clients_actifs(90)

# ===============================
# TRANSACTIONS PAR CLIENT
# ===============================
tx_par_client = (
    df.groupby(['Sender Name', 'Agence'])
    .size()
    .reset_index(name='Nombre_Envois')
)

# ===============================
# SEGMENTATION CLIENT
# ===============================
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

# ===============================
# CLIENTS TOUTE L’ANNÉE (12 MOIS)
# ===============================
df['YearMonth'] = df['TxnDate'].dt.to_period('M')

clients_mensuels = (
    df.groupby(['Sender Name', 'Agence'])['YearMonth']
    .nunique()
    .reset_index(name='Mois_Actifs')
)

clients_toute_annee = clients_mensuels[clients_mensuels['Mois_Actifs'] == 12]

# ===============================
# TOP CLIENTS
# ===============================
top_clients_volume = tx_par_client.sort_values('Nombre_Envois', ascending=False)
top_clients_reguliers = clients_toute_annee.copy()

# ===============================
# SIDEBAR FILTRES
# ===============================
st.sidebar.header("🔎 Filtres")

agences = sorted(df['Agence'].dropna().unique())
agence_sel = st.sidebar.multiselect("Agence", agences, default=agences)

df_filtree = df[df['Agence'].isin(agence_sel)]
tx_filtree = tx_par_client[tx_par_client['Agence'].isin(agence_sel)]

# ===============================
# TITRE
# ===============================
st.markdown("<h1 style='text-align:center;'>📊 Dashboard Profilage Clients – 2025</h1>", unsafe_allow_html=True)
st.divider()

# ===============================
# KPI
# ===============================
c1, c2, c3, c4 = st.columns(4)
c1.metric("👥 Clients", nb_clients)
c2.metric("🔥 Actifs 30j", actifs_30j)
c3.metric("📆 Actifs 60j", actifs_60j)
c4.metric("📅 Actifs 90j", actifs_90j)

st.divider()

# ===============================
# GRAPHIQUE SEGMENTATION
# ===============================
seg_fig = px.bar(
    tx_filtree.groupby('Segment').size().reset_index(name='Clients'),
    x='Segment',
    y='Clients',
    text='Clients',
    title="Segmentation clients 2025"
)

st.plotly_chart(seg_fig, use_container_width=True)

# ===============================
# TOP CLIENTS VOLUME
# ===============================
st.subheader("🏆 Top clients par volume")
st.dataframe(top_clients_volume.head(20), use_container_width=True)

# ===============================
# TOP CLIENTS RÉGULIERS
# ===============================
st.subheader("🔁 Clients réguliers (12 mois actifs)")
st.dataframe(top_clients_reguliers, use_container_width=True)

# ===============================
# DÉTAIL CLIENT
# ===============================
st.subheader("📋 Détail clients")
st.dataframe(tx_filtree.sort_values('Nombre_Envois', ascending=False), use_container_width=True)
