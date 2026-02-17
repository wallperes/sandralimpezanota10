import streamlit as st
import streamlit.components.v1 as components # Necessário para o Calendário
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
import io
import textwrap

# --- CONFIGURAÇÕES ---
st.set_page_config(page_title="Gestão de Limpeza", page_icon="🧹", layout="centered")

# --- ESTILOS CSS ---
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 1. FUNÇÃO GERADORA DE IMAGEM
# ==============================================================================
def criar_imagem(dados, tipo):
    width = 800
    height = 1000 if tipo == "imovel" else 700 # Altura ajustada
    
    background_color = "white"
    image = Image.new("RGB", (width, height), background_color)
    draw = ImageDraw.Draw(image)

    # --- FONTES (Tenta carregar ou usa padrão) ---
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
    except:
        font_title = ImageFont.load_default()
        font_header = ImageFont.load_default()
        font_text = ImageFont.load_default()
        font_big = ImageFont.load_default()

    # --- CABEÇALHO ---
    if tipo == "imovel":
        cor_topo = "#0277bd" # Azul
        titulo = "FICHA DO IMÓVEL"
        subtitulo = f"Propriedade: {dados.get('Propriedade', '-')}"
    else:
        cor_topo = "#2e7d32" # Verde
        titulo = "ORDEM DE SERVIÇO"
        subtitulo = f"Data da Limpeza: {dados.get('Data', '-')}"

    draw.rectangle([(0, 0), (width, 150)], fill=cor_topo)
    draw.text((40, 40), titulo, font=font_title, fill="white")
    draw.text((40, 100), subtitulo, font=font_text, fill="#e1f5fe" if tipo=="imovel" else "#e8f5e9")

    y = 190
    margin = 50

    # ---------------------------------------------------------
    # LAYOUT 1: FICHA TÉCNICA (Regras Fixas)
    # ---------------------------------------------------------
    if tipo == "imovel":
        secoes = [
            ("🛏 QUARTO E BANHO", ["Montagem", "Toalhas", "Roupa Suja"]),
            ("🪣 OPERACIONAL", ["Produtos", "Amenities", "Geladeira", "Lixo"]),
            ("🔑 ACESSO", ["Entrada"])
        ]
        
        for titulo_grupo, chaves in secoes:
            draw.text((margin, y), titulo_grupo, font=font_header, fill=cor_topo)
            y += 40
            
            for chave in chaves:
                # Pergunta (chave) e Resposta (valor)
                valor = dados.get(chave, "-")
                
                # Desenha o rótulo (ex: "Lixo:")
                draw.text((margin, y), f"{chave}:", font=font_header, fill="#444")
                y += 35
                
                # Desenha a resposta com quebra de linha
                linhas = textwrap.wrap(str(valor), width=55)
                for linha in linhas:
                    draw.text((margin, y), linha, font=font_text, fill="#666")
                    y += 30
                y += 15
            
            y += 10
            draw.line([(margin, y), (width-margin, y)], fill="#eee", width=2)
            y += 30

    # ---------------------------------------------------------
    # LAYOUT 2: ROTINA (Dia a Dia)
    # ---------------------------------------------------------
    else:
        # Destaque para Hóspedes
        draw.rectangle([(margin, y), (width-margin, y+130)], fill="#f1f8e9", outline="#2e7d32", width=2)
        draw.text((margin+20, y+20), "👥 NÚMERO DE HÓSPEDES:", font=font_header, fill="#2e7d32")
        draw.text((margin+20, y+60), str(dados['Hóspedes']), font=font_big, fill="#333")
        
        y += 170
        
        # Observações Específicas
        draw.text((margin, y), "⚠️ OBSERVAÇÕES / PEDIDOS:", font=font_header, fill="#d84315")
        y += 40
        
        obs_texto = dados.get('Obs', '')
        if not obs_texto: obs_texto = "Seguir o padrão da Ficha do Imóvel."
        
        linhas = textwrap.wrap(obs_texto, width=50)
        for linha in linhas:
            draw.text((margin, y), linha, font=font_text, fill="#333")
            y += 35

    # Rodapé
    draw.text((margin, height-50), "Gerado via App de Gestão de Limpeza", font=font_text, fill="#aaa")

    return image

# ==============================================================================
# 2. INTERFACE DO APP
# ==============================================================================
st.title("🧹 Gestão de Limpeza")

# Menu Lateral
with st.sidebar:
    st.header("Menu")
    modo = st.radio("Selecione:", ["📅 1. Rotina (Estadia)", "🏢 2. Ficha do Imóvel (Cadastro)"])
    st.info("Use a **Ficha do Imóvel** para cadastrar as regras fixas. Use a **Rotina** para agendar limpezas pontuais.")

# ------------------------------------------------------------------------------
# MODO 1: ROTINA DA ESTADIA (COM AGENDA)
# ------------------------------------------------------------------------------
if "1." in modo:
    st.subheader("📅 Agendamento de Limpeza")
    
    # Abas para separar a visualização da agenda do preenchimento
    tab_agenda, tab_form = st.tabs(["🔍 Ver Disponibilidade", "📝 Preencher Ordem de Serviço"])
    
    with tab_agenda:
        st.markdown("**Consulte abaixo os dias livres na agenda:**")
        
        # --- CÓDIGO DO CALENDÁRIO ---
        # Substitua 'sandramjo26%40gmail.com' pelo seu ID se for diferente
        # mode=AGENDA deixa em formato de lista (melhor para celular)
        calendar_url = (
            "https://calendar.google.com/calendar/embed?"
            "src=sandramjo26%40gmail.com&ctz=America%2FSao_Paulo"
            "&mode=AGENDA&showTitle=0&showNav=1&showDate=1&showPrint=0"
            "&showTabs=0&showCalendars=0&showTz=0&bgcolor=%23ffffff"
        )
        components.iframe(calendar_url, height=500, scrolling=True)
        st.caption("ℹ️ Se o dia não aparece na lista, ele está livre.")

    with tab_form:
        st.write("Preencha os dados variáveis desta estadia:")
        with st.form("form_rotina"):
            col1, col2 = st.columns(2)
            data_limpeza = col1.date_input("Data da Limpeza", date.today())
            hospedes = col2.text_input("Hóspedes (Qtd):", placeholder="Ex: 2 adultos, 1 bebê")
            
            st.markdown("---")
            obs = st.text_area("Observações Específicas (Opcional):", placeholder="Ex: Atenção à mancha no tapete...")
            
            submit_rotina = st.form_submit_button("🚀 Gerar Ordem (Verde)")
        
        if submit_rotina:
            dados = {
                "Data": data_limpeza.strftime("%d/%m/%Y"),
                "Hóspedes": hospedes if hospedes else "Não informado",
                "Obs": obs
            }
            img = criar_imagem(dados, "rotina")
            st.success("Ordem de Serviço gerada!")
            st.image(img, use_container_width=True)
            
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("⬇️ Baixar Imagem", buf.getvalue(), "ordem_servico.png", "image/png")

# ------------------------------------------------------------------------------
# MODO 2: FICHA DO IMÓVEL (CADASTRO FIXO)
# ------------------------------------------------------------------------------
else:
    st.subheader("🏢 Ficha Técnica (Regras Fixas)")
    st.write("Preencha as orientações fixas do apartamento.")
    
    with st.form("form_imovel"):
        propriedade = st.text_input("Nome/Número do Imóvel:")
        
        st.markdown("### 🛏 QUARTO E BANHO")
        montagem = st.radio("Montagem:", ["Camas Feitas", "Roupas Dobradas"])
        toalhas = st.text_input("Toalhas (Onde deixar?):", placeholder="Cama, Banheiro, Rack...")
        roupa_suja = st.radio("Roupa Suja:", ["Lavar na máquina do apto", "Apenas retirar"])
        
        st.markdown("### 🪣 OPERACIONAL")
        produtos = st.radio("Produtos/Equipamentos:", ["Cliente Fornece", "Prestador Leva"])
        amenities = st.text_input("Amenities (Qtd Padrão):", placeholder="Ex: 2 papéis, 1 sabonete")
        geladeira = st.radio("Geladeira:", ["Descartar tudo", "Manter fechados"])
        lixo = st.text_input("Lixo (Descarte Final):", placeholder="Ex: Lixeira do corredor")
        
        st.markdown("### 🔑 ACESSO")
        entrada = st.text_area("Como será a entrada?", placeholder="Senha, chaves, portaria...")
        
        submit_imovel = st.form_submit_button("💾 Gerar Ficha Técnica (Azul)")
        
    if submit_imovel:
        dados = {
            "Propriedade": propriedade,
            "Montagem": montagem,
            "Toalhas": toalhas,
            "Roupa Suja": roupa_suja,
            "Produtos": produtos,
            "Amenities": amenities,
            "Geladeira": geladeira,
            "Lixo": lixo,
            "Entrada": entrada
        }
        img = criar_imagem(dados, "imovel")
        st.success("Ficha Técnica gerada!")
        st.image(img, use_container_width=True)
        
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        st.download_button("⬇️ Baixar Ficha", buf.getvalue(), "ficha_imovel.png", "image/png")
