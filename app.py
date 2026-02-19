import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont
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
# FUNÇÃO: GERAÇÃO TÉCNICA DE IMAGEM (PILLOW)
# ==============================================================================
def criar_imagem_profissional(dados, tipo):
    width, height = 800, (1000 if tipo == "imovel" else 750)
    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    # Carregamento de tipografia robusta
    try:
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 26)
        font_text = ImageFont.truetype("DejaVuSans.ttf", 24)
        font_big = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
    except:
        font_title = font_header = font_text = font_big = ImageFont.load_default()

    # Definição de paleta cromática por contexto
    if tipo == "imovel":
        cor_topo, titulo = "#01579b", "FICHA TÉCNICA DO IMÓVEL"
        subtitulo = f"Propriedade Identificada: {dados.get('Propriedade', '-')}"
    else:
        cor_topo, titulo = "#1b5e20", "ORDEM DE SERVIÇO OPERACIONAL"
        subtitulo = f"Cronograma: {dados.get('Data', '-')}"

    draw.rectangle([(0, 0), (width, 160)], fill=cor_topo)
    draw.text((45, 45), titulo, font=font_title, fill="white")
    draw.text((45, 105), subtitulo, font=font_text, fill="#e1f5fe")

    y_pos, margin = 200, 50

    if tipo == "imovel":
        # Correção da sintaxe e definição das categorias
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
    return image

# ==============================================================================
# FUNÇÃO: COMPONENTE DE COMPARTILHAMENTO NATIVO (WEB SHARE API)
# ==============================================================================
def injetar_botao_compartilhar(img, texto_corpo, nome_arquivo="ordem_servico.png"):
    # Conversão de imagem para Base64 para trânsito via WebSocket
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64_data = base64.b64encode(buffered.getvalue()).decode()
    
    # Injeção de JavaScript corrigida (Removido artefato displ[span_15]...)
    js_interface = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; font-family: sans-serif;">
        <button id="btnShare" style="
            background-color: #25D366; color: white; border: none; padding: 14px 28px; 
            border-radius: 10px; font-weight: bold; cursor: pointer; width: 100%; 
            font-size: 17px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); transition: 0.2s;">
            <span style="display: flex; align-items: center; justify-content: center; gap: 8px;">
                <svg width="22" height="22" fill="white" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0.16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L0 24l6.335-1.662c1.72.937 3.659 1.432 5.63 1.433h.005c6.554 0 11.89-5.335 11.893-11.892a11.826 11.826 0 00-3.483-8.417"/></svg>
                Compartilhar Ordem no WhatsApp
            </span>
        </button>
        <span id="txtStatus" style="font-size: 11px; color: #888;"></span>
    </div>

    <script>
    async function dispararCompartilhamento() {{
        const b64 = "{b64_data}";
        const status = document.getElementById("txtStatus");
        
        try {{
            const res = await fetch("data:image/png;base64," + b64);
            const blob = await res.blob();
            const file = new File([blob], "{nome_arquivo}", {{ type: "image/png" }});
            
            const shareData = {{
                title: "Documentação de Limpeza",
                text: "{texto_corpo}",
                files: [file]
            }};

            if (navigator.canShare && navigator.canShare(shareData)) {{
                await navigator.share(shareData);
                status.innerText = "Operação concluída.";
            }} else {{
                status.innerText = "Ambiente não suporta compartilhamento de arquivos.";
            }}
        }} catch (e) {{
            status.innerText = "Erro: " + e.message;
        }}
    }}
    document.getElementById("btnShare").onclick = dispararCompartilhamento;
    </script>
    """
    components.html(js_interface, height=100)

# ==============================================================================
# INTERFACE DO USUÁRIO
# ==============================================================================
st.title("🧹 Gestão de Limpeza")

with st.sidebar:
    st.header("Navegação")
    # Adicionadas as opções na estrutura radio
    opcao = st.radio("Selecione o Fluxo:", ["Rotina Operacional", "Ficha do Imóvel"])

if "Rotina" in opcao:
    st.subheader("📅 Agendamento Operacional")
    # Adicionados os nomes das abas
    tab_vis, tab_form = st.tabs(["Calendário", "Nova Ordem"])
    
    with tab_vis:
        cal_url = "https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&mode=AGENDA"
        components.iframe(cal_url, height=500, scrolling=True)

    with tab_form:
        with st.form("form_rotina"):
            c1, c2 = st.columns(2)
            dt = c1.date_input("Data da Limpeza", date.today())
            hs = c2.text_input("Quantidade de Hóspedes:")
            ob = st.text_area("Notas Especiais (Ex: Manutenção de ar condicionado)")
            btn_gen = st.form_submit_button("🚀 Gerar e Compartilhar")
        
        if btn_gen:
            payload = {"Data": dt.strftime("%d/%m/%Y"), "Hóspedes": hs or "Não informado", "Obs": ob}
            img_os = criar_imagem_profissional(payload, "rotina")
            st.image(img_os, use_container_width=True)
            
            # Corrigido o erro ao usar format() diretamente no objeto do dicionário (payload)
            msg_whatsapp = f"Olá! Segue a Ordem de Serviço para o dia {payload['Data']}. Hóspedes: {payload['Hóspedes']}. Observações: {payload['Obs']}"
            injetar_botao_compartilhar(img_os, msg_whatsapp, f"OS_{payload['Data'].replace('/','-')}.png")

else:
    st.subheader("🏢 Ficha de Regras Fixas")
    with st.form("form_imovel"):
        prop = st.text_input("Nome/Código do Imóvel:")
        st.markdown("---")
        c1, c2 = st.columns(2)
        # Adicionadas as opções aos itens
        mnt = c1.radio("Montagem das Camas:", ["Padrão", "Camas Separadas"])
        tua = c2.text_input("Localização das Toalhas:", placeholder="Ex: Prateleira superior")
        rps = c1.radio("Processamento de Roupa Suja:", ["Lavar no Local", "Recolher p/ Lavanderia"])
        prd = c2.radio("Fornecimento de Insumos:", ["Proprietário", "Prestador"])
        amn = st.text_input("Amenities (Quantidade):", placeholder="Ex: 2 sabonetes, 1 shampoo")
        gel = st.radio("Protocolo Geladeira:", ["Esvaziar e limpar", "Manter itens lacrados"])
        lxo = st.text_input("Ponto de Descarte de Lixo:")
        ent = st.text_area("Protocolo de Acesso (Senhas/Chaves):")
        btn_imovel = st.form_submit_button("💾 Salvar e Compartilhar Ficha")
        
    if btn_imovel:
        dados_imovel = {
            "Propriedade": prop, "Montagem": mnt, "Toalhas": tua, "Roupa Suja": rps,
            "Produtos": prd, "Amenities": amn, "Geladeira": gel, "Lixo": lxo, "Entrada": ent
        }
        img_fch = criar_imagem_profissional(dados_imovel, "imovel")
        st.image(img_fch, use_container_width=True)
        
        msg_fch = f"Ficha Técnica Atualizada: {prop}. Favor seguir os protocolos em anexo para todas as limpezas neste imóvel."
        injetar_botao_compartilhar(img_fch, msg_fch, f"Ficha_{prop}.png")
