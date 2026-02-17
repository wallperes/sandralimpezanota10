import streamlit as st
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# ==========================================
# 1. CONFIGURAÇÕES VISUAIS
# ==========================================
st.set_page_config(page_title="Gestão de Limpeza Pro", page_icon="🧹", layout="centered")

st.markdown("""
    <style>
    .stButton>button {
        width: 100%; border-radius: 8px; height: 3.5em;
        background-color: #007bff; color: white; font-weight: bold;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    .instruction-box {
        background-color: #f0f2f6; padding: 15px; border-radius: 10px;
        border-left: 5px solid #007bff; margin-bottom: 10px; font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NEGÓCIO (PREÇO)
# ==========================================
def calculate_price(tipo, quartos, banheiros):
    """Sua lógica original de preço"""
    base = 120.0 if "Padrão" in tipo else 200.0
    total = base + (quartos * 20.0) + (banheiros * 30.0)
    return total

# ==========================================
# 3. FUNÇÃO QUE DESENHA A IMAGEM
# ==========================================
def criar_imagem_ficha(dados, checklist_items=None, tipo="cadastro", preco_final=None):
    # --- CÁLCULO DA ALTURA DA IMAGEM ---
    height = 900 # Altura base
    
    # Aumenta a imagem se tiver muitos itens no checklist
    if checklist_items:
        height += len(checklist_items) * 45 + 100
    
    # Se for cadastro, precisa de espaço para os dados fixos
    if tipo == "cadastro":
        height = 1100

    width = 800
    background_color = "white"
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # --- FONTES (Tentativa de carregar fontes melhores) ---
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_check = ImageFont.truetype("DejaVuSans.ttf", 22)
        font_price = ImageFont.truetype("DejaVuSans-Bold.ttf", 35)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_check = ImageFont.load_default()
        font_price = ImageFont.load_default()

    # --- CABEÇALHO ---
    cor_topo = "#007bff" if tipo == "cadastro" else "#6f42c1" # Azul ou Roxo
    titulo = "FICHA DE CADASTRO" if tipo == "cadastro" else "ORDEM DE SERVIÇO"
    
    draw.rectangle([(0, 0), (width, 130)], fill=cor_topo)
    draw.text((40, 40), titulo, font=font_title, fill="white")

    # --- CORPO DOS DADOS ---
    y = 170
    margin = 50
    
    for label, valor in dados.items():
        draw.text((margin, y), label, font=font_header, fill="#333")
        y += 40
        # Quebra de linha automática
        linhas = textwrap.wrap(str(valor), width=50)
        for linha in linhas:
            draw.text((margin, y), linha, font=font_text, fill="#555")
            y += 35
        y += 20
        draw.line([(margin, y), (width-margin, y)], fill="#eee", width=2)
        y += 25

    # --- DESENHAR CHECKLIST (SE HOUVER) ---
    if checklist_items and len(checklist_items) > 0:
        y += 10
        # Cabeçalho do Checklist
        draw.rectangle([(0, y), (width, y+60)], fill="#e9ecef")
        draw.text((margin, y+15), "📋 CHECKLIST OPERACIONAL", font=font_header, fill="#333")
        y += 80
        
        for item in checklist_items:
            # Desenha caixinha de check [ ]
            draw.rectangle([(margin, y+5), (margin+25, y+30)], outline="#333", width=2)
            # Texto da tarefa
            draw.text((margin + 40, y+2), item, font=font_check, fill="#000")
            y += 45
        
        y += 30 # Espaço após checklist

    # --- DESENHAR PREÇO (SE HOUVER) ---
    if preco_final:
        draw.rectangle([(margin, y), (width-margin, y+80)], fill="#d4edda")
        texto_preco = f"VALOR TOTAL: R$ {preco_final:.2f}"
        draw.text((margin + 150, y+20), texto_preco, font=font_price, fill="#155724")

    # --- RODAPÉ ---
    rodape = f"Gerado em {date.today().strftime('%d/%m/%Y')} | Sistema de Limpeza Pro"
    draw.text((margin, height - 50), rodape, font=font_text, fill="#aaaaaa")

    return image

# ==========================================
# 4. INTERFACE PRINCIPAL
# ==========================================
st.title("🧹 Gerador de Fichas de Limpeza")
st.markdown("Crie fichas detalhadas com checklists e envie via WhatsApp.")

# Seletor de Modo
modo = st.radio(
    "Escolha o tipo de documento:",
    ["📅 Ordem de Serviço (Dia a Dia)", "📝 Cadastro de Imóvel (Fixo)"],
    horizontal=True
)

st.divider()

# --- MODO 1: ORDEM DE SERVIÇO (AGENDAMENTO) ---
if "Ordem" in modo:
    with st.form("form_agendamento"):
        st.subheader("1. Detalhes do Serviço")
        
        # Recuperando inputs originais
        cliente_nome = st.text_input("Nome do Cliente:")
        
        c1, c2 = st.columns(2)
        checkin = c1.date_input("Check-in", date.today())
        checkout = c2.date_input("Check-out", date.today() + timedelta(days=2))
        
        tipo_limpeza = st.selectbox("Tipo de Serviço:", ["Padrão (Turnover)", "Limpeza Pesada / Pós-Obra"])
        
        st.markdown("**Configuração para Cálculo**")
        col_q, col_b = st.columns(2)
        n_quartos = col_q.number_input("Quartos:", min_value=1, value=2)
        n_banheiros = col_b.number_input("Banheiros:", min_value=1, value=1)
        
        # Cálculo em tempo real
        preco_calc = calculate_price(tipo_limpeza, n_quartos, n_banheiros)
        st.info(f"💰 Valor Calculado: **R$ {preco_calc:.2f}**")
        
        st.subheader("2. Checklist de Execução")
        st.caption("Selecione o que deve ser feito nesta visita:")
        
        tarefas = []
        
        # --- SEUS CHECKLISTS ORIGINAIS RECUPERADOS ---
        with st.expander("🍽️ Cozinha e Áreas Comuns", expanded=True):
            if st.checkbox("Remover lixo e colocar novos sacos"): tarefas.append("Remover lixo e trocar sacos")
            if st.checkbox("Limpar interior do micro-ondas e fogão"): tarefas.append("Limpar micro-ondas e fogão")
            if st.checkbox("Higienizar bancadas e pia"): tarefas.append("Higienizar bancadas e pia")
            if st.checkbox("Limpar cafeteira e repor itens"): tarefas.append("Limpar cafeteira e repor itens")
            
        with st.expander("🛁 Banheiros"):
            if st.checkbox("Desinfetar vaso sanitário (base/tampa)"): tarefas.append("Desinfetar vaso sanitário")
            if st.checkbox("Limpar box e remover fios de cabelo"): tarefas.append("Limpar box e ralos")
            if st.checkbox("Polir metais e espelhos"): tarefas.append("Polir metais e espelhos")
            if st.checkbox("Repor papel higiênico e toalhas"): tarefas.append("Repor papel e toalhas")
            
        with st.expander("🛏️ Quartos e Sala"):
            if st.checkbox("Trocar roupas de cama e fronhas"): tarefas.append("Trocar roupas de cama")
            if st.checkbox("Espanar móveis e eletrônicos"): tarefas.append("Espanar móveis e eletrônicos")
            if st.checkbox("Organizar almofadas e mantas"): tarefas.append("Organizar almofadas/mantas")
            if st.checkbox("Desinfetar controles e maçanetas"): tarefas.append("Desinfetar controles/maçanetas")

        obs_extra = st.text_area("Observações Extras:")
        
        submitted = st.form_submit_button("🔨 GERAR ORDEM DE SERVIÇO")
        
        if submitted:
            if not cliente_nome:
                st.error("Por favor, preencha o nome do cliente.")
            else:
                dados = {
                    "Cliente": cliente_nome,
                    "Período": f"{checkin.strftime('%d/%m')} a {checkout.strftime('%d/%m')}",
                    "Tipo": tipo_limpeza,
                    "Configuração": f"{n_quartos} Quartos | {n_banheiros} Banheiros",
                    "Observações": obs_extra if obs_extra else "Seguir checklist abaixo."
                }
                
                # Gera imagem com checklist e preço
                st.session_state['imagem_final'] = criar_imagem_ficha(
                    dados, 
                    checklist_items=tarefas, 
                    tipo="ordem", 
                    preco_final=preco_calc
                )
                st.session_state['nome_arquivo'] = "ordem_servico.png"

# --- MODO 2: CADASTRO (FIXO) ---
else:
    with st.form("form_cadastro"):
        st.subheader("📝 Ficha Cadastral Completa")
        
        nome = st.text_input("Nome do Proprietário:")
        whatsapp = st.text_input("WhatsApp de Contato:")
        email = st.text_input("E-mail (Opcional):")
        endereco = st.text_area("Endereço Completo:")
        
        c1, c2 = st.columns(2)
        quartos = c1.number_input("Qtd. Padrão Quartos", min_value=1, value=2)
        banheiros = c2.number_input("Qtd. Padrão Banheiros", min_value=1, value=2)
        
        st.markdown("**Acesso e Instruções**")
        wifi = st.text_input("Rede Wi-Fi / Senha:")
        instrucoes = st.text_area("Instruções de Chaves/Portaria:")
        
        submitted = st.form_submit_button("💾 GERAR FICHA DE CADASTRO")
        
        if submitted:
            if not nome or not endereco:
                st.error("Nome e Endereço são obrigatórios.")
            else:
                dados = {
                    "Proprietário": f"{nome} ({whatsapp})",
                    "E-mail": email if email else "-",
                    "Endereço": endereco,
                    "Configuração": f"{quartos} Quartos | {banheiros} Banheiros",
                    "Wi-Fi": wifi if wifi else "-",
                    "Acesso": instrucoes if instrucoes else "Combinar"
                }
                st.session_state['imagem_final'] = criar_imagem_ficha(dados, tipo="cadastro")
                st.session_state['nome_arquivo'] = "ficha_cadastro.png"

# ==========================================
# 5. ÁREA DE VISUALIZAÇÃO E DOWNLOAD
# ==========================================
if 'imagem_final' in st.session_state:
    st.divider()
    st.success("✅ Imagem gerada com sucesso! Veja abaixo:")
    
    st.image(st.session_state['imagem_final'], caption="Prévia do Documento", use_container_width=True)
    
    # Prepara Buffer
    buf = io.BytesIO()
    st.session_state['imagem_final'].save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.markdown("### 📲 Como enviar?")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="instruction-box">
        <b>Opção 1 (Celular):</b><br>
        Toque e segure na imagem acima e escolha "Compartilhar" ou "Copiar".
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.download_button(
            label="⬇️ BAIXAR ARQUIVO",
            data=byte_im,
            file_name=st.session_state['nome_arquivo'],
            mime="image/png"
        )
