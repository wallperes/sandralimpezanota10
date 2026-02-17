import streamlit as st
from datetime import datetime, date, timedelta
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# ==========================================
# 1. CONFIGURAÇÕES DA PÁGINA E ESTILO
# ==========================================
st.set_page_config(
    page_title="Gerador de Ficha de Limpeza",
    page_icon="🧹",
    layout="centered"
)

# CSS para melhorar a aparência no celular (Botões grandes e caixas de instrução)
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
    .instruction-title {
        font-weight: bold;
        color: #007bff;
        margin-bottom: 5px;
        display: block;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. FUNÇÃO QUE DESENHA A IMAGEM (CARD)
# ==========================================
def criar_imagem_ficha(dados, tipo="cadastro"):
    # Configurações da tela de pintura
    width = 800
    # Altura dinâmica (se for cadastro é maior)
    height = 1100 if tipo == "cadastro" else 900 
    background_color = "white"
    
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # Tentar carregar fontes do sistema (Linux/Streamlit Cloud)
    # Se falhar, usa a fonte padrão (feia, mas funciona)
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 26)
        font_footer = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # Definição de Cores
    if tipo == "cadastro":
        cor_topo = "#007bff" # Azul
        titulo_card = "FICHA DE CADASTRO"
    else:
        cor_topo = "#28a745" # Verde
        titulo_card = "AGENDA DE LIMPEZA"

    # Desenhar Cabeçalho
    draw.rectangle([(0, 0), (width, 130)], fill=cor_topo)
    draw.text((40, 40), titulo_card, font=font_title, fill="white")
    
    # Desenhar os Dados (Loop)
    y_position = 170
    margin = 50
    
    for label, valor in dados.items():
        # Título do campo (Ex: Endereço)
        draw.text((margin, y_position), label, font=font_header, fill="#333333")
        y_position += 40
        
        # Valor do campo com quebra de linha automática
        # 'width=50' define quantos caracteres cabem antes de quebrar a linha
        linhas = textwrap.wrap(str(valor), width=50)
        
        for linha in linhas:
            draw.text((margin, y_position), linha, font=font_text, fill="#555555")
            y_position += 35
            
        y_position += 20 # Espaço extra
        # Linha separadora cinza
        draw.line([(margin, y_position), (width-margin, y_position)], fill="#eeeeee", width=2)
        y_position += 30

    # Rodapé
    rodape = f"Gerado em {date.today().strftime('%d/%m/%Y')} via App de Gestão"
    draw.text((margin, height - 50), rodape, font=font_footer, fill="#aaaaaa")

    return image

# ==========================================
# 3. INTERFACE DO USUÁRIO (FRONTEND)
# ==========================================
st.title("🧹 Gerador de Cards para WhatsApp")
st.markdown("Preencha os dados e gere uma imagem pronta para enviar à equipe de limpeza.")

# Menu de Escolha
opcao = st.radio(
    "O que você deseja fazer?",
    ["📝 Criar Novo Cadastro (Imóvel)", "📅 Agendar Limpeza (Rotina)"],
    horizontal=True
)

st.divider()

# --- FORMULÁRIO A: CADASTRO ---
if "Cadastro" in opcao:
    st.subheader("📍 Dados do Imóvel")
    with st.form("form_cadastro"):
        nome = st.text_input("Nome do Proprietário:")
        endereco = st.text_area("Endereço Completo (Rua, Nº, Apto, Bairro):")
        
        c1, c2 = st.columns(2)
        quartos = c1.number_input("Qtd. Quartos", min_value=1, value=2)
        banheiros = c2.number_input("Qtd. Banheiros", min_value=1, value=1)
        
        wifi = st.text_input("Senha do Wi-Fi (Opcional):")
        obs_acesso = st.text_area("Instruções de Acesso (Chaves/Senha/Portaria):")
        
        # Botão de Enviar
        submitted = st.form_submit_button("🎨 GERAR IMAGEM DE CADASTRO")
        
        if submitted:
            if not nome or not endereco:
                st.error("⚠️ Por favor, preencha pelo menos Nome e Endereço.")
            else:
                # Prepara os dados para a imagem
                dados = {
                    "Proprietário": nome,
                    "Endereço": endereco,
                    "Configuração": f"{quartos} Quartos | {banheiros} Banheiros",
                    "Wi-Fi": wifi if wifi else "Não informado",
                    "Acesso / Chaves": obs_acesso if obs_acesso else "Combinar entrega"
                }
                # Gera e salva no estado da sessão
                st.session_state['imagem_final'] = criar_imagem_ficha(dados, "cadastro")
                st.session_state['nome_arquivo'] = "ficha_cadastro.png"

# --- FORMULÁRIO B: AGENDAMENTO ---
else:
    st.subheader("📅 Dados do Serviço")
    with st.form("form_agenda"):
        cliente = st.text_input("Nome do Cliente:")
        
        col_a, col_b = st.columns(2)
        checkin = col_a.date_input("Data Entrada (Check-in)", date.today())
        checkout = col_b.date_input("Data Saída (Check-out)", date.today() + timedelta(days=2))
        
        tipo_servico = st.selectbox("Tipo de Limpeza", ["Limpeza Padrão (Turnover)", "Faxina Pesada", "Pós-Obra"])
        obs_dia = st.text_area("Observações para hoje (Ex: Atenção ao forno):")
        
        # Botão de Enviar
        submitted = st.form_submit_button("🎨 GERAR IMAGEM DE AGENDA")
        
        if submitted:
            if not cliente:
                st.error("⚠️ Identifique o cliente.")
            else:
                # Prepara os dados
                dados = {
                    "Cliente": cliente,
                    "Serviço": tipo_servico,
                    "Check-in": checkin.strftime("%d/%m/%Y"),
                    "Check-out": checkout.strftime("%d/%m/%Y"),
                    "Observações": obs_dia if obs_dia else "Nenhuma observação."
                }
                # Gera e salva no estado da sessão
                st.session_state['imagem_final'] = criar_imagem_ficha(dados, "agenda")
                st.session_state['nome_arquivo'] = "agendamento_limpeza.png"

# ==========================================
# 4. ÁREA DE DOWNLOAD E INSTRUÇÕES
# ==========================================
if 'imagem_final' in st.session_state:
    st.divider()
    st.success("✅ Imagem gerada com sucesso! Veja abaixo:")
    
    # Mostra a imagem na tela
    st.image(st.session_state['imagem_final'], caption="Prévia do Card", use_container_width=True)
    
    # Prepara o arquivo para o botão de download
    buf = io.BytesIO()
    st.session_state['imagem_final'].save(buf, format="PNG")
    byte_im = buf.getvalue()
    
    st.markdown("### 📲 Como enviar no WhatsApp?")
    
    col1, col2 = st.columns(2)
    
    # Instrução 1: Celular (Toque Longo)
    with col1:
        st.markdown("""
        <div class="instruction-box">
            <span class="instruction-title">Opção 1 (Celular)</span>
            👆 <b>Toque e segure</b> o dedo na imagem acima.<br>
            📋 Escolha <b>"Copiar"</b> ou <b>"Compartilhar"</b>.<br>
            💬 Cole na conversa do WhatsApp.
        </div>
        """, unsafe_allow_html=True)
        
    # Instrução 2: Download (Computador/Android)
    with col2:
        st.markdown("""
        <div class="instruction-box">
            <span class="instruction-title">Opção 2 (Arquivo)</span>
            👇 Clique no botão <b>Baixar Imagem</b> abaixo.<br>
            📎 No WhatsApp, clique no <b>Clipe</b>.<br>
            🖼️ Selecione a imagem da galeria.
        </div>
        """, unsafe_allow_html=True)

    # Botão de Download Real
    st.download_button(
        label="⬇️ BAIXAR IMAGEM AGORA",
        data=byte_im,
        file_name=st.session_state['nome_arquivo'],
        mime="image/png"
    )
