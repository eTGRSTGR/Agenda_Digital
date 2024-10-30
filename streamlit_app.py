import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(layout='wide')

# Função principal
def main():
    st.title("Agenda Digital para Despesas")
    st.write("Controle suas despesas de forma simples e eficiente.")

    # Carregar dados salvos
    df = carregar_dados()

    # Adicionar nova despesa na sidebar
    adicionar_despesa_sidebar(df)

    # Adicionar nova categoria na sidebar
    adicionar_categoria_sidebar(df)

    # Mostrar histórico de despesas
    mostrar_historico_despesas(df)

    # Análise gráfica
    analise_grafica(df)

# Função para carregar dados salvos
def carregar_dados():
    try:
        return pd.read_csv("despesas.csv")
    except FileNotFoundError:
        return pd.DataFrame(columns=["Categoria", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])

# Função para adicionar nova despesa na sidebar
def adicionar_despesa_sidebar(df):
    with st.sidebar:
        st.header("Adicionar Nova Despesa")
        mes = st.selectbox("Mês", ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"])
        categoria = st.selectbox("Categoria", df['Categoria'].unique() if not df.empty else ["Alimentação", "Transporte", "Lazer", "Educação", "Saúde", "Outros"])
        valor = st.number_input("Valor (R$)", min_value=0.0, format="%.2f")

        if st.button("Adicionar Despesa"):
            df = adicionar_despesa(df, mes, categoria, valor)
            df.to_csv("despesas.csv", index=False)
            st.success("Despesa adicionada com sucesso!")
            st.balloons()  # Feedback visual após adicionar despesa

# Função para adicionar nova categoria na sidebar
def adicionar_categoria_sidebar(df):
    with st.sidebar:
        st.header("Adicionar Nova Categoria")
        nova_categoria = st.text_input("Nome da Nova Categoria")

        if st.button("Adicionar Categoria"):
            if nova_categoria and nova_categoria not in df['Categoria'].values:
                nova_linha = pd.DataFrame({
                    "Categoria": [nova_categoria],
                    "Janeiro": [0.0], "Fevereiro": [0.0], "Março": [0.0], "Abril": [0.0], "Maio": [0.0], "Junho": [0.0],
                    "Julho": [0.0], "Agosto": [0.0], "Setembro": [0.0], "Outubro": [0.0], "Novembro": [0.0], "Dezembro": [0.0]
                })
                df = pd.concat([df, nova_linha], ignore_index=True)
                df.to_csv("despesas.csv", index=False)
                st.success("Categoria adicionada com sucesso!")
            elif nova_categoria in df['Categoria'].values:
                st.warning("Essa categoria já existe.")
            else:
                st.error("Por favor, insira um nome válido para a categoria.")

# Função para adicionar despesa ao DataFrame
def adicionar_despesa(df, mes, categoria, valor):
    if mes in df.columns:
        if not df[df['Categoria'] == categoria].empty:
            df.loc[(df['Categoria'] == categoria), mes] += valor
        else:
            nova_despesa = pd.DataFrame({
                "Categoria": [categoria],
                "Janeiro": [0.0], "Fevereiro": [0.0], "Março": [0.0], "Abril": [0.0], "Maio": [0.0], "Junho": [0.0],
                "Julho": [0.0], "Agosto": [0.0], "Setembro": [0.0], "Outubro": [0.0], "Novembro": [0.0], "Dezembro": [0.0]
            })
            nova_despesa[mes] = valor
            df = pd.concat([df, nova_despesa], ignore_index=True)
    else:
        st.error("Erro ao adicionar despesa. Verifique o mês selecionado.")
    return df

# Função para mostrar histórico de despesas
def mostrar_historico_despesas(df):
    st.header("Histórico de Despesas")
    if not df.empty:
        df = adicionar_total(df)
        # Formatar os valores monetários
        for mes in ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]:
            if mes in df.columns:
                df[mes] = df[mes].apply(lambda x: f"R$ {x:,.2f}")
        st.markdown("<div style='text-align: center;'>", unsafe_allow_html=True)
        st.dataframe(df)
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='text-align: center;'>Nenhuma despesa registrada até o momento.</div>", unsafe_allow_html=True)

# Função para adicionar linha de total ao DataFrame
def adicionar_total(df):
    total = df.select_dtypes(include=[float]).sum()
    total_row = pd.DataFrame([["Total"] + total.tolist()], columns=df.columns)
    df = pd.concat([df, total_row], ignore_index=True)
    return df

# Função para análise gráfica
def analise_grafica(df):
    st.header("Análise de Despesas")
    if not df.empty:
        meses = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]
        df[meses] = df[meses].fillna(0.0)

        # Layout de colunas para gráficos lado a lado
        col1, col2 = st.columns(2)

        # Gráfico de despesas por categoria
        with col1:
            st.subheader("Despesas por Categoria")
            despesas_categoria = df.groupby("Categoria")[meses].sum().sum(axis=1)
            fig_bar = px.bar(
                despesas_categoria, 
                x=despesas_categoria.index, 
                y=despesas_categoria.values, 
                labels={'x': 'Categoria', 'y': 'Valor (R$)'}, 
                title="Despesas por Categoria",
                color=despesas_categoria.index,  # Adiciona cores diferentes para cada categoria
                color_discrete_sequence=px.colors.qualitative.Set3  # Escolha de uma paleta de cores variada
            )
            st.plotly_chart(fig_bar)

        # Gráfico de pizza das despesas por categoria
        with col2:
            st.subheader("Distribuição de Despesas por Categoria")
            fig_pie = px.pie(
                despesas_categoria, 
                names=despesas_categoria.index, 
                values=despesas_categoria.values, 
                title="Distribuição de Despesas por Categoria",
                color_discrete_sequence=px.colors.qualitative.Pastel  # Escolha de uma paleta de cores variada
            )
            st.plotly_chart(fig_pie)

        # Gráfico de despesas ao longo dos meses
        st.subheader("Despesas ao Longo dos Meses")
        despesas_mes = df[meses].sum()
        fig_line = px.line(
            despesas_mes, 
            x=despesas_mes.index, 
            y=despesas_mes.values, 
            labels={'x': 'Mês', 'y': 'Valor (R$)'}, 
            title="Despesas ao Longo dos Meses",
            color_discrete_sequence=["#636EFA"]  # Cor de destaque para o gráfico de linha
        )
        st.plotly_chart(fig_line)

if __name__ == "__main__":
    main()