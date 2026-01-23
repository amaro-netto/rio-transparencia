import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Monitor de Transparência - Paracambi",
    page_icon="🏛️",
    layout="wide"
)

# CSS APENAS PARA RODAPÉ E ALINHAMENTO
st.markdown("""
<style>
    div[data-testid="column"] { display: flex; flex-direction: column; justify-content: flex-start; }
    .footer-container { margin-top: 80px; padding-top: 20px; border-top: 1px solid #444; }
    a { text-decoration: none; color: inherit; }
    a:hover { opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. FUNÇÃO CARD UNIFICADA (KPI)
# ==========================================
def custom_card(label, value, desc, color, arrow=None):
    arrow_html = ""
    if arrow == 'up':
        arrow_html = "<span>↑</span>&nbsp;" 
    elif arrow == 'down':
        arrow_html = "<span>↓</span>&nbsp;"
    
    html = f"""
    <div style="background-color: rgba(255, 255, 255, 0.05); border: 1px solid rgba(250, 250, 250, 0.2); border-radius: 8px; padding: 15px; height: 100%; display: flex; flex-direction: column; justify-content: center; margin-bottom: 10px;">
        <span style="font-size: 14px; color: #e0e0e0; margin-bottom: 5px;">{label}</span>
        <span style="font-size: 32px; font-weight: 700; color: #ffffff; margin-bottom: 5px; line-height: 1.1;">{value}</span>
        <span style="font-size: 14px; font-weight: 500; color: {color}; display: flex; align-items: center;">
            {arrow_html}{desc}
        </span>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

# ==========================================
# 3. CABEÇALHO
# ==========================================
head1, head2 = st.columns([2, 5])

with head1:
        st.image("https://raw.githubusercontent.com/amaro-netto/rio-transparencia/ce4b2dac8c9f4bafe8f5c2053f4e32db5323509a/data/logo.svg", use_container_width=True)

with head2:
    st.title("Painel de Inteligência e Conformidade Pública")
    st.markdown("""
    **Objeto:** Prefeitura Municipal de Paracambi - RJ  
    **Metodologia:** EBT (CGU) + Auditoria IA  
    **Fonte Oficial:** [Dados Abertos - Escala Brasil Transparente 🔗](https://dados.gov.br/dados/conjuntos-dados/escala-brasil-transparente-ebt)
    """)

st.divider()

# ==========================================
# 4. CARGA DE DADOS
# ==========================================
@st.cache_data
def carregar_dados():
    path_ranking = 'data/processed/rj_ebt_limpo.csv'
    path_laudo = 'data/processed/LAUDO_TECNICO_GEMINI_FINAL.xlsx'
    
    if not os.path.exists(path_ranking): return None, None
    df_rank = pd.read_csv(path_ranking)
    df_laud = pd.read_excel(path_laudo) if os.path.exists(path_laudo) else None
    
    return df_rank, df_laud

df_ranking, df_laudo = carregar_dados()

if df_ranking is None:
    st.error("❌ Dados base não encontrados.")
    st.stop()

# ==========================================
# 5. KPIS (MÉTRICAS)
# ==========================================
try:
    paracambi = df_ranking[df_ranking['is_paracambi'] == 'Sim'].iloc[0]
except IndexError:
    st.error("Paracambi não encontrada.")
    st.stop()

media_rj = df_ranking['nota'].mean()
melhor_rj = df_ranking.iloc[0]

raw_rank_br = paracambi.get('ranking_nacional', 0)
rank_br_text = f"{int(raw_rank_br)}º" if raw_rank_br > 0 else "-"

c1, c2, c3, c4, c5 = st.columns(5)

# 1. Ranking Brasil
with c1:
    custom_card("Ranking Brasil", rank_br_text, "Posição Nacional", "#FF4B4B", None)

# 2. Ranking RJ
with c2:
    custom_card("Ranking RJ", f"{int(paracambi['ranking_estadual'])}º", "Posição Estadual", "#FFA500", None)

# 3. Nota EBT
with c3:
    diff = paracambi['nota'] - media_rj
    custom_card("Nota EBT", f"{paracambi['nota']:.2f}", f"{diff:.2f} Média", "#FF4B4B", 'down')

# 4. Referência
with c4:
    gap = melhor_rj['nota'] - paracambi['nota']
    custom_card("Referência (Top 1)", f"{melhor_rj['nota']}", f"Faltam {gap:.2f} pts", "#00CC96", 'up')

# 5. Atenção
with c5:
    riscos_count = len(df_laudo) if df_laudo is not None else 0
    custom_card("Pontos de Atenção", str(riscos_count), "Ação Necessária", "#FF4B4B", None)

st.markdown("---")

# ==========================================
# 6. GRÁFICOS
# ==========================================
g1, g2 = st.columns([2, 1.5])

with g1:
    st.subheader("📊 Comparativo Regional")
    vizinhos = ['Japeri', 'Seropédica', 'Mendes', 'Piraí', 'Vassouras']
    filtro = ((df_ranking['ranking_estadual'] <= 5) | (df_ranking['is_paracambi'] == 'Sim') | (df_ranking['municipio'].str.contains('|'.join(vizinhos), na=False)))
    
    df_chart = df_ranking[filtro].sort_values('nota', ascending=True)
    colors = ['#FF4B4B' if 'Paracambi' in str(x) else '#0068C9' for x in df_chart['municipio']]
    
    fig = px.bar(df_chart, x='nota', y='municipio', orientation='h', text='nota')
    fig.update_traces(marker_color=colors, texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_range=[0, 11], margin=dict(l=0, r=0, t=0, b=0), yaxis_title="")
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.subheader("🌡️ Termômetro de Risco Legal")
    if df_laudo is not None:
        mapa_pontos = {'Alta': 3, 'Média': 2, 'Baixa': 1, 'N/A': 0}
        if 'Gravidade' in df_laudo.columns:
            pontos_totais = df_laudo['Gravidade'].map(mapa_pontos).sum()
        else:
            pontos_totais = len(df_laudo) * 2
        max_termometro = 50 
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = pontos_totais,
            title = {'text': "Nível de Criticidade"},
            gauge = {
                'axis': {'range': [None, max_termometro]},
                'bar': {'color': "black"},
                'steps': [
                    {'range': [0, 15], 'color': "#00CC96"},
                    {'range': [15, 30], 'color': "#FFFB00"},
                    {'range': [30, max_termometro], 'color': "#FF4B4B"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': pontos_totais
                }
            }
        ))
        fig_gauge.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
        st.plotly_chart(fig_gauge, use_container_width=True)
        st.caption("🟢 Verde: Risco Baixo  | 🟡 Amarelo: Risco Médio | 🔴 Vermelho: Risco Alto ")
    else:
        st.info("Sem dados para calcular risco.")

# ==========================================
# 7. LAUDO TÉCNICO (AGORA COLORIDO E SEPARADO)
# ==========================================
st.markdown("---")
st.subheader("⚖️ Laudo Técnico Detalhado (IA)")

if df_laudo is not None:
    for i, row in df_laudo.iterrows():
        gravidade = row.get('Gravidade', 'N/A')
        icon = "🔴" if gravidade == "Alta" else "🟠" if gravidade == "Média" else "🔵"
        
        # Expander (Cabeçalho)
        with st.expander(f"{icon} {row['Questão Original']} (Perda: {row['Pontos Perdidos']} pts)"):
            
            # Divide em 2 Colunas para comparar Problema vs Solução
            lc1, lc2 = st.columns(2)
            
            # --- COLUNA 1: O PROBLEMA (VERMELHO) ---
            with lc1:
                st.markdown("#### ⚖️ Análise Jurídica")
                # Caixa Vermelha (Error) para destacar o Risco
                st.error(f"**Risco Legal:** {row.get('Risco Legal', 'Não analisado')}")
                # Lei como nota de rodapé
                st.caption(f"📜 **Base Legal:** {row.get('Lei', '-')}")
            
            # --- COLUNA 2: A SOLUÇÃO (VERDE) ---
            with lc2:
                st.markdown("#### 🛠️ Solução Técnica")
                # Caixa Verde (Success) para destacar a Ação
                st.success(f"**Ação Recomendada:** {row.get('Ação Recomendada', 'Verificar manualmente')}")
                # Referência como nota de rodapé
                st.caption(f"🏛️ **Benchmarking:** {row.get('Referência', '-')}")

else:
    st.warning("Laudo ainda não processado.")

# ==========================================
# 8. RODAPÉ (CENTRALIZADO)
# ==========================================
st.markdown('<div class="footer-container"></div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns([1, 2, 1])

with f1:
    st.image("https://raw.githubusercontent.com/amaro-netto/amaro-netto/a5c3e8fe0abad9646b67183153a08881a1ba2805/logos/amaronetto%20solucoes/SVG/2.0/AMARO%20NETTO%20SOLU%C3%87%C3%95ES%202.0%20BRANCO.svg", width=220)
with f2:
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%;">
        <div style="text-align: center; color: #888; font-size: 14px;">
            <b>© 2025 Amaro Netto Soluções.</b><br>Relatório baseado em dados públicos.
        </div>
    </div>""", unsafe_allow_html=True)
with f3:
    st.markdown("""<div style="display: flex; justify-content: flex-end; align-items: center; gap: 20px; margin-top: 15px;">
        <a href="https://www.linkedin.com/in/amarosilvanetto/" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/3536/3536505.png" width="32" style="filter: invert(1);"></a>
        <a href="https://github.com/amaro-netto" target="_blank"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="32" style="filter: invert(1);"></a>
        </div>""", unsafe_allow_html=True)