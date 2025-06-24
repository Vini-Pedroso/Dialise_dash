import pandas as pd
import plotly.express as px
import streamlit as st
import numpy as np
from math import radians, sin, cos, sqrt, atan2

st.set_page_config(page_title="Dashboard Diálise Pediátrica - Rio Grande do Sul", layout="wide")
st.title("Dashboard Interativo: Perfil e Internação de Pacientes Pediátricos em Diálise no RS")

# === 1) CARREGAMENTO E PRÉ-PROCESSAMENTO ===

try:
    df = pd.read_csv('dados_limpos.csv', encoding='utf-8')
except FileNotFoundError:
    st.error("Arquivo 'dados_limpos.csv' não encontrado.")
    st.stop()

# Dicionários expandidos
proc_map = {
    '0305010182': 'Hemodiálise diária',
    '0305010166': 'Hemodiálise crônica',
    '0305010115': 'Diálise peritoneal automatizada (APD)',
    '0305010107': 'Diálise peritoneal ambulatorial contínua (CAPD)',
    '0305010204': 'Hemodiálise pediátrica',
    '0305010026': 'Hemodiálise (aguda)',
    '0305010042': 'Hemodiálise pediátrica (SIGTAP)',
    '0305010131': 'Diálise peritoneal pediátrica (SIGTAP)',
    '0305010140': 'Diálise peritoneal automatizada pediátrica (SIGTAP)',
    '0305010190': 'Hemodiálise pediátrica crônica (SIGTAP)'
}

gestao_map_expandido = {
    '430000': 'Estado do RS', '430210': 'Bagé', '430510': 'Canoas', '430610': 'Caxias do Sul',
    '431410': 'Novo Hamburgo', '431440': 'Passo Fundo', '431490': 'Porto Alegre',
    '430300': 'Camaquã', '430390': 'Cachoeirinha', '430770': 'Erechim', '430780': 'Estrela',
    '431140': 'Ijuí', '431340': 'Mostardas', '431680': 'Santiago', '431710': 'Santa Cruz do Sul',
    '431720': 'Santa Maria', '431800': 'São Borja', '431870': 'São Leopoldo', '432240': 'Três de Maio',
    '432250': 'Três Coroas', '432260': 'Tupanciretã'
}

condic_map = {
    'MN': 'Municipalizado', 'EP': 'Estadualizado / Estadual', 'PG': 'Gestão Plena'
}

tpups_map = {
    '05': 'Hospital Geral', '36': 'Centro de Terapia Renal Substitutiva', '39': 'Hospital Especializado'
}

tippre_map_expandido = {
    '00': 'Ambulatorial Individualizado', '30': 'Alta Complexidade', '61': 'TRS - Diálise',
    '20': 'Média Complexidade Ambulatorial', '22': 'Média Complexidade Hospitalar', '50': 'Atenção Básica'
}

sexo_map = {'M': 'Masculino', 'F': 'Feminino'}

raca_map_expandido = {
    '01': 'Branca', '02': 'Preta', '03': 'Parda', '04': 'Amarela', '05': 'Indígena', '99': 'Ignorado'
}
codigos_municipios_expandido = {
    430010: 'Aceguá',
    430047: 'Água Santa',
    430060: 'Agudo',
    430063: 'Ajuricaba',
    430087: 'Alecrim',
    430040: 'Alegrete',
    430110: 'Alegrete',
    430120: 'Alpestre',
    430160: 'Alto Alegre',
    430170: 'Alto Feliz',
    430190: 'Alvorada',
    430235: 'Amaral Ferrador',
    430240: 'Ametista do Sul',
    430260: 'André da Rocha',
    430320: 'Antônio Prado',
    430350: 'Arambaré',
    430420: 'Arroio do Meio',
    430440: 'Arroio do Sal',
    430463: 'Arroio do Tigre',
    430466: 'Arroio dos Ratos',
    430470: 'Arroio Grande',
    250180: 'Areial - PB',
    110007: 'Ariquemes - RO',
    430517: 'Augusto Pestana',
    430210: 'Bagé',
    420190: 'Balneário Camboriú - SC',
    150680: 'Belém - PA',
    311190: 'Belo Horizonte - MG',
    420240: 'Blumenau - SC',
    530010: 'Brasília - DF',
    530040: 'Brasília - DF',
    530180: 'Brasília - DF',
    430280: 'Cacequi',
    110010: 'Cacoal - RO',
    430300: 'Camaquã',
    430310: 'Camargo',
    430450: 'Campo Bom',
    500060: 'Campo Grande - MS',
    430460: 'Canoas',
    110012: 'Cerejeiras - RO',
    110013: 'Colorado do Oeste - RO',
    420460: 'Criciúma - SC',
    120030: 'Cruzeiro do Sul - AC',
    430570: 'Cruz Alta',
    410580: 'Curitiba - PR',
    430655: 'Dom Pedrito',
    430660: 'Dilermando de Aguiar',
    430676: 'Dois Irmãos das Missões',
    430700: 'Eldorado do Sul',
    430720: 'Encantado',
    430750: 'Encruzilhada do Sul',
    430755: 'Erebango',
    430760: 'Erechim',
    120035: 'Epitaciolândia - AC',
    250535: 'Esperança - PB',
    430790: 'Espumoso',
    430840: 'Fagundes Varela',
    430850: 'Farroupilha',
    120040: 'Feijó - AC',
    420540: 'Florianópolis - SC',
    430890: 'Fontoura Xavier',
    430910: 'Formigueiro',
    430920: 'Fortaleza dos Valos',
    430930: 'Frederico Westphalen',
    430950: 'Garibaldi',
    430960: 'Garruchos',
    430975: 'Gentil',
    431000: 'Giruá',
    431020: 'Glorinha',
    521250: 'Goiânia - GO',
    431033: 'Gramado',
    431041: 'Gramado dos Loureiros',
    431085: 'Gravataí',
    110020: 'Guajará-Mirim - RO',
    351440: 'Guarulhos - SP',
    431100: 'Guaporé',
    431110: 'Guarani das Missões',
    431115: 'Harmonia',
    431120: 'Herval',
    431213: 'Horizontina',
    431242: 'Humaitá',
    431250: 'Ibarama',
    431140: 'Ijuí',
    431330: 'Imbe',
    431337: 'Independência',
    431370: 'Ipiranga do Sul',
    431395: 'Itaíba',
    420710: 'Itajaí - SC',
    420770: 'Itajaí - SC',
    250750: 'Itabaiana - PB',
    250770: 'Itaporanga - PB',
    431405: 'Itapuca',
    431390: 'Itacurubi',
    431446: 'Ivoti',
    431454: 'Jaboticaba',
    431460: 'Jacuizinho',
    110028: 'Jaru - RO',
    431500: 'Jari',
    110032: 'Ji-Paraná - RO',
    420820: 'Joinville - SC',
    431530: 'Júlio de Castilhos',
    420910: 'Lages - SC',
    431570: 'Lagoa Bonita do Sul',
    431180: 'Lajeado',
    431600: 'Lavras do Sul',
    431640: 'Liberato Salzano',
    160030: 'Macapá - AP',
    431750: 'Machadinho',
    251150: 'Mamanguape - PB',
    130260: 'Manaus - AM',
    431820: 'Marcelino Ramos',
    431225: 'Marau',
    421370: 'Pinhalzinho - SC',
    251230: 'Pocinhos - PB',
    431490: 'Porto Alegre',
    110001: 'Porto Velho - RO',
    431550: 'Restinga Seca',
    431560: 'Rio Grande',
    421480: 'Rio do Sul - SC',
    110140: 'Rolim de Moura - RO',
    291955: 'Salvador - BA',
    431720: 'Santa Maria',
    431700: 'Santa Cruz do Sul',
    251420: 'Santa Rita - PB',
    431630: 'Santa Rosa',
    160060: 'Santana - AP',
    431680: 'Santiago',
    431690: 'Santo Ângelo',
    355030: 'São Paulo - SP',
    431870: 'São Leopoldo',
    431890: 'São Lourenço do Sul',
    210530: 'São Luís - MA',
    251600: 'Sousa - PB',
    431960: 'Taquara',
    432240: 'Três de Maio',
    432250: 'Três Coroas',
    432220: 'Três Passos',
    432260: 'Tupanciretã',
    432270: 'Uruguaiana',
    522185: 'Valparaíso de Goiás - GO',
    432290: 'Veranópolis',
    432300: 'Viamão',
    345: 'Vila Flores',
    110170: 'Vilhena - RO'
}

unidade_map_expandido = {
    '2223546': 'Centro de Hemodiálise - Canoas',
    '2242400': 'Centro de Hemodiálise - RS',
    '2266539': 'Centro de Hemodiálise - RS',
    '2233304': 'Centro de Especialidades - RS',
    '2227290': 'Centro de Saúde - Região Metropolitana',
    '2707829': 'Centro Especializado - Região Sul',
    '2248204': 'Centro Médico - RS',
    '2232022': 'Centro Médico Especializado - RS',
    '2262770': 'Centro de Nefrologia - RS',
    '2228602': 'Hospital Regional - Interior RS',
    '2236370': 'Hospital Geral - Interior RS',
    '2241048': 'Hospital Regional - Passo Fundo',
    '2253054': 'Hospital Regional - Santa Rosa',
    '2231042': 'Hospital Comunitário - RS',
    '2248298': 'Hospital Comunitário - Interior',
    '2262568': 'Santa Casa de Caridade de Bagé',
    '2262509': 'Hospital de Caridade de Alegrete',
    '2244306': 'Hospital de Caridade de Ijuí',
    '2237253': 'Hospital de Clínicas de Porto Alegre (HCPA)',
    '2247984': 'Hospital Geral de Caxias do Sul',
    '2232995': 'Hospital Filantrópico - RS',
    '2262584': 'Hospital Filantrópico - Bagé',
    '2246929': 'Hospital Especializado - Novo Hamburgo',
    '2223538': 'Hospital Universitário – Canoas',
    '2247771': 'Hospital Privado - RS',
    '2241021': 'Hospital São Vicente de Paulo – Passo Fundo',
    '2263858': 'Hospital Municipal – Bagé',
    '2261057': 'Hospital Municipal - Interior',
    '2246988': 'Hospital Regina – Novo Hamburgo',
    '2253046': 'Hospital Vida e Saúde – Santa Rosa',
    '2237571': 'Centro de Tratamento Renal - RS',
    '2839938': 'Centro de Tratamento Renal - Outros Estados',
    '2252287': 'Centro de Saúde Renal - RS',
    '2237164': 'Clínica de Diálise - Porto Alegre',
    '2707918': 'Clínica de Diálise - Região Sul',
    '2247429': 'Clínica Renal - RS',
    '2262460': 'Clínica Renal - Alegrete',
    '2231069': 'Clínica Nefrológica - RS',
    '2247968': 'Clínica Nefrológica - Caxias do Sul',
    '2252295': 'Clínica de Nefrologia - RS',
    '2248239': 'Clínica Especializada - RS',
    '2229706': 'Clínica Especializada - RS',
    '2256029': 'Clínica de Hemodiálise - RS',
    '2247488': 'Centro de Diálise - Caxias do Sul',
    '2230577': 'Centro de Diálise - RS',
    '2261898': 'Centro de Diálise - Bagé',
    '2242397': 'Unidade de Nefrologia - RS',
    '2232030': 'Unidade de Terapia Renal - RS',
    '2248220': 'Unidade de Hemodiálise - RS',
    '2226952': 'Unidade de Saúde - Região Norte RS',
    '2701146': 'Unidade de Saúde - Região Sul',
    '2266474': 'Unidade de Saúde Especializada - RS',
    '2255456': 'Unidade Especializada - RS',
    '2254611': 'Centro de Tratamento - RS',
    '3564150': 'Hospital/Clínica - São Paulo',
    '2237601': 'Santa Casa de Misericórdia de Porto Alegre'
}

# Função para classificar idade
def classificar_idade(idade):
    if idade < 1:
        return 'Lactente (< 1 ano)'
    elif idade < 2:
        return 'Primeira infância (1-2 anos)'
    elif idade < 6:
        return 'Pré-escolar (2-6 anos)'
    elif idade < 12:
        return 'Escolar (6-12 anos)'
    elif idade < 18:
        return 'Adolescente (12-18 anos)'
    else:
        return 'Adulto (≥ 18 anos)'

# Aplicar mapeamentos
df['AP_PRIPAL_str'] = df['AP_PRIPAL'].astype(str).str.zfill(10)
df['AP_CODUNI_str'] = df['AP_CODUNI'].astype(str).str.zfill(7)
df['AP_GESTAO_str'] = df['AP_GESTAO'].astype(str).str.zfill(6)
df['AP_CONDIC_str'] = df['AP_CONDIC'].astype(str)
df['AP_TPUPS_str'] = df['AP_TPUPS'].astype(str).str.zfill(2)
df['AP_TIPPRE_str'] = df['AP_TIPPRE'].astype(str).str.zfill(2)
df['AP_RACACOR_str'] = df['AP_RACACOR'].astype(str).str.zfill(2)
df['AP_UFMUN_int'] = df['AP_UFMUN'].astype(int)
df['AP_MUNPCN_int'] = df['AP_MUNPCN'].astype(int)

df['procedimento_nome'] = df['AP_PRIPAL_str'].map(proc_map).fillna('Desconhecido')
df['unidade_nome'] = df['AP_CODUNI_str'].map(unidade_map_expandido).fillna('Desconhecido')
df['gestao_desc'] = df['AP_GESTAO_str'].map(gestao_map_expandido).fillna('Outro')
df['condicao_desc'] = df['AP_CONDIC_str'].map(condic_map).fillna('Outro')
df['tpups_desc'] = df['AP_TPUPS_str'].map(tpups_map).fillna('Outro')
df['tippre_desc'] = df['AP_TIPPRE_str'].map(tippre_map_expandido).fillna('Outro')
df['sexo_desc'] = df['AP_SEXO'].map(sexo_map).fillna('Ignorado')
df['raca_desc'] = df['AP_RACACOR_str'].map(raca_map_expandido).fillna('Ignorado')
df['municipio'] = df['AP_UFMUN_int'].map(codigos_municipios_expandido).fillna('Outro')
df['municipio_origem'] = df['AP_MUNPCN_int'].map(codigos_municipios_expandido).fillna('Outro')

if 'AP_NUIDADE' in df.columns:
    df['faixa_etaria'] = df['AP_NUIDADE'].apply(classificar_idade)

df['estado_origem'] = df['AP_MUNPCN_int'].astype(str).str[:2].map({
    '11': 'RO', '12': 'AC', '13': 'AM', '14': 'RR', '15': 'PA', '16': 'AP', '17': 'TO',
    '21': 'MA', '22': 'PI', '23': 'CE', '24': 'RN', '25': 'PB', '26': 'PE', '27': 'AL',
    '28': 'SE', '29': 'BA', '31': 'MG', '32': 'ES', '33': 'RJ', '35': 'SP', '41': 'PR',
    '42': 'SC', '43': 'RS', '50': 'MS', '51': 'MT', '52': 'GO', '53': 'DF'
}).fillna('Outro')

procedimentos_dialise = ['0305010182', '0305010166', '0305010115', '0305010107']  # Alinhar com proc_map
df_pediatrico = df[
    (df['AP_NUIDADE'].notna()) & (df['AP_NUIDADE'] < 18) &
    (df['AP_PRIPAL_str'].str.contains('|'.join(procedimentos_dialise), na=False)) &
    (df['estado_origem'] == 'RS')
].copy()

if df_pediatrico.empty:
    st.warning("Nenhum paciente pediátrico encontrado com os filtros iniciais. Relaxando filtros...")
    st.write("Valores únicos de AP_PRIPAL_str no dataset original:", df['AP_PRIPAL_str'].unique())
    df_pediatrico = df[
        (df['AP_NUIDADE'].notna()) & (df['AP_NUIDADE'] < 18) &
        (df['estado_origem'] == 'RS')
    ].copy()
    if df_pediatrico.empty:
        st.error("Ainda assim não há dados disponíveis.")
        st.stop()

st.sidebar.subheader("Filtros do Dashboard")
ano_sel = st.sidebar.multiselect("Ano", sorted(df_pediatrico['ANO'].dropna().astype(str).unique()), default=None)
#uni_sel = st.sidebar.multiselect("Unidade de Saúde", df_pediatrico['unidade_nome'].unique(), default=None)
uni_sel = st.sidebar.multiselect("Unidade de Saúde", sorted(df_pediatrico['unidade_nome'].unique()), default=None)
faixa_sel = st.sidebar.multiselect("Faixa Etária", df_pediatrico['faixa_etaria'].unique(), default=None)
#mun_ori_sel = st.sidebar.multiselect("Município de Origem", df_pediatrico['municipio_origem'].unique(), default=None)
mun_ori_sel = st.sidebar.multiselect("Município de Origem", sorted(df_pediatrico['municipio_origem'].unique()), default=None)


dff = df_pediatrico.copy()
if ano_sel: dff = dff[dff['ANO'].astype(str).isin(ano_sel)]
if uni_sel: dff = dff[dff['unidade_nome'].isin(uni_sel)]
if faixa_sel: dff = dff[dff['faixa_etaria'].isin(faixa_sel)]
if mun_ori_sel: dff = dff[dff['municipio_origem'].isin(mun_ori_sel)]

if dff.empty:
    st.warning("Sem dados para os filtros selecionados.")
    st.stop()

tab1, tab2, tab3 = st.tabs(["Visão Geral", "Análises Detalhadas", "Distribuição"])
with tab1:
    # 1. Gráfico de barras por unidade
    st.subheader("🏥 Distribuição por Unidade de Saúde")
    df_unidades = dff.groupby('unidade_nome').size().reset_index(name='contagem')
    if not df_unidades.empty:
        fig_barras = px.bar(
            df_unidades.sort_values("contagem", ascending=True),
            x='contagem', y='unidade_nome',
            orientation='h',
            title="Pacientes por Unidade de Saúde"
        )
        st.plotly_chart(fig_barras, use_container_width=True)
    else:
        st.warning("Nenhum dado disponível para unidades de saúde.")

    # 2. Gráfico de barras por faixa etária e sexo
    st.subheader("👶 Distribuição por Faixa Etária e Sexo")
    fig_barra = px.histogram(dff, x='faixa_etaria', color='sexo_desc', barmode='group')
    st.plotly_chart(fig_barra, use_container_width=True)

    # 3. Treemap por gestão e raça
    st.subheader("🧬 Gestão e Raça/Cor")
    fig_tree = px.treemap(dff, path=['gestao_desc', 'raca_desc'])
    st.plotly_chart(fig_tree, use_container_width=True)

with tab2:
    # 4. Total de Internações por Ano e Local
    st.subheader("📊 Total de Internações por Ano e Local")
    # Ajuste para AP_TPATEN == 10 (assumindo que 10 pode indicar algo; caso contrário, usar presença de dados)
    dff['internado'] = dff['AP_TPATEN'] == 10  # Testar se 10 indica internação
    
    # Agrupar apenas por ANO e unidade_nome (removendo faixa_etaria) - CONTAGEM
    df_internacao = dff.groupby(['ANO', 'unidade_nome'])['internado'].sum().reset_index(name='total_internacoes')
    
    if not df_internacao.empty:
        fig_internacao = px.bar(
            df_internacao,
            x='ANO',
            y='total_internacoes',
            color='unidade_nome',  # Apenas cores por unidade, sem padrões
            title="Total de Internações por Ano e Local no RS"
        )
        fig_internacao.update_layout(
            showlegend=True,
            margin=dict(l=50, r=50, t=50, b=50),
            xaxis_title="Ano",
            yaxis_title="Total de Internações"
        )
        st.plotly_chart(fig_internacao, use_container_width=True)
    else:
        st.warning("Nenhum dado para total de internações no RS. Verifique o significado de AP_TPATEN (valor 10).")
    
    # 6. Perfil dos Pacientes por Unidade
    st.subheader("📊 Perfil dos Pacientes por Unidade")
    df_perfil = dff.groupby(['unidade_nome', 'sexo_desc', 'raca_desc']).size().reset_index(name='contagem')
    if not df_perfil.empty:
        fig_perfil = px.bar(
            df_perfil,
            x='contagem',
            y='unidade_nome',
            color='raca_desc',
            orientation='h',
            title="Perfil dos Pacientes no RS",
            barmode='stack'
        )
        st.plotly_chart(fig_perfil, use_container_width=True)
    else:
        st.warning("Nenhum dado para perfil dos pacientes no RS. Verifique as colunas sexo_desc e raca_desc.")

with tab3:
    # 8. Proporção de Hemodiálise vs. Diálise Peritoneal
    st.subheader("📉 Proporção de Hemodiálise vs. Diálise Peritoneal")
    df_dialise = dff.copy()
    df_dialise['tipo_dialise'] = df_dialise['AP_PRIPAL_str'].map({
        '0305010182': 'Hemodiálise', '0305010166': 'Hemodiálise', '0305010115': 'Diálise Peritoneal',
        '0305010107': 'Diálise Peritoneal'
    }).fillna('Outro')
    df_dialise = df_dialise[df_dialise['tipo_dialise'] != 'Outro']  # Filtrar apenas diálise
    df_dialise_agg = df_dialise.groupby(['ANO', 'tipo_dialise']).size().reset_index(name='contagem')
    if not df_dialise_agg.empty:
        fig_area = px.area(df_dialise_agg, x='ANO', y='contagem', color='tipo_dialise', title="Proporção no RS")
        st.plotly_chart(fig_area, use_container_width=True)
    else:
        st.warning("Nenhum dado para tipos de diálise no RS. Verifique a coluna AP_PRIPAL_str e os códigos de diálise no dataset.")

    # 9. Prevalência por Estado de Origem
    st.subheader("🌞 Prevalência por Estado de Origem")
    df_estado = dff.groupby('municipio_origem').size().reset_index(name='contagem')
    if not df_estado.empty:
        fig_barras_estado = px.bar(
            df_estado,
            x='municipio_origem',
            y='contagem',
            title="Prevalência por Município de Origem no RS"
        )
        fig_barras_estado.update_layout(xaxis={'tickangle': 45})  # Rotacionar rótulos
        st.plotly_chart(fig_barras_estado, use_container_width=True)
    else:
        st.warning("Nenhum dado para origem dos pacientes no RS. Verifique a coluna municipio_origem.")

    # 10. Idade por Tipo de Diálise
    st.subheader("🎻 Idade por Tipo de Diálise")
    df_violin = df_dialise.dropna(subset=['AP_NUIDADE', 'tipo_dialise'])
    # Depuração: Mostrar valores únicos de AP_NUIDADE
    #st.write("Valores únicos de AP_NUIDADE no dff:", df_violin['AP_NUIDADE'].unique())
    if not df_violin.empty:
        fig_violin = px.violin(df_violin, x='tipo_dialise', y='AP_NUIDADE', box=True, color='tipo_dialise', title="Idade no RS")
        st.plotly_chart(fig_violin, use_container_width=True)
    else:
        st.warning("Nenhum dado para tipo de diálise e idade no RS. Verifique as colunas AP_NUIDADE e AP_PRIPAL_str.")
