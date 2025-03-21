import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
import altair as alt
import pandas as pd


st.set_page_config(page_title="Dimensão Fractal")
# st.logo("./assets/images/ialogo.png", icon_image="./assets/images/ialogo2.png")


if 'df_b' not in st.session_state:
    st.session_state.df_b = None
if 'df_p' not in st.session_state:
    st.session_state.df_p = None


def load_css(file_name: str):
    """Função para carregar CSS externo e aplicá-lo no Streamlit."""
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


load_css("styles.css")


def ajuste_linear(x, y):
    a = np.sum(x * y) / np.sum(x ** 2)
    return a


def imagem_para_tons_de_cinza(imagem):
    return imagem.convert('L')


def corte(imagem, valor, tipo):
    imagem = imagem.convert('L')
    matriz_tons_de_cinza = np.array(imagem)
    if tipo == 'M':
        matriz_filtrada = np.where(matriz_tons_de_cinza < valor, 255, 0)
    else:
        matriz_filtrada = np.where(matriz_tons_de_cinza > valor, 255, 0)
    return Image.fromarray(matriz_filtrada.astype(np.uint8))


def dividir_em_blocos(imagem, tamanho):
    largura, altura = imagem.size
    blocos = [imagem.crop((x, y, x + tamanho, y + tamanho))
              for y in range(0, altura, tamanho) for x in range(0, largura, tamanho)]
    return blocos


def calcular_dimensao_fractal(imagem, status, label):
    largura, altura = imagem.size
    dados = {}
    index = len(list(range(largura - 1, 2, -2)))
    cnt = 1
    if label == 'Calculando a dimensão fractal da ramificação em branco':
        for i in range(largura - 1, 2, -2):
            status.update(label=f"{label} - {100*(cnt / index):.2f}%")
            cnt = cnt+1
            prop = i / largura
            prop_inv = 1 / prop
            blocos = dividir_em_blocos(imagem, i)
            contagem = sum(np.sum(np.array(bloco) < 1) > 0 for bloco in blocos)
            dados[contagem] = prop_inv
        tam_lado = np.array(list(dados.values()))
        num_caixas = np.array(list(dados.keys()))
        ajuste = ajuste_linear(
            np.log(tam_lado[-100:]), np.log(num_caixas[-100:]))

        st.session_state.df_b = ajuste
        st.session_state.dado_b = pd.DataFrame({
            "x": tam_lado,
            "y": num_caixas,
            "x_log": np.log(tam_lado),
            "y_log": np.log(num_caixas)
        })
    else:
        for i in range(largura - 1, 2, -2):
            status.update(label=f"{label} - {100*(cnt / index):.2f}%")
            cnt = cnt+1
            prop = i / largura
            prop_inv = 1 / prop
            blocos = dividir_em_blocos(imagem, i)
            contagem = sum(np.sum(np.array(bloco) > 0) > 0 for bloco in blocos)
            dados[contagem] = prop_inv
        tam_lado = np.array(list(dados.values()))
        num_caixas = np.array(list(dados.keys()))
        ajuste = ajuste_linear(
            np.log(tam_lado[-50:]), np.log(num_caixas[-50:]))
        st.session_state.df_p = ajuste
        st.session_state.dado_p = pd.DataFrame({
            "x": tam_lado,
            "y": num_caixas,
            "x_log": np.log(tam_lado),
            "y_log": np.log(num_caixas)
        })
    return ajuste


def callback():
    st.session_state.df_b = None
    st.session_state.df_p = None
    pass


def callback_calc():
    pass


def main():
    caption_text_preto = "Ramificação em preto"
    caption_text_branco = "Ramificação em branco"
    st.markdown(f"\n<h5 style='text-align: center;'>Dimensão Fractal de Ramificações de Árvores</h5>",
                unsafe_allow_html=True)
    st.sidebar.header("Parâmentros e configurações")
    imagens_exemplo = {"Árvore 1": "image2.png",
                       "Árvore 2": "image6.png", "Árvore 3": "image8.png"}
    opcao = st.sidebar.selectbox("Escolha uma imagem de exemplo:", list(
        imagens_exemplo.keys()), on_change=callback)

    imagem = None
    arquivo = st.sidebar.file_uploader(
        "Carregue sua imagem:", type=["png", "jpg", "jpeg"], on_change=callback)
    if arquivo:
        imagem = Image.open(arquivo)
    else:
        caminho = imagens_exemplo[opcao]
        imagem = Image.open(f"./imagens/{caminho}")

    valor_corte = st.sidebar.slider(
        "Ajuste o valor de corte para P&B: ", 0, 255, 20, key='valor_corte', on_change=callback)

    if imagem:
        conttg = st.sidebar.container()
        conttg2 = st.sidebar.container()
        on = conttg.toggle("Ver imagens em linhas", value=False, key="toggle")

        conttg2.divider()

        if conttg2.button("Calcular dimensão fractal", use_container_width=True):
            empty_space = st.empty()
            with empty_space.container():
                with st.status('Calculando a dimensão fractal...', expanded=False) as status:
                    imagem_pb_branco = corte(imagem, valor_corte, 'M')
                    imagem_pb_preto = corte(imagem, valor_corte, 'm')
                    dimensao_branco = calcular_dimensao_fractal(
                        imagem_pb_branco, status, 'Calculando a dimensão fractal da ramificação em branco')
                    dimensao_preto = calcular_dimensao_fractal(
                        imagem_pb_preto, status, 'Calculando a dimensão fractal da ramificação em preto')
            empty_space.empty()

        st.session_state.imagem = imagem
        if "df_p" in st.session_state and st.session_state.df_p is not None:
            caption_text_preto += f"\n\nDimensão fractal: {st.session_state.df_p:.4f}"

        if "df_b" in st.session_state and st.session_state.df_b is not None:
            caption_text_branco += f"\n\nDimensão fractal: {st.session_state.df_b:.4f}"

        if st.session_state.toggle:
            cols = st.columns([0.2, 0.6, 0.2])
            show_image = conttg.radio('Visualizar image: ', [
                                      'Original', 'Ramificação em preto', 'Ramificação em branco'])
            if show_image == 'Original':
                cols[1].image(imagem, caption="Imagem original",
                              use_container_width=True)
            elif show_image == 'Ramificação em preto':
                cols[1].image(corte(imagem, valor_corte, 'M'),
                              caption=caption_text_preto, use_container_width=True)
            else:
                imagem_pb_branco = corte(imagem, valor_corte, 'M')
                cols[1].image(corte(imagem, valor_corte, 'm'),
                              caption=caption_text_branco, use_container_width=True)

        else:
            cols = st.container(border=True).columns(3)
            cols[0].image(imagem, caption="Imagem original",
                          use_container_width=True)

            cols[1].image(corte(imagem, valor_corte, 'M'),
                          caption=caption_text_preto, use_container_width=True)
            cols[2].image(corte(imagem, valor_corte, 'm'),
                          caption=caption_text_branco, use_container_width=True)

        if st.session_state.df_p:
            cont1 = st.container(border=True)
            cont1.markdown(f"\n<h6 style='text-align: center;'> Gráficos com dados do algoritmo de Contagem de Caixas</h6>",
                           unsafe_allow_html=True)
            cont2 = st.container(border=True)
            cont2.markdown(f"\n<h6 style='text-align: center;'> Tabela com dados do algoritmo de Contagem de Caixas</h6>",
                           unsafe_allow_html=True)
            cols2 = cont1.columns(2)
            cols3 = cont2.columns(2)

            st.sidebar.markdown(
                f"**Dimensão fractal da ramificação em preto:** {st.session_state.df_p:.4f}")
            chart = alt.Chart(st.session_state.dado_p).mark_line(strokeDash=[5, 2],  # Linha tracejada
                                                                 color="blue").encode(
                x=alt.X("x_log", title="Log da número de divisões"),
                y=alt.Y("y_log", title="Log do número de caixas com pixel preto"),
                tooltip=[alt.Tooltip("x", title="r: "), alt.Tooltip("y", title="N: "), alt.Tooltip("x_log", title="Log(r): "), alt.Tooltip("y_log", title="Log(N)"),
                         alt.Tooltip(
                             "y_log", title="Log do número de caixas com pixel preto"),
                         ]
            ).properties(height=400,
                         title=alt.TitleParams(
                             text="Ramificação em preto",
                             anchor="middle"  # Centraliza o título
                         )
                         )

            pontos = alt.Chart(st.session_state.dado_p).mark_point(
                size=100,  # Tamanho dos pontos
                color="white",
                stroke="red",  # Borda vermelha
                strokeWidth=2  # Espessura da borda
            ).encode(
                x="x_log",
                y="y_log"
            )

            chart = chart + pontos

            cols2[0].altair_chart(
                chart, use_container_width=True)

            cols3[0].dataframe(st.session_state.dado_b.rename(columns={"x": "No de divisões (x)", "y": "No de caixas não vazias (N)","x_log":"Log(x)", "y_log": "Log(N)" }),hide_index=True)

        if st.session_state.df_b:

            st.sidebar.markdown(
                f"**Dimensão fractal da ramificação em branco:** {st.session_state.df_b:.4f}")

            chart = alt.Chart(st.session_state.dado_b).mark_line(
                strokeDash=[5, 2],  # Linha tracejada
                color="blue"
            ).encode(
                x=alt.X("x_log", title="Log do número de divisões"),
                y=alt.Y("y_log", title="Log do número de caixas com pixel branco"),
                tooltip=[
                    alt.Tooltip("x", title="r: "),
                    alt.Tooltip("y", title="N: "),
                    alt.Tooltip("x_log", title="Log(r): "),
                    alt.Tooltip("y_log", title="Log(N)")
                ]
            ).properties(
                    height=400,
                    title=alt.TitleParams(
                        text="Ramificação em branco",
                        anchor="middle"  # Centraliza o título
                    )
                )

            pontos = alt.Chart(st.session_state.dado_b).mark_point(
                size=100,  # Tamanho dos pontos
                color="white",
                stroke="red",  # Borda vermelha
                strokeWidth=2  # Espessura da borda
            ).encode(
                x="x_log",
                y="y_log"
            )

            chart = chart + pontos

            # Exibir gráfico no Streamlit
            cols2[1].altair_chart(
                chart, use_container_width=True)

            cols3[1].dataframe(st.session_state.dado_b.rename(columns={"x": "No de divisões (x)", "y": "No de caixas não vazias (N)","x_log":"Log(x)", "y_log": "Log(N)" }),hide_index=True)


if __name__ == "__main__":
    main()
