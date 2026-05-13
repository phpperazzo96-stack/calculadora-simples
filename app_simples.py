import streamlit as st

# 1. Configuração da Página com Favicon (Ícone da Aba do Navegador)
st.set_page_config(
    page_title="Calculadora Fiscal | We Balance",
    page_icon="📊",
    layout="centered",
)

# 2. Inserir a Logo no Topo
# Certifique-se de salvar o arquivo 'logo.png' na mesma pasta do script
try:
    st.image("logo.png", width=200)
except FileNotFoundError:
    # Caso a imagem não exista ainda, exibe um placeholder profissional
    st.markdown("### 🏢 **We Balance**")

st.title("Calculadora Oficial do Simples Nacional")
st.markdown(
    "*Desenvolvido por [We Balance](https://seu-site.com.br) - Planejamento Fiscal Inteligente*"
)
st.markdown("---")

import streamlit as st

st.set_page_config(page_title="Simples Nacional Completo", layout="centered")
st.title("📊 Calculadora Oficial do Simples Nacional")
st.subheader("Cálculo com Alíquotas Efetivas e Planejamento do Fator R")

# --- 1. ENTRADA DE DADOS ---
cnae = st.text_input("Digite o CNAE da empresa:", placeholder="Ex: 6201-5/00")

tipo_atividade = st.selectbox(
    "Selecione o tipo de atividade deste CNAE:",
    ["Comércio (Anexo I)", "Serviços Gerais (Anexo III)", "Serviços com Fator R (Anexo III ou V)"]
)

faturamento = st.number_input("Renda Bruta Anual (Últimos 12 meses):", min_value=0.0, format="%.2f")
folha_salarial = st.number_input("Folha Salarial Anual Atual (Últimos 12 meses):", min_value=0.0, format="%.2f")

# --- 2. TABELAS OFICIAIS DO SIMPLES NACIONAL ---
TABELA_ANEXO_I = [
    (180000.00, 0.04, 0.00),
    (360000.00, 0.073, 5940.00),
    (720000.00, 0.095, 13860.00),
    (1800000.00, 0.107, 22500.00),
    (3600000.00, 0.143, 87300.00),
    (4800000.00, 0.19, 256500.00)
]

TABELA_ANEXO_III = [
    (180000.00, 0.06, 0.00),
    (360000.00, 0.112, 9360.00),
    (720000.00, 0.135, 17640.00),
    (1800000.00, 0.16, 35640.00),
    (3600000.00, 0.21, 125640.00),
    (4800000.00, 0.33, 558000.00)
]

TABELA_ANEXO_V = [
    (180000.00, 0.155, 0.00),
    (360000.00, 0.18, 4500.00),
    (720000.00, 0.195, 9900.00),
    (1800000.00, 0.205, 17100.00),
    (3600000.00, 0.23, 62100.00),
    (4800000.00, 0.305, 332100.00)
]

def descobrir_faixa_e_calcular(faturamento, tabela):
    for limite, aliquota_nom, deducao in tabela:
        if faturamento <= limite:
            aliquota_efetiva = ((faturamento * aliquota_nom) - deducao) / faturamento
            return aliquota_efetiva, aliquota_nom, deducao
    return None, None, None

# --- 3. PROCESSAMENTO DO CÁLCULO ---
if st.button("Calcular Alíquota Efetiva Real"):
    if faturamento > 0:
        if faturamento > 4800000.00:
            st.error("❌ Erro: O faturamento informado ultrapassa o limite máximo de R$ 4.800.000,00.")
        else:
            fator_r = 0.0
            tabela_escolhida = []
            nome_anexo = ""

            if tipo_atividade == "Comércio (Anexo I)":
                tabela_escolhida = TABELA_ANEXO_I
                nome_anexo = "Anexo I (Comércio)"
            elif tipo_atividade == "Serviços Gerais (Anexo III)":
                tabela_escolhida = TABELA_ANEXO_III
                nome_anexo = "Anexo III (Serviços)"
            elif tipo_atividade == "Serviços com Fator R (Anexo III ou V)":
                fator_r = folha_salarial / faturamento
                if fator_r >= 0.28:
                    tabela_escolhida = TABELA_ANEXO_III
                    nome_anexo = "Anexo III (Fator R - Reduzido)"
                else:
                    tabela_escolhida = TABELA_ANEXO_V
                    nome_anexo = "Anexo V (Fator R - Majorado)"

            aliquota_efetiva, aliq_nominal, deducao = descobrir_faixa_e_calcular(faturamento, tabela_escolhida)

            if aliquota_efetiva is not None:
                st.success("🎯 Análise de Enquadramento Concluída!")
                
                # Exibição dos cards principais
                col1, col2, col3 = st.columns(3)
                col1.metric("Enquadramento", nome_anexo)
                col2.metric("Alíquota Nominal", f"{aliq_nominal * 100:.2f}%")
                col3.metric("Alíquota Efetiva Real", f"{aliquota_efetiva * 100:.2f}%")
                
                # --- BLOCO DE PLANEJAMENTO FISCAL (FATOR R) ---
                if tipo_atividade == "Serviços com Fator R (Anexo III ou V)":
                    st.markdown("---")
                    st.subheader("💡 Planejamento de Pró-Labore / Folha")
                    
                    folha_alvo_anual = faturamento * 0.28
                    folha_alvo_mensal = folha_alvo_anual / 12
                    
                    if fator_r < 0.28:
                        # Descobre quanto falta no ano e divide por 12 meses
                        falta_anual = folha_alvo_anual - folha_salarial
                        pro_labore_sugerido_mensal = falta_anual / 12
                        
                        # Calcula a economia estimada simulando a alíquota do Anexo III
                        aliq_anexo3_simulada, _, _ = descobrir_faixa_e_calcular(faturamento, TABELA_ANEXO_III)
                        economia_anual = (aliquota_efetiva - aliq_anexo3_simulada) * faturamento

                        st.warning(f"🔴 Seu Fator R atual é de **{fator_r * 100:.2f}%**. Você está perdendo dinheiro no Anexo V.")
                        
                        col_plan1, col_plan2 = st.columns(2)
                        col_plan1.metric("Pró-Labore Adicional Mensal Recomendado", f"R$ {pro_labore_sugerido_mensal:,.2f}")
                        col_plan2.metric("Economia de Imposto Estimada (Anual)", f"R$ {economia_anual:,.2f}", delta="Redução de Custo")
                        
                        st.info(f"📌 **Estratégia:** Se você aumentar a retirada de Pró-Labore (ou folha de salários) para uma média de **R$ {folha_alvo_mensal:,.2f} por mês**, sua empresa migra automaticamente para o Anexo III, reduzindo a alíquota efetiva.")
                    else:
                        st.info(f"🟢 Seu Fator R atual é de **{fator_r * 100:.2f}%**. Sua folha atende aos requisitos legais.")
                        st.write(f"Sua retirada média mensal de folha/pró-labore atual é de **R$ {(folha_salarial/12):,.2f}**. O mínimo necessário para se manter no Anexo III é de **R$ {folha_alvo_mensal:,.2f}** por mês.")

                # Memória de Cálculo Oculta
                with st.expander("🔍 Ver memória de cálculo detalhada"):
                    st.write(f"**Faturamento total considerado:** R$ {faturamento:,.2f}")
                    st.write(f"**Parcela deduzida aplicada:** R$ {deducao:,.2f}")
                    st.write(f"**Fórmula:** (({faturamento} × {aliq_nominal}) - {deducao}) ÷ {faturamento}")
            else:
                st.error("Erro no processamento das faixas tributárias.")
    else:
        st.error("Por favor, digite um valor de faturamento válido.")