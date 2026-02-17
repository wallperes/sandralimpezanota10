import streamlit as st
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# --- CONFIGURAÇÕES INICIAIS ---
NUMERO_WHATSAPP_MAE = "5521969293505" 

st.set_page_config(
    page_title="Agenda de Limpeza da Sandra",
    page_icon="🧹",
    layout="centered"
)

# --- ESTILOS CSS (Para interface do app) ---
st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #2e7d32; color: white; font-weight: bold; /* Verde Sandra */
    }
    .instruction-box {
        background-color: #e8f5e9; padding: 15px; border-radius: 10px;
        border-left: 5px solid #2e7d32; margin-bottom: 10px; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# FUNÇÃO DE GERAR IMAGEM (O "CÉREBRO" DO CÓDIGO)
# ==============================================================================
def criar_cartao_sandra(dados, checklist_items):
    # Altura base dinâmica
    height = 950
    if checklist_items:
        height += len(checklist_items) * 40 + 50
    
    # Se tiver muitas instruções de acesso/obs, aumenta a imagem
    if len(dados.get("Obs", "")) > 100: height += 100
    if len(dados.get("Acesso", "")) > 100: height += 100

    width = 800
    background_color = "white"
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # --- FONTES ---
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_sub = ImageFont.truetype("DejaVuSans-Bold.ttf", 24)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_small = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # --- CABEÇALHO VERDE ---
    draw.rectangle([(0, 0), (width, 140)], fill="#2e7d32") # Verde Escuro
    draw.text((30, 30), "AGENDA & CHECKLIST", font=font_title, fill="white")
    draw.text((30, 90), f"Profissional: Sandra | Data: {dados['Data']}", font=font_text, fill="#e8f5e9")

    y = 170
    margin = 40

    # --- BLOCO 1: IDENTIFICAÇÃO E ACESSO ---
    draw.text((margin, y), "📍 LOCAL E ACESSO", font=font_header, fill="#1b5e20")
    y += 40
    
    # Cliente e Endereço
    draw.text((margin, y), f"Cliente: {dados['Cliente']}", font=font_sub, fill="#333")
    y += 35
    linhas_end = textwrap.wrap(f"Endereço: {dados['Endereço']}", width=60)
    for l in linhas_end:
        draw.text((margin, y), l, font=font_text, fill="#555")
        y += 30
    
    y += 15
    # Caixa de destaque para Acesso (Chaves/Senha)
    draw.rectangle([(margin, y), (width-margin, y+90)], fill="#fffde7", outline="#fbc02d", width=2)
    draw.text((margin+15, y+10), "🔑 INSTRUÇÕES DE ENTRADA:", font=font_sub, fill="#f57f17")
    
    linhas_acesso = textwrap.wrap(dados['Acesso'], width=55)
    y_acesso = y + 45
    for l in linhas_acesso:
        draw.text((margin+15, y_acesso), l, font=font_text, fill="#333")
        y_acesso += 30
    
    y += 110 # Pula a caixa amarela

    draw.line([(margin, y), (width-margin, y)], fill="#eee", width=2)
    y += 20

    # --- BLOCO 2: PREFERÊNCIAS (ROUPAS, LIXO, ETC) ---
    draw.text((margin, y), "🛏️ PREFERÊNCIAS E ROTINA", font=font_header, fill="#1b5e20")
    y += 40

    infos_rapidas = [
        f"Camas: {dados['Camas']}",
        f"Toalhas: {dados['Toalhas']}",
        f"Roupa Suja: {dados['Roupa Suja']}",
        f"Lixo: {dados['Lixo']}",
        f"Aspirador: {dados['Aspirador']}",
        f"Repor: {dados['Amenities']}"
    ]

    for info in infos_rapidas:
        draw.rectangle([(margin, y+5), (margin+10, y+15)], fill="#2e7d32") # Bullet point quadrado
        draw.text((margin+20, y), info, font=font_text, fill="#444")
        y += 35

    y += 20
    draw.line([(margin, y), (width-margin, y)], fill="#eee", width=2)
    y += 20

    # --- BLOCO 3: CHECKLIST TÉCNICO ---
    if checklist_items:
        draw.text((margin, y), "📋 TAREFAS ESPECÍFICAS (CHECKLIST)", font=font_header, fill="#1b5e20")
        y += 45
        
        for item in checklist_items:
            # Checkbox vazio [ ]
            draw.rectangle([(margin, y+5), (margin+20, y+25)], outline="#333", width=2)
            draw.text((margin+35, y), item, font=font_text, fill="#333")
            y += 40

    # --- OBSERVAÇÕES FINAIS ---
    if dados['Obs']:
        y += 20
        draw.rectangle([(0, y), (width, y+40)], fill="#eee")
        draw.text((margin, y+8), "⚠️ OBSERVAÇÕES EXTRAS", font=font_sub, fill="#333")
        y += 50
        linhas_obs = textwrap.wrap(dados['Obs'], width=60)
        for l in linhas_obs:
            draw.text((margin, y), l, font=font_text, fill="#555")
            y += 30

    # Rodapé
    draw.text((margin, height-40), "Gerado via App Agenda da Sandra", font=font_small, fill="#aaa")

    return image

# ==============================================================================
# INTERFACE DO STREAMLIT
# ==============================================================================
st.title("🧹 Agenda & Check-list da Sandra")
st.markdown("Verifique a disponibilidade e gere a ordem de serviço.")

tab_agenda, tab_servico = st.tabs(["📅 Ver Disponibilidade", "📝 Criar Ordem de Serviço"])

# --- ABA 1: CALENDÁRIO (Mantido do código novo) ---
with tab_agenda:
    st.info("💡 Dica: Se o dia não aparece na lista abaixo, ele está **LIVRE**!")
    calendar_url = "https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&ctz=America%2FSao_Paulo&mode=AGENDA&showTitle=0&showNav=1&showDate=1&showPrint=0&showTabs=0&showCalendars=0&showTz=0&bgcolor=%23ffffff"
    st.components.v1.iframe(calendar_url, height=500, scrolling=True)

# --- ABA 2: FORMULÁRIO COMPLETO (Fusão) ---
with tab_servico:
    with st.form("form_ordem_servico"):
        st.subheader("1. Identificação")
        col_d1, col_d2 = st.columns(2)
        data_servico = col_d1.date_input("Data da Limpeza", datetime.now())
        nome_cliente = col_d2.text_input("Nome do Cliente")
        endereco = st.text_input("Endereço / Apto")

        st.divider()
        
        st.subheader("2. Acesso e Instruções (Importante)")
        tipo_entrada = st.selectbox("Como entro no imóvel?", 
            ["Senha na Fechadura", "Chave na Portaria", "Lockbox (Cofre)", "Tag / Porteiro", "Tem gente em casa"])
        
        detalhes_acesso = st.text_area("Detalhes do Acesso (Senhas, onde está a chave, Wi-Fi):", 
            placeholder="Ex: Senha 1234. Wi-Fi: Casa123. A chave fica no cofre atrás do vaso.")

        st.divider()

        st.subheader("3. Preferências e Rotina")
        c1, c2 = st.columns(2)
        cama_pref = c1.radio("Camas:", ["Fazer Completa", "Apenas Dobrar", "Não Mexer"])
        toalha_pref = c2.radio("Toalhas:", ["No Banheiro", "Em cima da Cama", "Não Mexer"])
        
        roupa_suja = st.selectbox("Roupa Suja:", ["Não tem", "Lavar na Máquina", "Apenas retirar e por no cesto"])
        lixo_instrucao = st.text_input("Onde descarto o lixo?", placeholder="Ex: Lixeira do andar, Tubo, Levar pra rua...")
        aspirador = st.selectbox("Aspirador:", ["Tem e funciona", "Não tem (usar vassoura)", "Tem mas é fraco"])
        
        amenities = st.multiselect("Repor (Se houver no estoque):", 
            ["Papel Higiênico", "Sabonete", "Detergente", "Saco de Lixo", "Cápsula Café"])

        st.divider()

        st.subheader("4. Checklist Técnico (O que focar?)")
        st.caption("Marque o que precisa de atenção especial hoje:")
        
        tarefas_selecionadas = []
        
        with st.expander("🍽️ Cozinha", expanded=True):
            if st.checkbox("Limpar interior do micro-ondas"): tarefas_selecionadas.append("Limpar Micro-ondas")
            if st.checkbox("Limpar Geladeira (Descartar itens abertos)"): tarefas_selecionadas.append("Limpar Geladeira (Descarte)")
            if st.checkbox("Limpar Forno"): tarefas_selecionadas.append("Limpar Forno")
        
        with st.expander("🛁 Banheiros"):
            if st.checkbox("Lavar Box e Ralos"): tarefas_selecionadas.append("Lavar Box/Ralos")
            if st.checkbox("Limpar Espelhos"): tarefas_selecionadas.append("Limpar Espelhos")
            if st.checkbox("Limpar Vidros/Janelas"): tarefas_selecionadas.append("Limpar Vidros")

        with st.expander("🛏️ Quartos/Sala"):
            if st.checkbox("Aspirar Sofá"): tarefas_selecionadas.append("Aspirar Sofá")
            if st.checkbox("Limpar embaixo das camas"): tarefas_selecionadas.append("Limpar sob camas")
            if st.checkbox("Tirar pó persianas"): tarefas_selecionadas.append("Pó Persianas")

        obs_geral = st.text_area("Outras observações:")

        # Botão
        submitted = st.form_submit_button("✅ Gerar Cartão de Serviço")

    # --- PÓS ENVIO: GERAÇÃO DA IMAGEM ---
    if submitted:
        if not nome_cliente:
            st.error("Preencha o nome do cliente!")
        else:
            # Prepara dados
            amenities_str = ", ".join(amenities) if amenities else "Nada"
            
            dados_imagem = {
                "Cliente": nome_cliente,
                "Data": data_servico.strftime("%d/%m/%Y"),
                "Endereço": endereco,
                "Acesso": f"{tipo_entrada}. {detalhes_acesso}",
                "Camas": cama_pref,
                "Toalhas": toalha_pref,
                "Roupa Suja": roupa_suja,
                "Lixo": lixo_instrucao if lixo_instrucao else "Perguntar portaria",
                "Aspirador": aspirador,
                "Amenities": amenities_str,
                "Obs": obs_geral
            }

            # Gera Imagem
            imagem_final = criar_cartao_sandra(dados_imagem, tarefas_selecionadas)
            
            st.success("Cartão Gerado com Sucesso!")
            st.image(imagem_final, caption="Prévia do Cartão", use_container_width=True)

            # Botões de Download e Ação
            buf = io.BytesIO()
            imagem_final.save(buf, format="PNG")
            byte_im = buf.getvalue()

            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Baixar Imagem", data=byte_im, file_name=f"faxina_{nome_cliente}.png", mime="image/png")
            with c2:
                # Link WhatsApp apenas chamando a Sandra, pois a pessoa envia a imagem
                link_zap = f"https://wa.me/{NUMERO_WHATSAPP_MAE}?text=Olá Sandra, segue o cartão com as instruções da limpeza:"
                st.link_button("📲 Abrir WhatsApp da Sandra", link_zap)
            
            st.info("👆 Dica: Baixe a imagem e envie para a Sandra junto com a mensagem!")
