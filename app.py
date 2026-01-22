import streamlit as st
import pandas as pd
import plotly.express as px
import os
from fpdf import FPDF
from datetime import datetime

# ==========================================
# 1. CONFIGURAÇÃO E CSS (ESTILO)
# ==========================================
st.set_page_config(
    page_title="Monitor de Transparência - Paracambi",
    page_icon="🏛️",
    layout="wide"
)

# CSS Avançado para Layout Fino
st.markdown("""
<style>
    /* Ajuste de alinhamento vertical */
    div[data-testid="column"] {
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    /* Rodapé separado visualmente */
    .footer-container {
        margin-top: 60px;
        padding-top: 20px;
        border-top: 1px solid #444;
    }
    /* Estilo dos Links */
    a { text-decoration: none; color: inherit; }
    a:hover { opacity: 0.7; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. CABEÇALHO (AJUSTE DE TAMANHO DE LOGO)
# ==========================================
# Aumentamos a primeira coluna (Ratio 2:5 em vez de 1:5)
head1, head2 = st.columns([1.5, 4.5])

with head1:
    # Logo Paracambi MAIOR
    st.image("https://raw.githubusercontent.com/amaro-netto/rio-transparencia/ce4b2dac8c9f4bafe8f5c2053f4e32db5323509a/data/logo.svg", use_container_width=True)

with head2:
    st.title("Painel de Inteligência e Conformidade Pública")
    
    # Adicionando o Link da Fonte de Dados
    st.markdown("""
    **Objeto:** Prefeitura Municipal de Paracambi - RJ  
    **Metodologia:** EBT (CGU) + Auditoria IA  
    **Fonte Oficial:** [Dados Abertos - Escala Brasil Transparente 🔗](https://dados.gov.br/dados/conjuntos-dados/escala-brasil-transparente-ebt)
    """)

st.divider()

# ==========================================
# 3. CARGA DE DADOS
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
# 4. FUNÇÃO GERADORA DE PDF (NOVA)
# ==========================================
def gerar_pdf_laudo(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Cabeçalho do PDF
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "LAUDO TECNICO DE AUDITORIA - PARACAMBI/RJ", ln=True, align="C")
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, f"Gerado em: {datetime.now().strftime('%d/%m/%Y')} por Amaro Netto Solucoes", ln=True, align="C")
    pdf.ln(10)
    
    # Corpo
    pdf.set_font("Arial", "", 10)
    
    # Itera sobre os erros para criar o documento
    for i, row in dataframe.iterrows():
        # Tratamento de caracteres especiais (Latin-1 é padrão do FPDF básico)
        q = str(row['Questão Original']).encode('latin-1', 'replace').decode('latin-1')
        risco = str(row.get('Risco Legal', '')).encode('latin-1', 'replace').decode('latin-1')
        acao = str(row.get('Ação Recomendada', '')).encode('latin-1', 'replace').decode('latin-1')
        lei = str(row.get('Lei', '')).encode('latin-1', 'replace').decode('latin-1')
        
        # Título do Item (Card)
        pdf.set_font("Arial", "B", 11)
        pdf.set_fill_color(240, 240, 240) # Cinza claro
        pdf.multi_cell(0, 8, f"ITEM {i+1}: {q}", fill=True)
        
        # Conteúdo
        pdf.set_font("Arial", "B", 10)
        pdf.write(5, "Risco Legal: ")
        pdf.set_font("Arial", "", 10)
        pdf.write(5, risco + "\n")
        
        pdf.set_font("Arial", "B", 10)
        pdf.write(5, "Acao Tecnica: ")
        pdf.set_font("Arial", "", 10)
        pdf.write(5, acao + "\n")
        
        pdf.set_font("Arial", "B", 10)
        pdf.write(5, "Base Legal: ")
        pdf.set_font("Arial", "", 10)
        pdf.write(5, lei + "\n")
        
        pdf.ln(5) # Espaço entre itens

    return bytes(pdf.output(dest="S"))

# ==========================================
# 5. KPIs E GRÁFICOS (MANTIDOS)
# ==========================================
try:
    paracambi = df_ranking[df_ranking['is_paracambi'] == 'Sim'].iloc[0]
except IndexError:
    st.error("Paracambi não encontrada.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
media_rj = df_ranking['nota'].mean()
melhor_rj = df_ranking.iloc[0]

c1.metric("Nota Atual", f"{paracambi['nota']:.2f}", f"{paracambi['nota'] - media_rj:.2f} vs Média")
c2.metric("Ranking Estadual", f"{paracambi['ranking_estadual']}º Lugar", delta_color="inverse")
c3.metric("Referência (Top 1)", f"{melhor_rj['nota']}", f"Gap: {melhor_rj['nota'] - paracambi['nota']:.2f}")
riscos_count = len(df_laudo) if df_laudo is not None else 0
c4.metric("Pontos de Atenção", riscos_count, "Ação Necessária", delta_color="inverse")

st.markdown("---")

g1, g2 = st.columns([2, 1])
with g1:
    st.subheader("📊 Benchmarking Regional")
    vizinhos = ['Japeri', 'Seropédica', 'Mendes', 'Piraí']
    filtro = ((df_ranking['ranking_estadual'] <= 5) | (df_ranking['is_paracambi'] == 'Sim') | (df_ranking['municipio'].str.contains('|'.join(vizinhos), na=False)))
    df_chart = df_ranking[filtro].sort_values('nota', ascending=True)
    colors = ['#FF4B4B' if 'Paracambi' in str(x) else '#0068C9' for x in df_chart['municipio']]
    fig = px.bar(df_chart, x='nota', y='municipio', orientation='h', text='nota')
    fig.update_traces(marker_color=colors, texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_range=[0, 11], margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True)

with g2:
    st.subheader("⚠️ Classificação de Riscos")
    if df_laudo is not None and 'Gravidade' in df_laudo.columns:
        fig_pie = px.pie(df_laudo, names='Gravidade', hole=0.5, color='Gravidade', color_discrete_map={'Alta': '#FF4B4B', 'Média': '#FFA500', 'Baixa': '#00CC96', 'N/A': 'grey'})
        fig_pie.update_layout(margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

# ==========================================
# 6. LAUDO TÉCNICO (UX CARD VIEW)
# ==========================================
st.markdown("---")
st.subheader("⚖️ Laudo Técnico Detalhado (Jurídico)")

if df_laudo is not None:
    for i, row in df_laudo.iterrows():
        gravidade = row.get('Gravidade', 'N/A')
        icon = "🔴" if gravidade == "Alta" else "🟠" if gravidade == "Média" else "🔵"
        with st.expander(f"{icon} {row['Questão Original']} (Perda: {row['Pontos Perdidos']} pts)"):
            lc1, lc2 = st.columns(2)
            with lc1:
                st.markdown(f"**Risco Legal:** {row.get('Risco Legal', '-')}")
                st.caption(f"Lei: {row.get('Lei', '-')}")
            with lc2:
                st.markdown(f"**Ação Recomendada:** {row.get('Ação Recomendada', '-')}")
                st.caption(f"Ref: {row.get('Referência', '-')}")

    # ==========================================
    # BOTÃO DOWNLOAD EM PDF (NOVO)
    # ==========================================
    st.markdown("<br>", unsafe_allow_html=True)
    pdf_bytes = gerar_pdf_laudo(df_laudo)
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        st.download_button(
            label="📥 BAIXAR LAUDO TÉCNICO OFICIAL (PDF)",
            data=pdf_bytes,
            file_name="Laudo_Auditoria_Paracambi_2025.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )
else:
    st.warning("Laudo ainda não processado.")

# ==========================================
# 7. RODAPÉ REESTRUTURADO (3 COLUNAS)
# ==========================================
st.markdown('<div class="footer-container"></div>', unsafe_allow_html=True)

# Layout: 1 (Logo) | 2 (Copyright) | 1 (Social)
foot1, foot2, foot3 = st.columns([1.5, 2.5, 1.5])

with foot1:
    # Sua Logo MAIOR
    st.image(
        "https://raw.githubusercontent.com/amaro-netto/amaro-netto/a5c3e8fe0abad9646b67183153a08881a1ba2805/logos/amaronetto%20solucoes/SVG/2.0/AMARO%20NETTO%20SOLU%C3%87%C3%95ES%202.0%20BRANCO.svg", 
        width=180 
    )

with foot2:
    # Texto Centralizado
    st.markdown(
        """
        <div style="text-align: center; color: #888; font-size: 14px; margin-top: 15px;">
            © 2025 Amaro Netto Soluções.<br>
            Relatório gerado com base em dados públicos (Lei 12.527/2011).
        </div>
        """, 
        unsafe_allow_html=True
    )

with foot3:
    # Ícones Reais e Limpos (Alinhados à direita)
    st.markdown(
        """
        <div style="display: flex; justify-content: flex-end; align-items: center; gap: 15px; margin-top: 10px;">
            <div style="font-size: 12px; color: #aaa; margin-right: 5px;">Conecte-se:</div>
            <a href="https://www.linkedin.com/in/amarosilvanetto/" target="_blank" title="LinkedIn">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="24" style="filter: invert(1);">
            </a>
            <a href="https://github.com/amaro-netto" target="_blank" title="GitHub">
                <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" width="24" style="filter: invert(1);">
            </a>
        </div>
        """, 
        unsafe_allow_html=True
    )