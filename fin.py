import streamlit as st
import pandas as pd
import openpyxl




page_bg_img = """
<style>
/* Fundo principal */
[data-testid="stAppViewContainer"] {
    background-color: #889b9e !important;
}

/* Barra lateral */
[data-testid="stSidebar"] {
    background-color: #003147 !important; /* Fundo azul escuro */
    color: white !important;             /* Texto branco */
}
[data-testid="stSidebar"] .css-1n76uvr a,
[data-testid="stSidebar"] .css-1n76uvr span {
    color: white !important;             /* Texto branco */
    font-weight: bold !important;        /* Negrito */
}
[data-testid="stSidebar"] > div:first-child {
    padding: 10px;
    border-bottom: 2px solid #fff;       /* Linha de separação */
}

/* Expanders */
[data-testid="stExpander"] {
    border: 2px solid black !important;
    border-radius: 8px !important;
    margin-bottom: 20px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}
[data-testid="stExpander"] summary {
    font-size: 20px !important;
    font-weight: bold !important;
    color: white !important;
    background-color: #003147 !important;
    padding: 10px !important;
}
[data-testid="stExpanderDetails"] {
    padding: 15px !important;
    font-size: 14px !important;
    background-color: #f9f9f9 !important;
    border-radius: 0 0 6px 6px !important;
}

/* Botões personalizados */
button[kind="secondary"] {
    background-color: #003147 !important;
    color: white !important;
    border: 2px solid #003147 !important;
    border-radius: 6px !important;
    font-weight: bold;
    padding: 10px 20px;
    transition: background-color 0.3s ease;
}

/* Tabelas */
.custom-table {
    border: 2px solid #003147;
    border-radius: 10px;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
}
.custom-table th {
    background-color: #003147;
    color: white;
    font-weight: bold;
}
.custom-table td {
    background-color: #f9f9f9;
    color: black;
}

/* Cabeçalho */
[data-testid="stHeader"] {
    background: none !important;
}

/* Tabs */
div[data-testid="stHorizontalBlock"] div[role="tablist"] > div {
    background-color: #003147 !important;
    color: white !important;
    border-radius: 5px;
    padding: 10px;
    margin-right: 5px;
}
div[data-testid="stHorizontalBlock"] div[role="tablist"] > div[aria-selected="true"] {
    background-color: #005f6b !important;
    font-weight: bold;
}
/* Estilo para os rótulos (labels) dos widgets */
label {
    color: white !important; /* Define a cor branca para todos os labels */
    font-weight: bold;       /* Adiciona negrito, opcional */
    font-size: 14px;         /* Ajusta o tamanho da fonte, opcional */
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

def editor_dataframe_contas(df, tipo_conta):
    if tipo_conta == "pagar":
        df_display = df.rename(columns={
            'Fornecedor': 'Fornecedor',
            'Vencimento': 'Data de Vencimento',
            'Descrição': 'Descrição',
            'R$ Valor': 'Valor (R$)',
            'Plano Contas': 'Plano de Contas',
            'Situação': 'Situação'
        })
        columns_order = ['Fornecedor', 'Data de Vencimento', 'Descrição', 'Valor (R$)', 'Plano de Contas', 'Situação']
    elif tipo_conta == "receber":
        df_display = df.rename(columns={
            'Cliente': 'Cliente',
            'Vencimento': 'Data de Vencimento',
            'Descrição': 'Descrição',
            'R$ Valor': 'Valor (R$)',
            'Status': 'Status'
        })
        columns_order = ['Cliente', 'Data de Vencimento', 'Descrição', 'Valor (R$)', 'Status']
    
    df_display = df_display[columns_order]

    df_display['Valor (R$)'] = df_display['Valor (R$)'].apply(lambda x: f"R$ {x:,.2f}")
    df_html = df_display.to_html(classes='custom-table', index=False)
    st.markdown(df_html, unsafe_allow_html=True)
   
st.markdown("""
<style>

/* Estilo do título principal */
.main-header {
    text-align: center;
    background-color: #1b262e;
    color: white;
    padding: 0px 0;
    border-radius: 12px;
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.2);
    font-size: 2rem;
    text-transform: uppercase;
    letter-spacing: 4px;
    margin-bottom: 30px;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
/* Estilo específico para o título do selectbox */
.sidebar-title {
    font-size: 20px;
    font-weight: bold;
    color: #1b262e;
    background-color: #f9f9f9;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# Mapeamento dos dias da semana em português
weekday_mapping = {
    'Monday': 'Segunda-feira',
    'Tuesday': 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday': 'Quinta-feira',
    'Friday': 'Sexta-feira',
    'Saturday': 'Sábado',
    'Sunday': 'Domingo'
}
def convert_to_float(value):
    # Verificar se o valor é do tipo string
    if isinstance(value, str):
        # Remover o símbolo 'R$' e trocar a vírgula para ponto para o decimal
        value = value.replace('R$ ', '').replace('.', '').replace(',', '.')
    return float(value)

# Função para ajustar a data de vencimento
def adjust_due_date(date):
    if date.weekday() == 5:  # Sábado
        return date + pd.Timedelta(days=2)
    elif date.weekday() == 6:  # Domingo
        return date + pd.Timedelta(days=1)
    else:
        return date

# Criação das colunas para upload de arquivos
col1, col2 = st.columns(2)
col11, col12 = st.columns(2)
col111, col112 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader("Carregue o arquivo Contas a Pagar", type=["xlsx"])
with col2:
    uploaded_file2 = st.file_uploader("Carregue o arquivo Contas a Receber", type=["xlsx"])

# Carregar e exibir os dados se o arquivo for carregado
if uploaded_file is not None:
    df1 = pd.read_excel(uploaded_file)
    df1['Vencimento'] = pd.to_datetime(df1['Vencimento'], errors='coerce')
    df1['Vencimento'] = df1['Vencimento'].dt.strftime('%d/%m/%Y')
    df1['Dia da Semana'] = pd.to_datetime(df1['Vencimento'], errors='coerce').dt.day_name().map(weekday_mapping)
    df1['Pag Oficial'] = df1['Vencimento'].apply(lambda x: adjust_due_date(pd.to_datetime(x, format='%d/%m/%Y')).strftime('%d/%m/%Y'))
    df1['R$ Valor'] = pd.to_numeric(df1['R$ Valor'], errors='coerce')

if uploaded_file2 is not None:
    df2 = pd.read_excel(uploaded_file2)
    df2['Vencimento'] = pd.to_datetime(df2['Vencimento'], errors='coerce')
    df2['Vencimento'] = df2['Vencimento'].dt.strftime('%d/%m/%Y')
    df2['Dia da Semana'] = pd.to_datetime(df2['Vencimento'], errors='coerce').dt.day_name().map(weekday_mapping)
    df2['Pag Oficial'] = df2['Vencimento'].apply(lambda x: adjust_due_date(pd.to_datetime(x, format='%d/%m/%Y')).strftime('%d/%m/%Y'))
    df2['R$ Valor'] = pd.to_numeric(df2['R$ Valor'], errors='coerce')

# Sidebar: Filtro de Empresas
if uploaded_file is not None and uploaded_file2 is not None:
    empresas_pagar = df1['Empresa'].unique().tolist()
    empresas_receber = df2['Empresa'].unique().tolist()
    todas_empresas = list(set(empresas_pagar + empresas_receber))
    # Criando o título estilizado acima do selectbox
    st.sidebar.markdown('<div class="sidebar-title">FILTROS</div>', unsafe_allow_html=True)

    # O selectbox funcional, sem o texto padrão
    empresa_selecionada = st.sidebar.selectbox("Selecione uma Empresa", todas_empresas)

    data_inicio = st.sidebar.date_input("Data Início", min_value=pd.to_datetime(df1['Pag Oficial']).min(), max_value=pd.to_datetime(df1['Pag Oficial']).max())
    data_fim = st.sidebar.date_input("Data Fim", min_value=pd.to_datetime(df1['Pag Oficial']).min(), max_value=pd.to_datetime(df1['Pag Oficial']).max())

    # Filtro de Status para Contas a Pagar
    situacao_selecionada = st.sidebar.multiselect(
        "Filtrar por Situação (Contas a Pagar)", 
        options=["ABERTO", "PAGO", "CANCELADO"], 
        default=["ABERTO", "PAGO", "CANCELADO"]
    )
    
    # Filtro de Status para Contas a Receber
    status_selecionado = st.sidebar.multiselect(
        "Filtrar por Status (Contas a Receber)", 
        options=["   Previsão", "   Aberto", "   Atrasado", "   Pago"], 
        default=["   Previsão", "   Aberto", "   Atrasado", "   Pago"]
    )

    df1_filtered = df1[df1['Empresa'] == empresa_selecionada]
    df2_filtered = df2[df2['Empresa'] == empresa_selecionada]

    df1_filtered['Pag Oficial'] = pd.to_datetime(df1_filtered['Pag Oficial'], format='%d/%m/%Y')
    df2_filtered['Pag Oficial'] = pd.to_datetime(df2_filtered['Pag Oficial'], format='%d/%m/%Y')

    df1_filtered = df1_filtered[
        (df1_filtered['Pag Oficial'] >= pd.to_datetime(data_inicio)) & 
        (df1_filtered['Pag Oficial'] <= pd.to_datetime(data_fim)) &
        (df1_filtered['Situação'].isin(situacao_selecionada))
    ]
    df2_filtered = df2_filtered[
        (df2_filtered['Pag Oficial'] >= pd.to_datetime(data_inicio)) & 
        (df2_filtered['Pag Oficial'] <= pd.to_datetime(data_fim)) &
        (df2_filtered['Status'].isin(status_selecionado))
    ]

    with col111:
        st.markdown('<div class="main-header">Contas a Pagar</div>', unsafe_allow_html=True)
        df1_filtered_display = df1_filtered[['Fornecedor', 'Vencimento', 'Descrição', 'R$ Valor', 'Plano Contas', 'Situação']]
        st.dataframe(df1_filtered_display, hide_index=True,use_container_width=True)
    with col112:
        st.markdown('<div class="main-header">Contas a Receber</div>', unsafe_allow_html=True)
        # Selecionar as colunas específicas para exibição
        df2_filtered_display = df2_filtered[['Cliente', 'Vencimento', 'Descrição', 'R$ Valor', 'Status']]
        st.dataframe(df2_filtered_display, hide_index=True, use_container_width=True)

# Ajustando o cálculo da diferença entre 'Receber' e 'Pagar' por dia
if uploaded_file is not None and uploaded_file2 is not None:
    df1_summary = df1_filtered.groupby('Pag Oficial')['R$ Valor'].sum().reset_index()
    df1_summary = df1_summary.rename(columns={'R$ Valor': 'Pagar'})
    
    df2_summary = df2_filtered.groupby('Pag Oficial')['R$ Valor'].sum().reset_index()
    df2_summary = df2_summary.rename(columns={'R$ Valor': 'Receber'})
    
    merged_summary = pd.merge(df1_summary, df2_summary, on='Pag Oficial', how='outer')
    merged_summary = merged_summary.fillna(0)
    
    merged_summary['Pag Oficial'] = pd.to_datetime(merged_summary['Pag Oficial'], format='%d/%m/%Y')
    merged_summary = merged_summary.sort_values(by='Pag Oficial')
    
    # Convertendo os valores de 'Pagar' e 'Receber' corretamente
    merged_summary['Pagar'] = merged_summary['Pagar'].apply(lambda x: convert_to_float(x))
    merged_summary['Receber'] = merged_summary['Receber'].apply(lambda x: convert_to_float(x))

    # Calculando a diferença entre 'Receber' e 'Pagar'
    merged_summary['A Receber - A Pagar por Dia'] = merged_summary['Receber'] - merged_summary['Pagar']
    
    # Formatando a coluna de diferença corretamente
    merged_summary['A Receber - A Pagar por Dia'] = merged_summary['A Receber - A Pagar por Dia'].apply(lambda x: f'R$ {x:,.2f}')

    merged_summary['Pag Oficial'] = merged_summary['Pag Oficial'].dt.strftime('%d/%m/%Y')

    with col11:  # Correção: Usando a primeira coluna de col11
        st.markdown('<div class="main-header">Resumo - Receber e Pagar</div>', unsafe_allow_html=True)
        
        st.dataframe(merged_summary, hide_index=True, use_container_width=True)

if uploaded_file2 is not None:
    # Agrupar as contas a receber por 'Forma de Cobrança' e somar os valores
    df2_payment_summary = df2_filtered.groupby('Forma Cobrança')['R$ Valor'].sum().reset_index()
    df2_payment_summary = df2_payment_summary.rename(columns={'R$ Valor': 'Total'})
    
    # Formatar os valores como moeda
    df2_payment_summary['Total'] = df2_payment_summary['Total'].apply(lambda x: f'R$ {x:,.2f}')
    
    with col12:
        # Exibir a tabela das formas de pagamento ao lado da tabela de 'Contas a Receber'
        st.markdown('<div class="main-header">Resumo - Formas de Pagamento</div>', unsafe_allow_html=True)
        st.dataframe(df2_payment_summary, hide_index=True, use_container_width=True)


