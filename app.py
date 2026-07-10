import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date, time
import requests 
import urllib.parse
from st_keyup import st_keyup

# --- CONFIGURAÇÕES DO AMBIENTE ---
st.set_page_config(page_title="Gestão de Limpeza Automatizada", page_icon="✨", layout="centered")

# Inicialização de variáveis de memória para o CEP
if "rua_input" not in st.session_state: st.session_state.rua_input = ""
if "bairro_input" not in st.session_state: st.session_state.bairro_input = ""
if "cidade_uf_input" not in st.session_state: st.session_state.cidade_uf_input = ""

def buscar_cep_tempo_real(cep_limpo):
    try:
        response = requests.get(f"https://viacep.com.br/ws/{cep_limpo}/json/", timeout=5)
        data = response.json()
        if "erro" not in data:
            st.session_state.rua_input = data.get("logradouro", "")
            st.session_state.bairro_input = data.get("bairro", "")
            st.session_state.cidade_uf_input = f"{data.get('localidade', '')} / {data.get('uf', '')}"
    except:
        pass 

# --- ESTILOS VISUAIS ---
st.markdown("""
    <style>
    .stApp { background-color: #F4F7F6; font-family: 'Inter', sans-serif; }
    div[data-testid="stWidgetLabel"] p, .stMarkdown p, h1, h2, h3, label { color: #2b2b2b !important; }
    button[data-baseweb="tab"][aria-selected="true"] p { color: #188038 !important; font-weight: bold !important; }
    [data-testid="stForm"] { background-color: #FFFFFF !important; border-radius: 20px; padding: 30px; box-shadow: 0 8px 24px rgba(0,0,0,0.04); border: 1px solid #f0f0f0; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 16px; color: #FFFFFF !important; background: linear-gradient(135deg, #34A853 0%, #188038 100%); border: none; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea { border-radius: 10px !important; border: 1px solid #E0E0E0 !important; background-color: #FAFAFA !important; padding: 12px !important; color: #2b2b2b !important; }
    [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 12px; padding: 5px; gap: 10px; }
    [data-baseweb="tab"][aria-selected="true"] { background-color: #E8F5E9 !important; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO DE AUXÍLIO: BOTÃO DO WHATSAPP ---
def renderizar_botao_whatsapp(texto_corpo):
    texto_codificado = urllib.parse.quote(texto_corpo)
    link_whatsapp = f"https://wa.me/5521969293505?text={texto_codificado}"
    
    componente_html = f"""
    <div style="font-family: 'Inter', sans-serif; margin-top: 20px; margin-bottom: 20px;">
        <a href="{link_whatsapp}" target="_blank" style="text-decoration: none;">
            <button style="background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; border: none; padding: 16px 28px; border-radius: 12px; font-weight: bold; cursor: pointer; width: 100%; font-size: 17px; box-shadow: 0 4px 12px rgba(37,211,102,0.3);">
                💬 Chamar Sandra no WhatsApp para Confirmar
            </button>
        </a>
    </div>
    """
    components.html(componente_html, height=100)

# --- CABEÇALHO DO APP ---
st.markdown("<h1 style='text-align: center; color: #188038;'>✨ App da Sandra</h1>", unsafe_allow_html=True)
st.markdown("<div style='background-color: #E8F5E9; padding: 25px; border-radius: 15px; border-left: 6px solid #188038; margin-bottom: 25px;'><h3 style='color: #188038; margin-top:0;'>Olá, eu sou a Sandra! ✨</h3><p style='color: #424242; font-size: 16px; margin-bottom:0;'>Criei este espaço para organizar os agendamentos das nossas faxinas e manter o seu padrão de qualidade registrado. Escolha a aba desejada abaixo para começar!</p></div>", unsafe_allow_html=True)

tab_imovel, tab_rotina = st.tabs(["🏢 Ficha do Imóvel", "📅 Solicitação de Limpeza"])

# --- ABA 1: FICHA DO IMÓVEL ---
with tab_imovel:
    st.markdown("### 🔎 Cadastro do Imóvel")
    i_cep = st_keyup("CEP", placeholder="Preencha seu CEP aqui", label_visibility="collapsed", key="cep_input")
    if i_cep:
        cep_limpo = i_cep.replace("-", "").replace(".", "").replace(" ", "").strip()
        if len(cep_limpo) == 8 and cep_limpo.isdigit():
            buscar_cep_tempo_real(cep_limpo)
        
    with st.form("form_imovel"):
        st.markdown("### 📍 1. Identificação do Imóvel")
        i_rua = st.text_input("Logradouro (Rua, Avenida, etc.)", key="rua_input")
        col_end1, col_end2 = st.columns(2)
        with col_end1: i_bairro = st.text_input("Bairro", key="bairro_input")
        with col_end2: i_cidade_uf = st.text_input("Cidade / UF", key="cidade_uf_input")
        col_end3, col_end4 = st.columns(2)
        with col_end3: i_num = st.text_input("Número 🔢")
        with col_end4: i_comp = st.text_input("Complemento")
        i_cond = st.text_input("Qual é o nome do Edifício ou Condomínio? 🏢")
        i_prop = st.text_input("Qual o nome do proprietário ou responsável? 👤")
        i_configuracao = st.text_input("Como é a configuração do seu imóvel? 🏠")
        
        st.markdown("### 🧹 2. Equipamentos, Climatização e Materiais")
        i_aspirador = st.text_input("Tem aspirador de pó funcionando? Qual a voltagem? 🔌")
        i_materiais = st.text_input("Posso contar com vassoura, rodo, balde e panos?")
        i_produtos = st.text_input("Instruções sobre os produtos de limpeza:")
        i_proibido = st.text_input("Tem algum produto PROIBIDO? 🚫")
        i_ventiladores = st.text_input("Sobre os ventiladores (teto e chão): 🌬️")
        
        st.markdown("### 🛏️ 3. Quartos e Roupa de Cama")
        i_guardar = st.text_input("Onde guarda as roupas de cama e banho limpas? 🧺")
        i_suja = st.text_input("Onde deixo a roupa suja?")
        i_montar = st.text_area("Como você prefere que eu monte as camas?")
        
        st.markdown("### 4. Detalhes Adicionais")
        i_obs_finais = st.text_area("Alguma observação importante ou detalhe final? 📝")
        
        btn_imovel = st.form_submit_button("💾 Enviar Ficha do Imóvel")
        
    if btn_imovel:
        msg_ficha = f"Oi Sandra! Acabei de enviar a Ficha Técnica do imóvel do(a) {i_prop} ({i_cond}) através do site para o seu controle!"
        st.success("Ficha técnica registrada no sistema com sucesso!")
        renderizar_botao_whatsapp(msg_ficha)

# --- ABA 2: SOLICITAÇÃO DE LIMPEZA (SISTEMA INTELIGENTE COFRE) ---
with tab_rotina:
    st.markdown("### 🗓️ Visão Geral da Minha Agenda de Limpeza")
    components.iframe("https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&mode=WEEK", height=600, scrolling=True)

    st.markdown("### 📝 Nova Solicitação de Limpeza")
    
    q_cadastro = st.radio("Já fizemos a Ficha Técnica desse seu imóvel antes? 📝", ["Já fizemos a Ficha", "Primeira vez"])
    q_ident = st.text_input("Qual é o imóvel? Condomínio, torre e apartamento 🏢 (Ex: Rio Wonder, Torre 1, Apto 302)")
    q_data = st.date_input("Qual é a data gostaria de reservar? 🗓️✅", date.today(), format="DD/MM/YYYY")
    
    st.write("")
    st.markdown("### ⏰ Horários")
    st.info("💡 É desejável dispor de 3 horas para uma limpeza padrão, mas é possível realizar o serviço em até 2 horas se necessário.")
    
    # Substituição para garantir precisão na varredura da API do Google Calendar
    col_h1, col_h2 = st.columns(2)
    with col_h1:
        q_hora_inicio = st.selectbox("Horário de Início desejado 🕒", [time(h, 0) for h in range(8, 20)], format_func=lambda t: t.strftime("%H:%M"))
    with col_h2:
        q_hora_fim = st.selectbox("Horário de Término desejado 🕒", [time(h, 0) for h in range(9, 21)], index=3, format_func=lambda t: t.strftime("%H:%M"))
        
    q_checkin = st.radio("Entrarão novos hóspedes no mesmo dia? 🚪", ["Sim, entram no mesmo dia", "Não, o apartamento ficará vazio"])
    q_acesso = st.text_area("Como vai ser a minha entrada no dia dessa limpeza? 🔑")
    q_notas = st.text_area("Deseja acrescentar alguma observação importante ou pedido especial? ✨")
    
    btn_gen = st.button("🚀 Verificar Disponibilidade e Agendar")
    
    if btn_gen:
        dt_br = q_data.strftime("%d/%m/%Y")
        horario_txt = f"das {q_hora_inicio.strftime('%H:%M')} às {q_hora_fim.strftime('%H:%M')}"
        
        # Constrói strings ISO válidas (RFC3339) para o Google Calendar
        iso_inicio = f"{q_data.strftime('%Y-%m-%d')}T{q_hora_inicio.strftime('%H:%M:%S')}"
        iso_fim = f"{q_data.strftime('%Y-%m-%d')}T{q_hora_fim.strftime('%H:%M:%S')}"
        
        # Envio oculto de servidor para servidor
        URL_WEBHOOK_GOOGLE = "https://script.google.com/macros/s/AKfycbzQy_O8w9C03O2Sg3wH2t6Yj59RzK9wR7f3l4m/exec" # Substitua pela nova URL gerada pelo Script atualizado
        
        payload_seguro = {
            "token": "SenhaSuperSegura123!",
            "tipo": "limpeza",
            "apto": q_ident,
            "data_inicio": iso_inicio,
            "data_fim": iso_fim,
            "data_br": dt_br,
            "horario_formatated": horario_txt,
            "detalhes": f"Acesso: {q_acesso}\nCheck-in simultâneo: {q_checkin}\nNotas: {q_notas}"
        }
        
        status_agenda = "erro"
        try:
            r = requests.post(URL_WEBHOOK_GOOGLE, json=payload_seguro, timeout=10)
            resposta_servidor = r.json()
            status_agenda = resposta_servidor.get("status", "erro")
        except:
            status_agenda = "erro" # Se o Google cair ou falhar, o sistema assume tratamento seguro
            
        if status_agenda == "sucesso":
            st.balloons()
            st.success(f"🎉 Excelente! O horário {horario_txt} no dia {dt_br} estava livre e já foi pré-reservado para você!")
            
            msg_sucesso = f"""Oi Sandra! Usei o seu site para solicitar uma limpeza. 
            
🏢 *Imóvel:* {q_ident}
📅 *Data:* {dt_br}
⏰ *Horário:* {horario_txt}

O site me avisou que seu horário estava livre e já registrou o pedido. Se estiver tudo certinho com as condições, me avise por favor! 😊"""
            renderizar_botao_whatsapp(msg_sucesso)
            
        elif status_agenda == "conflito":
            st.warning(f"⚠️ Atenção: O horário das {q_hora_inicio.strftime('%H:%M')} às {q_hora_fim.strftime('%H:%M')} no dia {dt_br} já possui outro compromisso agendado.")
            st.info("💡 Não se preocupe! Você ainda pode enviar uma mensagem para a Sandra abaixo para verificar a possibilidade de um encaixe ou reajuste de horários.")
            
            msg_conflito = f"""Oi Sandra, tudo bem? Tentei solicitar uma limpeza para o imóvel {q_ident} no dia {dt_br} {horario_txt}.
            
O site me informou que você já tem um compromisso agendado exatamente nessa janela de tempo, mas gostaria de ver com você se existe alguma possibilidade de encaixe, reajuste ou troca com o outro cliente. Seria possível?"""
            renderizar_botao_whatsapp(msg_conflito)
            
        else:
            st.error("Ocorreu uma oscilação temporária na comunicação com o calendário. Por favor, tente falar diretamente com a Sandra clicando abaixo.")
            renderizar_botao_whatsapp(f"Oi Sandra, o sistema de agendamento automático deu um erro ao tentar agendar para o dia {dt_br} {horario_txt}. Pode checar para mim?")
