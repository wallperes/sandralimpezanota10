import streamlit as st
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# ==========================================
# 1. CONFIGURAÇÕES DA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Gestão de Limpeza Pro",
    page_icon="🧹",
    layout="centered"
)

# Estilo CSS
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        font-weight: bold;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        border: none;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }
    .instruction-box {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 6px solid #007bff;
        margin-bottom: 10px;
        font-size: 14px;
        color: #333;
    }
    .price-tag {
        font-size: 20px;
        font-weight: bold;
        color: #28a745;
        background-color: #e6fffa;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin-top: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA DE NEGÓCIO (DO CÓDIGO ORIGINAL)
# ==========================================
def calculate_price(tipo, quartos, banheiros):
    """Lógica de precificação baseada em cômodos (Restaurada)"""
    # Se for Padrão base 120, se for Pesada base 200
    base = 120.0 if "Padrão" in tipo else 200.0
    total = base + (quartos * 20.0) + (banheiros * 30.0)
    return total

# ==========================================
# 3. FUNÇÃO GERADORA DE IMAGEM
# ==========================================
def criar_imagem_ficha(dados, tipo="cadastro", preco=None):
    # Configurações da tela
    width = 800
    height = 1100 if tipo == "cadastro" else 1000 
    background_color = "white"
    
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Fontes
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 26)
        font_price = ImageFont.truetype("DejaVuSans-Bold.ttf", 35) # Fonte para preço
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_price = ImageFont.load_default()

    # Cores e Títulos
    if tipo == "cadastro":
        cor_topo = "#007bff" # Azul
        titulo_card = "FICHA DE CADASTRO"
    else:
        cor_topo = "#28a745" # Verde
        titulo_card = "ORDEM DE SERVIÇO"

    # Cabeçalho
    draw.rectangle([(0, 0), (width, 130)], fill=cor_topo)
    draw.text((40, 40), titulo_card, font=font_title, fill="white")
    
    # Corpo dos Dados
    y_position = 170
    margin = 50
    
    for label, valor in dados.items():
        draw.text((margin, y_position), label, font=font_header, fill="#333333")
        y_position += 40
        
        linhas = textwrap.wrap(str(valor), width=50)
        for linha in linhas:
            draw.text((margin, y_position), linha, font=font_text, fill="#555555")
            y_position += 35
            
        y_position += 20
        draw.line([(margin, y_position), (width-margin, y_position)], fill="#eeeeee", width=2)
        y_position += 30

    # SE TIVER PREÇO (Agendamento), desenha destaque
    if preco:
        # Caixa de destaque para o valor
        draw.rectangle([(margin, y_position), (width-margin, y_position + 80)], fill="#d4edda")
        texto_preco = f"VALOR TOTAL: R$ {preco:.2f}"
        # Centraliza grosseiramente
        draw.text((margin + 180, y_position + 20), texto_preco, font=font_price, fill="#155724")

    # Rodapé
    rodape = f"Gerado em {date.today().strftime('%d/%m/%Y')} | Sistema de Limpeza"
    draw.text((margin, height - 50), rodape, font=font_text, fill="#aaaaaa")

    return image

# ==========================================
# 4. INTERFACE DO USUÁRIO
# ==========================================
st.title("🧹 Agenda de Limpeza da Mamãe")
st.markdown("Gere fichas completas para enviar via WhatsApp.")

opcao = st.radio(
    "Selecione o tipo de documento:",
    ["📝 Ficha de Cadastro Completa", "📅 Ordem de Serviço (Agendamento)"],
    horizontal=True
)

st.divider()

# --- OPÇÃO 1: CADASTRO COMPLETO (Campos restaurados) ---
if "Cadastro" in opcao:
    st.subheader("📍 Dados do Cliente e Imóvel")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome do Proprietário:")
        whatsapp = st.text_input("WhatsApp (Contato):")
        email = st.text_input("E-mail (Opcional):")
        endereco = st.text_area("Endereço Completo (Rua, Nº, Comp, Bairro):")
        
        st.markdown("---")
        st.markdown("**Configuração da Propriedade**")
        c1, c2 = st.columns(2)
        quartos = c1.number_input("Qtd. Quartos", min_value=1, value=2)
        banheiros = c2.number_input("Qtd. Banheiros", min_value=1, value=2)
        
        st.markdown("**Acesso e Instruções**")
        wifi = st.text_input("Senha do Wi-Fi:")
        obs_acesso = st.text_area("Instruções de Chaves/Portaria:")
        
        submitted = st.form_submit_button("🎨 GERAR FICHA DE CADASTRO")
        
        if submitted:
            if not nome or not endereco:
                st.error("⚠️ Nome e Endereço são obrigatórios.")
            else:
                dados = {
                    "Proprietário": f"{nome} ({whatsapp})",
                    "E-mail": email if email else "Não informado",
                    "Endereço": endereco,
                    "Configuração": f"{quartos} Quartos | {banheiros} Banheiros",
                    "Wi-Fi": wifi if wifi else "Não informado",
                    "Acesso / Chaves": obs_acesso if obs_acesso else "Combinar entrega"
                }
                st.session_state['imagem_final'] = criar_imagem_ficha(dados, "cadastro")
                st.session_state['nome_arquivo'] = "ficha_cadastro.png"

# --- OPÇÃO 2: AGENDAMENTO COM PREÇO (Lógica restaurada) ---
else:
    st.subheader("📅 Detalhes do Serviço")
    with st.form("form_agenda"):
        cliente = st.text_input("Nome do Cliente (Já cadastrado):")
        
        col_a, col_b = st.columns(2)
        checkin = col_a.date_input("Check-in", date.today())
        checkout = col_b.date_input("Check-out", date.today() + timedelta(days=2))
        
        tipo_servico = st.selectbox("Tipo de Serviço", ["Padrão (Turnover)", "Limpeza Pesada / Pós-Obra"])
        
        st.markdown("**Cálculo do Valor**")
        c1, c2 = st.columns(2)
        n_quartos = c1.number_input("Quartos (para cálculo):", min_value=1, value=2)
        n_banheiros = c2.number_input("Banheiros (para cálculo):", min_value=1, value=2)
        
        # Mostra o preço em tempo real (simulado na interface) se quiser, mas o form calcula no submit
        preco_calculado = calculate_price(tipo_servico, n_quartos, n_banheiros)
        st.caption(f"ℹ️ Valor base calculado automaticamente: R$ {preco_calculado:.2f}")

        obs_dia = st.text_area("Observações/Checklist Específico:")
        
        submitted = st.form_submit_button("🎨 GERAR ORDEM DE SERVIÇO")
        
        if submitted:
            if not cliente:
                st.error("⚠️ Identifique o cliente.")
            else:
                dados = {
                    "Cliente": cliente,
                    "Serviço": tipo_servico,
                    "Período": f"De {checkin.strftime('%d/%m')} até {checkout.strftime('%d/%m')}",
                    "Configuração Limpa": f"{n_quartos} Quartos | {n_banheiros} Banheiros",
                    "Observações": obs_dia if obs_dia else "Seguir checklist padrão."
                }
                # Gera imagem COM o preço
                st.session_state['imagem_final'] = criar_imagem_ficha(dados, "agenda", preco=preco_calculado)
                st.session_state['nome_arquivo'] = "ordem_servico.png"

# ==========================================
# 5. ÁREA DE DOWNLOAD
# ==========================================
if 'imagem_final' in st.session_state:
    st.divider()
    st.success("✅ Documento gerado!")
    
    st.image(st.session_state['imagem_final'], caption="Prévia", use_container_width=True)
    
    buf = io.BytesIO()
    st.session_state['imagem_final'].save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="instruction-box">
            <b>Celular:</b><br>
            Segure o dedo na imagem e selecione "Compartilhar".
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.download_button(
            label="⬇️ BAIXAR ARQUIVO",
            data=byte_im,
            file_name=st.session_state['nome_arquivo'],
            mime="image/png"
        )
