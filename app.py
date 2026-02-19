import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap
import base64

# --- CONFIGURAÇÕES DO AMBIENTE ---
st.set_page_config(page_title="Gestão de Limpeza Automatizada", page_icon="🧹", layout="centered")

# --- ESTILOS VISUAIS ---
st.markdown("""
    <style>
   .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; background-color: #f0f2f6; transition: 0.3s; }
   .stButton>button:hover { background-color: #e0e2e6; border-color: #2e7d32; }
   .share-container { border: 1px solid #e6e9ef; padding: 20px; border-radius: 15px; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# FUNÇÃO: GERAÇÃO TÉCNICA DE IMAGEM (COM MARCA D'ÁGUA E ALERTA)
# ==============================================================================
def criar_imagem_profissional(dados, tipo):
    # Aumentamos um pouco a altura para acomodar a nova faixa de alerta no topo
    width, height = 800, (1050 if tipo == "imovel" else 800)
    # Criamos a imagem base em RGBA para permitir transparências
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # --- CARREGAMENTO DE FONTES ---
    try:
        # Tenta carregar fontes do sistema (comum em Linux/Servidores)
        font_alert = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_watermark = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
    except:
        # Fallback para fonte padrão se não encontrar as acima
        font_alert = font_watermark = font_title = font_header = font_text = font_big = ImageFont.load_default()

    # --- 1. FAIXA DE ALERTA SUPERIOR ---
    altura_alerta = 50
    draw.rectangle([(0, 0), (width, altura_alerta)], fill="#d32f2f") # Faixa vermelha
    texto_alerta = "🚨 DOCUMENTO VÁLIDO APENAS SE ENVIADO PARA SANDRA: (21) 96929-3505"
    # Cálculo para centralizar o texto do alerta
    bbox_alert = draw.textbbox((0, 0), texto_alerta, font=font_alert)
    tw_alert, th_alert = bbox_alert[2], bbox_alert[3]
    draw.text(((width - tw_alert) / 2, (altura_alerta - th_alert) / 2), texto_alerta, font=font_alert, fill="white")

    # Define um offset (deslocamento) para tudo que vier abaixo da faixa de alerta
    offset_y = altura_alerta

    # --- 2. CONTEÚDO PRINCIPAL ---
    # Definição de paleta cromática por contexto
    if tipo == "imovel":
        cor_topo, titulo = "#01579b", "FICHA TÉCNICA DO IMÓVEL"
        subtitulo = f"Propriedade Identificada: {dados.get('Propriedade', '-')}"
    else:
        cor_topo, titulo = "#1b5e20", "ORDEM DE SERVIÇO OPERACIONAL"
        subtitulo = f"Cronograma: {dados.get('Data', '-')}"

    # Cabeçalho Principal (Deslocado pelo offset_y)
    draw.rectangle([(0, offset_y), (width, 160 + offset_y)], fill=cor_topo)
    draw.text((45, 45 + offset_y), titulo, font=font_title, fill="white")
    draw.text((45, 105 + offset_y), subtitulo, font=font_text, fill="#e1f5fe")

    y_pos, margin = 200 + offset_y, 50

    if tipo == "imovel":
        categorias = [
            ("🛏️ QUARTO E ROUPARIA", ["Montagem", "Toalhas", "Roupa Suja"]),
            ("🪣 PROTOCOLO OPERACIONAL", ["Produtos", "Amenities", "Geladeira", "Lixo"]),
            ("🔑 LOGÍSTICA DE ACESSO", ["Entrada"])
        ]
        for cat_nome, campos in categorias:
            draw.text((margin, y_pos), cat_nome, font=font_header, fill=cor_topo)
            y_pos += 45
            for campo in campos:
                val = dados.get(campo, "-")
                draw.text((margin, y_pos), f"{campo}:", font=font_header, fill="#424242")
                y_pos += 35
                for linha in textwrap.wrap(str(val), width=58):
                    draw.text((margin, y_pos), linha, font=font_text, fill="#757575")
                    y_pos += 30
                y_pos += 15
            draw.line([(margin, y_pos), (width-margin, y_pos)], fill="#eeeeee", width=2)
            y_pos += 30
    else:
        # Layout para Rotina de Estadia
        draw.rectangle([(margin, y_pos), (width-margin, y_pos+140)], fill="#f1f8e9", outline="#388e3c", width=2)
        draw.text((margin+25, y_pos+25), "👥 VOLUME DE HÓSPEDES:", font=font_header, fill="#2e7d32")
        draw.text((margin+25, y_pos+65), str(dados['Hóspedes']), font=font_big, fill="#212121")
        y_pos += 180
        draw.text((margin, y_pos), "⚠️ INSTRUÇÕES ESPECÍFICAS:", font=font_header, fill="#bf360c")
        y_pos += 45
        obs = dados.get('Obs', '') or "Seguir rigorosamente o padrão da Ficha do Imóvel."
        for ln in textwrap.wrap(obs, width=52):
            draw.text((margin, y_pos), ln, font=font_text, fill="#212121")
            y_pos += 35

    draw.text((margin, height-60), "Documento Gerado por Ecossistema Digital de Limpeza", font=font_text, fill="#bdbdbd")

    # --- 3. MARCA D'ÁGUA DIAGONAL ---
    # Cria uma nova imagem transparente para a marca d'água
    texto_wm = "ENVIAR PARA SANDRA\n(21) 96929-3505"
    watermark_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw_wm = ImageDraw.Draw(watermark_img)
    
    # Calcula o tamanho do texto da marca d'água para centralizar
    bbox_wm = draw_wm.multiline_textbbox((0, 0), texto_wm, font=font_watermark, align='center')
    wm_width = bbox_wm[2] - bbox_wm[0]
    wm_height = bbox_wm[3] - bbox_wm[1]
    
    # Desenha o texto no centro da imagem transparente
    # Cor cinza claro (150,150,150) com transparência alpha (90 de 255)
    draw_wm.multiline_text(((width - wm_width) / 2, (height - wm_height) / 2), 
                           texto_wm, font=font_watermark, fill=(150, 150, 150, 90), align='center')
    
    # Rotaciona a imagem da marca d'água
    rotacionada = watermark_img.rotate(30, resample=Image.BICUBIC)
    
    # Combina a imagem original com a marca d'água rotacionada
    image = Image.alpha_composite(image, rotacionada)

    # Converte de volta para RGB para salvar como PNG (remove o canal alpha final)
    return image.convert("RGB")

# ==============================================================================
# FUNÇÃO: COMPONENTE DE COMPARTILHAMENTO NATIVO (WEB SHARE API)
# ==============================================================================
# (Esta função foi revertida para a versão original que anexa imagem)
def injetar_botao_compartilhar(img, texto_corpo, nome_arquivo="ordem_servico.png"):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64_data = base64.b64encode(buffered.getvalue()).decode()
    
    js_interface = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; font-family: sans-serif; margin-top: 20px;">
        <div style="background-color: #fff3cd; color: #856404; padding: 10px; border-radius: 8px; font-size: 14px; border: 1px solid #ffeeba; width: 100%; text-align: center;">
           ⚠️ Lembre-se de enviar para <strong>Sandra: (21) 96929-3505</strong>
        </div>
        <button id="btnShare" style="
            background-color: #25D366; color: white; border: none; padding: 14px 28px; 
            border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; 
            font-size: 17px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: 0.2s;">
            <span style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <svg width="22" height="22" fill="white" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0.16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L0 24l6.335-1.662c1.72.937 3.659 1.432 5.63 1.433h.005c6.554 0 11.89-5.335 11.893-11.892a11.826 11.826 0 00-3.483-8.417"/></svg>
                Compartilhar Documento (Anexar)
            </span>
        </button>
        <span id="txtStatus" style="font-size: 11px; color: #888;"></span>
    </div>

    <script>
    async function dispararCompartilhamento() {{
        const b64 = "{b64_data}";
        const status = document.getElementById("txtStatus");
        status.innerText = "Preparando arquivo...";
        
        try {{
            const res = await fetch("data:image/png;base64," + b64);
            const blob = await res.blob();
            const file = new File([blob], "{nome_arquivo}", {{ type: "image/png" }});
            
            const shareData = {{
                title: "Documentação de Limpeza",
                text: "{texto_corpo} - *Documento válido apenas se enviado para Sandra: (21) 96929-3505*",
                files: [file]
            }};

            if (navigator.canShare && navigator.canShare(shareData)) {{
                await navigator.share(shareData);
                status.innerText = "Compartilhamento iniciado. Selecione o contato de Sandra.";
            }} else {{
                status.innerText = "Seu navegador não suporta o compartilhamento direto de arquivos.";
            }}
        }} catch (e) {{
            status.innerText = "Erro no compartilhamento: " + e.message;
            console.error(e);
        }}
    }}
    document.getElementById("btnShare").onclick = dispararCompartilhamento;
    </script>
    """
    components.html(js_interface, height=130)

# ==============================================================================
# INTERFACE DO USUÁRIO
# ==============================================================================
st.title("🧹 Gestão de Limpeza")

# Menus Superiores usando Tabs (Mantido conforme pedido anterior)
tab_rotina, tab_imovel = st.tabs(["📅 Rotina Operacional", "🏢 Ficha do Imóvel"])

with tab_rotina:
    st.subheader("Visão Geral da Agenda")
    cal_url = "https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&mode=AGENDA"
    components.iframe(cal_url, height=400, scrolling=True)

    st.markdown("---")
    st.subheader("Nova Ordem de Serviço")
    with st.form("form_rotina"):
        c1, c2 = st.columns(2)
        dt = c1.date_input("Data da Limpeza", date.today())
        hs = c2.text_input("Quantidade de Hóspedes:")
        ob = st.text_area("Notas Especiais (Ex: Manutenção de ar condicionado)")
        btn_gen = st.form_submit_button("🚀 Gerar Ordem com Segurança")
    
    if btn_gen:
        payload = {"Data": dt.strftime("%d/%m/%Y"), "Hóspedes": hs or "Não informado", "Obs": ob}
        # Gera a imagem com as novas marcas d'água
        img_os = criar_imagem_profissional(payload, "rotina")
        st.image(img_os, use_container_width=True)
        
        msg_whatsapp = f"Olá! Segue a Ordem de Serviço para o dia {payload['Data']}. Hóspedes: {payload['Hóspedes']}."
        # Usa o botão de compartilhamento nativo (que anexa a imagem)
        injetar_botao_compartilhar(img_os, msg_whatsapp, f"OS_{payload['Data'].replace('/','-')}.png")

with tab_imovel:
    st.subheader("Cadastro de Regras Fixas")
    with st.form("form_imovel"):
        prop = st.text_input("Nome/Código do Imóvel:")
        st.markdown("---")
        c1, c2 = st.columns(2)
        mnt = c1.radio("Montagem das Camas:", ["Padrão", "Camas Separadas"])
        tua = c2.text_input("Localização das Toalhas:", placeholder="Ex: Prateleira superior")
        rps = c1.radio("Processamento de Roupa Suja:", ["Lavar no Local", "Recolher p/ Lavanderia"])
        prd = c2.radio("Fornecimento de Insumos:", ["Proprietário", "Prestador"])
        amn = st.text_input("Amenities (Quantidade):", placeholder="Ex: 2 sabonetes, 1 shampoo")
        gel = st.radio("Protocolo Geladeira:", ["Esvaziar e limpar", "Manter itens lacrados"])
        lxo = st.text_input("Ponto de Descarte de Lixo:")
        ent = st.text_area("Protocolo de Acesso (Senhas/Chaves):")
        btn_imovel = st.form_submit_button("💾 Gerar Ficha Protegida")
        
    if btn_imovel:
        dados_imovel = {
            "Propriedade": prop, "Montagem": mnt, "Toalhas": tua, "Roupa Suja": rps,
            "Produtos": prd, "Amenities": amn, "Geladeira": gel, "Lixo": lxo, "Entrada": ent
        }
        # Gera a imagem com as novas marcas d'água
        img_fch = criar_imagem_profissional(dados_imovel, "imovel")
        st.image(img_fch, use_container_width=True)
        
        msg_fch = f"Ficha Técnica Atualizada: {prop}. Seguir os protocolos da imagem."
        # Usa o botão de compartilhamento nativo
        injetar_botao_compartilhar(img_fch, msg_fch, f"Ficha_{prop}.png")
