# 🏛️ Monitor de Inteligência e Conformidade Pública (EBT + GenAI)

![Status](https://img.shields.io/badge/Status-Finalizado-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red?style=for-the-badge&logo=streamlit&logoColor=white)
![AI](https://img.shields.io/badge/AI-Google%20Gemini%202.0-orange?style=for-the-badge&logo=google&logoColor=white)

> **Objeto de Análise:** Prefeitura Municipal de Paracambi - RJ  
> **Foco:** Transparência Pública, Lei de Acesso à Informação (LAI) e Lei de Responsabilidade Fiscal (LRF).
<p>&nbsp;</p>

## 🎯 O Problema de Negócio

A transparência pública é um requisito legal e moral para municípios brasileiros. O não cumprimento da **Escala Brasil Transparente (EBT)** da CGU pode acarretar em:
* Bloqueio de verbas voluntárias.
* Multas e processos por improbidade administrativa.
* Rejeição de contas pelo TCE-RJ.

A análise manual desses portais é lenta, técnica e difícil de traduzir para gestores públicos (Prefeitos e Secretários).
<p>&nbsp;</p>

## 💡 A Solução: Auditoria Aumentada por IA

Este projeto não é apenas um dashboard de BI. Ele é um **Sistema de Suporte à Decisão** que integra:
1.  **Engenharia de Dados (ETL):** Coleta e limpeza de dados brutos da CGU.
2.  **Analytics:** Comparativo regional (Benchmarking) para identificar gaps.
3.  **IA Generativa (Google Gemini):** Um "Consultor Jurídico Virtual" que analisa cada falha detectada e gera, automaticamente:
    * O Risco Legal (Improbidade, Multa, etc.).
    * O Plano de Ação Técnico (O que a TI deve fazer).
    * A Base Legal exata (Artigo da Lei).
<p>&nbsp;</p>

## 📸 Visualização do Projeto

### 1. Painel de Controle (KPIs e Métricas)
Visualização executiva com termômetro de risco legal e comparação imediata com municípios vizinhos.
<img width="1307" height="598" alt="image" src="https://github.com/user-attachments/assets/ea4cd5b3-aa82-4b1b-8a38-3621666171d9" />


### 2. Consultoria Jurídica via IA
Ao expandir os cartões, o gestor recebe o parecer técnico gerado pelo Gemini.
<img width="1333" height="480" alt="image" src="https://github.com/user-attachments/assets/af05c939-11e7-4470-a90f-0a9bc470a15e" />
<p>&nbsp;</p>

## 🛠️ Tecnologias Utilizadas

* **Linguagem:** Python
* **ETL & Manipulação:** Pandas, NumPy
* **Inteligência Artificial:** Google Generative AI (Gemini 2.0 Flash)
* **Visualização:** Streamlit, Plotly Express, Plotly Graph Objects
* **Ambiente:** VS Code, Dotenv (Segurança de Chaves)
<p>&nbsp;</p>

## 📂 Estrutura do Projeto

```bash
rio-transparencia/
├── data/
│   ├── raw/                   # Dados brutos baixados da CGU
│   └── processed/             # Dados limpos e o Laudo gerado pela IA
├── notebooks/
│   ├── 1.0-coleta-limpeza.ipynb    # ETL dos dados da CGU
│   ├── 2.0-analise-exploratoria.ipynb
│   ├── 3.0-geracao-gaps.ipynb      # Isolamento dos erros de Paracambi
│   └── 5.0-analise-com-gemini.ipynb # A MÁGICA: Script que chama a IA
├── app.py                     # Código do Dashboard (Streamlit)
├── requirements.txt           # Dependências do projeto
├── .env                       # (Não comitado) Chaves de API
└── README.md                  # Documentação
```
<p>&nbsp;</p>

## 🚀 Como Executar Localmente

### 1. Clone o repositório
```bash
git clone https://github.com/amaro-netto/rio-transparencia.git
cd rio-transparencia
```

### 2. Instale as dependências

```
pip install -r requirements.txt
```
3. Configure a API Key
Crie um arquivo .env na raiz do projeto e adicione sua chave do Google AI Studio:

```
GEMINI_API_KEY="sua_chave_aqui"
```
4. Execute o Dashboard
```
streamlit run app.py
```
<p>&nbsp;</p>

## 📊 Resultados Alcançados

* **Automação:** Redução de dias de análise manual para segundos de processamento.
* **Acessibilidade:** Tradução de "juridiquês" para linguagem de gestão.
* **Plano de Ação:** Geração automática de checklist de correção para a equipe de TI da prefeitura.
<p>&nbsp;</p>

## 👨‍💻 Autor

<a href="https://github.com/amaro-netto" title="Amaro Netto"><img width="200" src="https://i.ibb.co/qMV0jBqM/Data-Science.webp"/></a>

---
*Este projeto utiliza dados públicos conforme a Lei de Acesso à Informação (Lei nº 12.527/2011).*
