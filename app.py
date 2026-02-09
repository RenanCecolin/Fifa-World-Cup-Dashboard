import streamlit as st
import pandas as pd
import plotly.express as px


# Configuração da Página
st.set_page_config(
    page_title="Copa do Mundo FIFA (1930–2014)",
    page_icon="⚽",
    layout="wide"
)


# Cores da FIFA
CORES_FIFA = {
    "azul": "#0033A0",
    "verde": "#009A44",
    "dourado": "#C9A227",
    "cinza": "#F5F5F5"
}


# Carregamento dos dados
@st.cache_data
def carregar_dados():
    df = pd.read_csv("WorldCupMatches_1930_2014_PT_BR.csv")
    df["Ano_da_Copa"] = pd.to_numeric(df["Ano_da_Copa"], errors="coerce").astype("Int64")
    return df

df = carregar_dados()
df_estadios = pd.read_csv("estadios_lat_long.csv")


# Ordem das fases
ordem_fases = [
    "Fase de Grupos",
    "Oitavas de Final",
    "Quartas de Final",
    "Semifinal",
    "Disputa de Terceiro Lugar",
    "Final"
]


# Filtros
st.sidebar.header("🔎 Filtros")

anos = sorted(df["Ano_da_Copa"].dropna().unique())
filtro_anos = st.sidebar.multiselect("Ano da Copa", anos, default=anos)

fases_disp = [f for f in ordem_fases if f in df["Fase_do_Torneio"].unique()]
filtro_fases = st.sidebar.multiselect("Fase do Torneio", fases_disp, default=fases_disp)

selecoes = sorted(
    pd.concat([df["Selecao_Mandante"], df["Selecao_Visitante"]]).dropna().unique()
)
filtro_selecao = st.sidebar.multiselect("Seleção", selecoes)

estadios = sorted(df["Estadio"].dropna().unique())
filtro_estadio = st.sidebar.multiselect("Estádio", estadios)


# Filtragem
df_filtrado = df[df["Ano_da_Copa"].isin(filtro_anos)]

if filtro_fases:
    df_filtrado = df_filtrado[df_filtrado["Fase_do_Torneio"].isin(filtro_fases)]

if filtro_selecao:
    df_filtrado = df_filtrado[
        (df_filtrado["Selecao_Mandante"].isin(filtro_selecao)) |
        (df_filtrado["Selecao_Visitante"].isin(filtro_selecao))
    ]

if filtro_estadio:
    df_filtrado = df_filtrado[df_filtrado["Estadio"].isin(filtro_estadio)]


# Título
st.title("⚽ Copa do Mundo FIFA (1930–2014)")
st.markdown("Dashboard interativo com estatísticas históricas das Copas do Mundo.")


# KPIs
col1, col2, col3, col4, col5 = st.columns(5)

total_partidas = df_filtrado.shape[0]
total_gols = (df_filtrado["Gols_Mandante"] + df_filtrado["Gols_Visitante"]).sum()
media_gols = round(total_gols / total_partidas, 2) if total_partidas else 0
publico_medio = int(df_filtrado["Publico"].mean()) if not df_filtrado.empty else 0

gols_por_copa = (
    df_filtrado
    .groupby("Ano_da_Copa")[["Gols_Mandante", "Gols_Visitante"]]
    .sum()
    .sum(axis=1)
)

copa_top = gols_por_copa.idxmax()
gols_top = gols_por_copa.max()

col1.metric("🏟️ Partidas", total_partidas)
col2.metric("⚽ Gols", total_gols)
col3.metric("📊 Média de gols", media_gols)
col4.metric("👥 Público médio", f"{publico_medio:,}")
col5.metric("🏆 Copa + gols", f"{copa_top}", f"{gols_top} gols")

st.info(
    f"📖 A Copa de **{copa_top}** foi a mais ofensiva da história, "
    f"com **{gols_top} gols**, média de **{round(gols_top / df_filtrado[df_filtrado['Ano_da_Copa'] == copa_top].shape[0], 2)} gols por jogo**."
)

st.markdown("---")


# Abas
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📊 Visão Geral",
    "🏆 Ranking",
    "⚽ Gols por Copa",
    "📈 Público",
    "🗺️ Estádios",
    "⚔️ Comparação"
])


# ABA 1 - Visão Geral
with aba1:
    fases = (
        df_filtrado["Fase_do_Torneio"]
        .value_counts()
        .reindex(ordem_fases)
        .dropna()
        .reset_index()
    )
    fases.columns = ["Fase", "Partidas"]

    fig = px.bar(
        fases,
        x="Fase",
        y="Partidas",
        color_discrete_sequence=[CORES_FIFA["azul"]],
        title="🏆 Partidas por Fase"
    )
    fig.update_layout(plot_bgcolor=CORES_FIFA["cinza"])
    st.plotly_chart(fig, use_container_width=True)


# ABA 2 - Ranking (Gols + Partidas)
with aba2:
    df_result = df_filtrado.copy()
    df_result["Vencedor"] = df_result.apply(
        lambda x: x["Selecao_Mandante"]
        if x["Gols_Mandante"] > x["Gols_Visitante"]
        else x["Selecao_Visitante"]
        if x["Gols_Visitante"] > x["Gols_Mandante"]
        else None,
        axis=1
    )

    ranking_vitorias = (
        df_result["Vencedor"]
        .value_counts()
        .dropna()
        .head(10)
        .reset_index()
    )
    ranking_vitorias.columns = ["Seleção", "Vitórias"]

    fig = px.bar(
        ranking_vitorias,
        x="Vitórias",
        y="Seleção",
        orientation="h",
        color_discrete_sequence=[CORES_FIFA["verde"]],
        title="🏆 Top 10 Seleções por Vitórias"
    )
    fig.update_layout(plot_bgcolor=CORES_FIFA["cinza"])
    st.plotly_chart(fig, use_container_width=True)


# ABA 3 - Gols por Copa
with aba3:
    gols = gols_por_copa.reset_index()
    gols.columns = ["Ano da Copa", "Total de Gols"]

    fig = px.line(
        gols,
        x="Ano da Copa",
        y="Total de Gols",
        markers=True,
        color_discrete_sequence=[CORES_FIFA["dourado"]],
        title="⚽ Total de Gols por Copa"
    )
    fig.update_layout(plot_bgcolor=CORES_FIFA["cinza"])
    st.plotly_chart(fig, use_container_width=True)


# ABA 4 - Público
with aba4:
    publico = df_filtrado.groupby("Ano_da_Copa")["Publico"].mean().reset_index()

    fig = px.line(
        publico,
        x="Ano_da_Copa",
        y="Publico",
        markers=True,
        color_discrete_sequence=[CORES_FIFA["azul"]],
        title="👥 Público Médio por Copa"
    )
    fig.update_layout(plot_bgcolor=CORES_FIFA["cinza"])
    st.plotly_chart(fig, use_container_width=True)


# ABA 5 - Mapa dos estádios
with aba5:
    copa_mapa = st.selectbox("Selecione a Copa", sorted(df_filtrado["Ano_da_Copa"].dropna().unique()))

    mapa = (
        df_filtrado[df_filtrado["Ano_da_Copa"] == copa_mapa]
        .merge(df_estadios, on="Estadio", how="left")
        .dropna(subset=["Latitude", "Longitude"])
        .groupby(["Estadio", "Latitude", "Longitude"])
        .size()
        .reset_index(name="Partidas")
    )

    fig = px.scatter_mapbox(
        mapa,
        lat="Latitude",
        lon="Longitude",
        size="Partidas",
        hover_name="Estadio",
        zoom=1,
        mapbox_style="carto-positron",
        title=f"🗺️ Estádios da Copa de {copa_mapa}"
    )
    st.plotly_chart(fig, use_container_width=True)


# ABA 6 - Comparação entre seleções
with aba6:
    sel_a = st.selectbox("Seleção A", selecoes)
    sel_b = st.selectbox("Seleção B", selecoes, index=1)

    def stats(selecao):
        jogos = df_filtrado[
            (df_filtrado["Selecao_Mandante"] == selecao) |
            (df_filtrado["Selecao_Visitante"] == selecao)
        ]
        gols = jogos.apply(
            lambda x: x["Gols_Mandante"] if x["Selecao_Mandante"] == selecao else x["Gols_Visitante"],
            axis=1
        ).sum()
        return jogos.shape[0], gols, round(gols / jogos.shape[0], 2) if jogos.shape[0] else 0

    ja, ga, ma = stats(sel_a)
    jb, gb, mb = stats(sel_b)

    c1, c2 = st.columns(2)
    c1.metric(sel_a, f"{ga} gols", f"{ja} jogos | média {ma}")
    c2.metric(sel_b, f"{gb} gols", f"{jb} jogos | média {mb}")


# Tabela detalhada
st.markdown("---")
st.subheader("📋 Dados Detalhados")
st.dataframe(df_filtrado)
