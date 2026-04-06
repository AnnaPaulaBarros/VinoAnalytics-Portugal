#Projeto: Análise de Produção Vinícola em Portugal
# Autora: Anna Paula Barros da Silva

#Importação das bibliotecas
import streamlit as st
import pandas as pd
import pyodbc
import plotly.express as px

# Configurações iniciais do Streamlit
st.set_page_config(page_title="VinoAnalytics Portugal", layout="wide")

# Títulos
st.title("VinoAnalytics Portugal")
st.write("Dashboard interativo da produção vinícola em Portugal (Dados INE - Safra 2025)")

# Menu lateral
with st.sidebar:
    st.header("Sobre o Projeto")
    st.info("Dados extraídos do INE (Instituto Nacional de Estatística) Portugal.")
    st.write("Desenvolvido por: Anna Paula Barros da Silva")
    st.markdown("---")
    st.subheader("Filtros de Análise")

# Carregamento de dados
# Utilizei @st.cache_data para que o Streamlit não precise de reler o arquivo a cada clique do usuário.
@st.cache_data
def carregar_dados():
    try:
        # 1. Extração via SQL Server        
        conn = pyodbc.connect(
            "DRIVER={SQL Server};"
            "SERVER=ANNAPAULABDS\\SQLEXPRESS;"
            "DATABASE=VinoAnalytics_Portugal;"
            "Trusted_Connection=yes;"
        )
        query = "SELECT Nome_Regiao, Quantidade_HL FROM Producao_Vinho WHERE Ano = 2025"
        df = pd.read_sql(query, conn)
        conn.close()
        return df, "SQL Server (Local)"
    except Exception:
        # 2. Caso o SQL Server esteja inacessível, ele usa o ficheiro que limpei, onde, extrai os dados do INE.
        df = pd.read_csv("producao_vinho.csv")
        return df, "Arquivo CSV (Cloud Mode)"

df, fonte = carregar_dados()
st.sidebar.caption(f"Fonte de dados atual: {fonte}")

# GEORREFERENCIAMENTO
# Mapeamento manual de latitude e longitude para que as regiões apareçam corretamente no mapa.
coordenadas = {
    "Entre Douro e Minho": [41.5, -8.0],
    "Trás-os-Montes": [41.8, -7.3],
    "Beira Litoral": [40.2, -8.4],
    "Beira Interior": [40.3, -7.3],
    "Ribatejo e Oeste": [39.3, -8.5],
    "Alentejo": [38.5, -7.9],
    "Algarve": [37.1, -8.0],
    "Açores": [37.7, -25.5],
    "Madeira": [32.7, -16.9]
}

# Apliquei a função lambda para criar novas colunas baseadas nas cordenadas
df["lat"] = df["Nome_Regiao"].apply(lambda x: coordenadas.get(x, [0,0])[0])
df["lon"] = df["Nome_Regiao"].apply(lambda x: coordenadas.get(x, [0,0])[1])

# Filtro 1: Seleção múltipla de regiões
regioes = st.sidebar.multiselect(
    "Selecione as regiões para comparar:",
    options=df["Nome_Regiao"].unique(),
    default=df["Nome_Regiao"].unique()
)

# Filtro 2: Slider de produção (hl)
min_p, max_p = int(df["Quantidade_HL"].min()), int(df["Quantidade_HL"].max())
faixa_producao = st.sidebar.slider("Filtrar por Volume (hl):", min_p, max_p, (min_p, max_p))

# Aplicação efetiva dos filtros no DataFrame
df_filtrado = df[
    (df["Nome_Regiao"].isin(regioes)) &
    (df["Quantidade_HL"] >= faixa_producao[0]) &
    (df["Quantidade_HL"] <= faixa_producao[1])
]

# PAINEL DE INDICADORES (KPIs)
col1, col2 = st.columns(2)

with col1:
    total_hl = df_filtrado["Quantidade_HL"].sum()
    st.metric("Volume Total Filtrado", f"{total_hl:,} hl")

with col2:
    if not df_filtrado.empty:
        # Identifiquei a região com maior produção no filtro atual
        top = df_filtrado.sort_values("Quantidade_HL", ascending=False).iloc[0]
        st.success(f"Líder do Filtro: {top['Nome_Regiao']}")

# VISUALIZAÇÕES
st.markdown("---")
tab_graficos, tab_mapa = st.tabs(["Gráficos e Tabelas", "Mapa Geográfico"])

with tab_graficos:
    st.subheader("Análise Comparativa por Região")
    # Gráfico nativo do Streamlit 
    st.bar_chart(df_filtrado.set_index("Nome_Regiao")["Quantidade_HL"])
    
    st.subheader("Exploração de Microdados")
    # Tabela interativa com largura ajustável
    st.dataframe(df_filtrado[["Nome_Regiao", "Quantidade_HL"]], use_container_width=True)

with tab_mapa:
    st.subheader("Distribuição Geográfica (Cores da Bandeira de Portugal)")
    if not df_filtrado.empty:
        # Cores Verde, Vermelho e Amarelo para as regiões
        cores_pt = ["#006600", "#FF0000", "#FFCC00"] 
        df_filtrado = df_filtrado.copy() # Evita avisos de cópia do Pandas
        df_filtrado["cor"] = [cores_pt[i % 3] for i in range(len(df_filtrado))]

        # Ajuste de Tema para o Plotly.
        is_dark = st.get_option("theme.base") == "dark"
        
        # Criação do Mapa Mapbox
        fig = px.scatter_mapbox(
            df_filtrado,
            lat="lat",
            lon="lon",
            size="Quantidade_HL",
            color="cor",
            color_discrete_map="identity", 
            hover_name="Nome_Regiao",
            hover_data={"Quantidade_HL": True, "cor": False, "lat": False, "lon": False},
            size_max=45,
            zoom=5,
            template="plotly_dark" if is_dark else "plotly_white"
        )

        # Estilo do mapa
        fig.update_layout(
            mapbox_style="carto-positron" if not is_dark else "carto-darkmatter",
            margin={"r":0,"t":0,"l":0,"b":0},
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Selecione pelo menos uma região para carregar o mapa.")