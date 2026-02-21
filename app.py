import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap
import base64
import requests 

# --- CONFIGURAÇÕES DO AMBIENTE ---
st.set_page_config(page_title="Gestão de Limpeza Automatizada", page_icon="✨", layout="centered")

# --- INICIALIZAÇÃO DE VARIÁVEIS DE MEMÓRIA (SESSION STATE) ---
if "rua_input" not in st.session_state: st.session_state.rua_input = ""
if "bairro_input" not in st.session_state: st.session_state.bairro_input = ""
if "cidade_uf_input" not in st.session_state: st.session_state.cidade_uf_input = ""

# --- FUNÇÃO DE BUSCA DO CEP ---
def buscar_cep():
    cep_bruto = st.session_state.cep_input
    cep_limpo = cep_bruto.replace("-", "").replace(".", "").replace(" ", "").strip()
    
    st.session_state.cep_input = cep_limpo
    
    if len(cep_limpo) == 8 and cep_limpo.isdigit():
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
    .stApp { background-color: #F4F7F6; font-family: 'Inter', 'Helvetica Neue', sans-serif; }
    div[data-testid="stWidgetLabel"] p, div[data-testid="stWidgetLabel"] span,
    .stMarkdown p, .stText, h1, h2, h3, label { color: #2b2b2b !important; }
    button[data-baseweb="tab"] p, button[data-baseweb="tab"] span, button[data-baseweb="tab"] div { color: #666666 !important; }
    button[data-baseweb="tab"][aria-selected="true"] p, button[data-baseweb="tab"][aria-selected="true"] span, 
    button[data-baseweb="tab"][aria-selected="true"] div { color: #188038 !important; font-weight: bold !important; }
    div[role="radiogroup"] p, div[role="radiogroup"] span, div[role="radiogroup"] div,
    label[data-baseweb="radio"] div { color: #2b2b2b !important; }
    [data-testid="stForm"] { background-color: #FFFFFF !important; border-radius: 20px; padding: 30px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04); border: 1px solid #f0f0f0; }
    .stButton>button { width: 100%; border-radius: 12px; height: 3.5em; font-weight: bold; font-size: 16px; color: #FFFFFF !important; background: linear-gradient(135deg, #34A853 0%, #188038 100%); border: none; box-shadow: 0 4px 10px rgba(24, 128, 56, 0.2); transition: all 0.3s ease; }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 6px 15px rgba(24, 128, 56, 0.3); }
    .stButton>button p, .stButton>button span { color: #FFFFFF !important; }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input { border-radius: 10px !important; border: 1px solid #E0E0E0 !important; background-color: #FAFAFA !important; padding: 12px !important; font-size: 15px !important; color: #2b2b2b !important; }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus { border-color: #34A853 !important; box-shadow: 0 0 0 2px rgba(52, 168, 83, 0.2) !important; }
    [data-baseweb="tab-list"] { background-color: #ffffff; border-radius: 12px; padding: 5px; box-shadow: 0 2px 10px rgba(0,0,0,0.02); gap: 10px; }
    [data-baseweb="tab"] { border-radius: 8px !important; padding: 10px 20px !important; background-color: transparent !important; }
    [data-baseweb="tab"][aria-selected="true"] { background-color: #E8F5E9 !important; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# NOVA FUNÇÃO: QUEBRA DE TEXTO BASEADA EM PIXELS E NÃO EM CARACTERES
# ==============================================================================
def quebrar_texto_por_pixels(texto, fonte, largura_maxima, draw):
    linhas_finais = []
    # Quebra primeiro pelos 'Enters' normais que o usuário deu no campo de texto
    for paragrafo in str(texto).split('\n'):
        if not paragrafo.strip():
            linhas_finais.append("")
            continue
            
        palavras = paragrafo.split()
        if not palavras:
            continue
            
        linha_atual = palavras[0]
        
        for palavra in palavras[1:]:
            linha_teste = f"{linha_atual} {palavra}"
            
            # Mede a largura real em pixels da tentativa
            try:
                # Método seguro e moderno do Pillow
                w = draw.textlength(linha_teste, font=fonte)
            except AttributeError:
                try:
                    w = draw.textbbox((0, 0), linha_teste, font=fonte)[2]
                except AttributeError:
                    w = draw.textsize(linha_teste, font=fonte)[0]
            
            # Se couber na margem, aceita a palavra na linha. Se não, joga pra baixo.
            if w <= largura_maxima:
                linha_atual = linha_teste
            else:
                linhas_finais.append(linha_atual)
                linha_atual = palavra
                
        linhas_finais.append(linha_atual)
    return linhas_finais

# ==============================================================================
# FUNÇÃO: GERAÇÃO TÉCNICA DE IMAGEM
# ==============================================================================
def criar_imagem_profissional(dados, tipo):
    width = 850
    # Aumentado o limite do canvas para evitar cortes. O excesso é removido no crop final.
    height = 8000 
    
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font_alert = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_watermark = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 20) # Reduzido levemente para caber melhor as perguntas
        font_text = ImageFont.truetype("DejaVuSans.ttf", 20)
    except:
        font_alert = font_watermark = font_title = font_header = font_text = ImageFont.load_default()

    altura_alerta = 50
    draw.rectangle([(0, 0), (width, altura_alerta)], fill="#d32f2f")
    texto_alerta = "🚨 DOCUMENTO VÁLIDO APENAS SE ENVIADO PARA SANDRA: (21) 96929-3505"
    
    try:
        bbox_alert = draw.textbbox((0, 0), texto_alerta, font=font_alert)
        tw_alert, th_alert = bbox_alert[2], bbox_alert[3]
    except AttributeError:
        tw_alert, th_alert = draw.textsize(texto_alerta, font=font_alert)
        
    draw.text(((width - tw_alert) / 2, (altura_alerta - th_alert) / 2), texto_alerta, font=font_alert, fill="white")
    offset_y = altura_alerta

    if tipo == "imovel":
        cor_topo, titulo = "#01579b", "FICHA TÉCNICA DO IMÓVEL"
        subtitulo = f"Propriedade Identificada: {dados.get('nome_prop', '-')}"
    else:
        cor_topo, titulo = "#188038", "ORDEM DE SERVIÇO OPERACIONAL"
        subtitulo = f"Cronograma: {dados.get('data_limpeza', '-')}"

    # O topo com título azul/verde também precisa tratar o tamanho do subtítulo (para não vazar)
    draw.rectangle([(0, offset_y), (width, 160 + offset_y)], fill=cor_topo)
    draw.text((45, 45 + offset_y), titulo, font=font_title, fill="white")
    
    sub_linhas = quebrar_texto_por_pixels(subtitulo, font_text, width - 90, draw)
    sub_y = 105 + offset_y
    for s_linha in sub_linhas:
        draw.text((45, sub_y), s_linha, font=font_text, fill="#e1f5fe")
        sub_y += 25

    y_pos, margin = 200 + offset_y, 45
    largura_maxima_texto = width - (margin * 2)

    for categoria, campos in dados.get("categorias", []):
        draw.text((margin, y_pos), categoria, font=font_header, fill=cor_topo)
        y_pos += 40
        
        for pergunta, resposta in campos:
            val_str = str(resposta).strip()
            if not val_str:
                val_str = "Não informado"
                
            # 1. Escreve a Pergunta (Quebrada por Pixels)
            linhas_pergunta = quebrar_texto_por_pixels(f"Pergunta: {pergunta}", font_header, largura_maxima_texto, draw)
            for linha in linhas_pergunta:
                draw.text((margin, y_pos), linha, font=font_header, fill="#424242")
                y_pos += 25 # Espaçamento da pergunta
                
            y_pos += 5 # Respiro entre pergunta e resposta
            
            # 2. Escreve a Resposta (Quebrada por Pixels)
            linhas_resposta = quebrar_texto_por_pixels(f"👉 Resposta: {val_str}", font_text, largura_maxima_texto, draw)
            for linha in linhas_resposta:
                draw.text((margin, y_pos), linha, font=font_text, fill="#188038") # Cor destacada para a resposta
                y_pos += 25
            
            y_pos += 25 # Espaçamento extra para o próximo campo
            
        draw.line([(margin, y_pos), (width-margin, y_pos)], fill="#eeeeee", width=2)
        y_pos += 25

    draw.text((margin, y_pos + 20), "Documento Gerado por Ecossistema Digital de Limpeza", font=font_text, fill="#bdbdbd")

    texto_wm = "ENVIAR PARA SANDRA\n(21) 96929-3505"
    watermark_img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
    draw_wm = ImageDraw.Draw(watermark_img)
    
    try:
        bbox_wm = draw_wm.multiline_textbbox((0, 0), texto_wm, font=font_watermark, align='center')
        wm_width = bbox_wm[2] - bbox_wm[0]
        wm_height = bbox_wm[3] - bbox_wm[1]
    except AttributeError:
        wm_width, wm_height = draw_wm.textsize(texto_wm, font=font_watermark)
        
    draw_wm.multiline_text(((width - wm_width) / 2, (height - wm_height) / 2), 
                           texto_wm, font=font_watermark, fill=(150, 150, 150, 70), align='center')
    
    rotacionada = watermark_img.rotate(30, resample=Image.BICUBIC)
    image = Image.alpha_composite(image, rotacionada)
    
    # Corta exatamente onde as respostas terminaram
    image = image.crop((0, 0, width, y_pos + 80))
    
    return image.convert("RGB")

# ==============================================================================
# FUNÇÃO: COMPARTILHAMENTO
# ==============================================================================
def injetar_botao_compartilhar(img, texto_corpo, nome_arquivo="ordem_servico.png"):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    b64_data = base64.b64encode(buffered.getvalue()).decode()
    
    js_interface = f"""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 10px; font-family: 'Inter', sans-serif; margin-top: 20px;">
        <div style="background-color: #FFF8E1; color: #F57F17; padding: 12px; border-radius: 10px; font-size: 14px; border: 1px solid #FFECB3; width: 100%; text-align: center; font-weight: 500;">
            ✨ Lembre-se de enviar para <strong>Sandra: (21) 96929-3505</strong>
        </div>
        <button id="btnShare" style="
            background: linear-gradient(135deg, #25D366 0%, #128C7E 100%); color: white; border: none; padding: 16px 28px; 
            border-radius: 12px; font-weight: bold; cursor: pointer; width: 100%; 
            font-size: 17px; box-shadow: 0 4px 12px rgba(37,211,102,0.3); transition: 0.2s;">
            <span style="display: flex; align-items: center; justify-content: center; gap: 10px; color: white;">
                <svg width="22" height="22" fill="white" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0.16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L0 24l6.335-1.662c1.72.937 3.659 1.432 5.63 1.433h.005c6.554 0 11.89-5.335 11.893-11.892a11.826 11.826 0 00-3.483-8.417"/></svg>
                Enviar Documento pelo WhatsApp
            </span>
        </button>
        <span id="txtStatus" style="font-size: 12px; color: #888; margin-top: 5px;"></span>
    </div>

    <script>
    async function dispararCompartilhamento() {{
        const b64 = "{b64_data}";
        const status = document.getElementById("txtStatus");
        status.innerText = "Preparando arquivo para a Sandra...";
        
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
                status.innerText = "Tudo pronto! Selecione o contato da Sandra.";
            }} else {{
                status.innerText = "Ops! Seu navegador não suporta enviar a imagem direto.";
            }}
        }} catch (e) {{
            status.innerText = "Erro no compartilhamento: " + e.message;
            console.error(e);
        }}
    }}
    document.getElementById("btnShare").onclick = dispararCompartilhamento;
    </script>
    """
    components.html(js_interface, height=140)

# ==============================================================================
# INTERFACE DO USUÁRIO
# ==============================================================================
st.markdown("<h1 style='text-align: center; color: #188038; margin-bottom: 5px;'>✨ App da Sandra</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 16px; margin-bottom: 30px;'>Organização e qualidade para deixar tudo impecável!</p>", unsafe_allow_html=True)

tab_imovel, tab_rotina = st.tabs(["🏢 Ficha do Imóvel", "📅 Solicitação de Limpeza"])

# --- ABA 1: FICHA DO IMÓVEL ---
with tab_imovel:
    st.info("Olá! Para eu deixar tudo impecável e seguir exatamente o seu padrão de qualidade (e não te incomodar com perguntas bem na hora da limpeza), preparei este ficha de cadastro de imóvel. Sei que são várias perguntas, mas respondendo isso uma única vez, eu salvo no meu sistema e sigo sempre o seu jeito! Quando puder, me confirma? 🥰✨")
    
    st.markdown("### 🔎 Cadastro do Imóvel - Digite o CEP abaixo")
        
    i_cep = st.text_input("CEP", label_visibility="collapsed", key="cep_input", on_change=buscar_cep)
    st.markdown("<div style='background-color: #E8F5E9; padding: 15px; border-radius: 10px; margin-bottom: 15px;'><span style='color: #188038; font-weight: bold;'>💡 Dica de Ouro:</span> Caso não saiba o CEP, <strong>ignore esse campo e continue o preenchimento do restante da ficha</strong>. Porém, se você souber, facilitará o preenchimento, pois o endereço será preenchido automaticamente na ficha abaixo!</div>", unsafe_allow_html=True)
    
    with st.form("form_imovel"):
        st.markdown("### 📍 1. Identificação do Imóvel")
              
        i_rua = st.text_input("Logradouro (Rua, Avenida, etc.)", key="rua_input")
        
        col_end1, col_end2 = st.columns(2)
        with col_end1:
            i_bairro = st.text_input("Bairro", key="bairro_input")
        with col_end2:
            i_cidade_uf = st.text_input("Cidade / UF", key="cidade_uf_input")
            
        st.markdown("<br>⬇️ **Faltam apenas estes dois campos de endereço:**", unsafe_allow_html=True)
        col_end3, col_end4 = st.columns(2)
        with col_end3:
            i_num = st.text_input("Número 🔢")
        with col_end4:
            i_comp = st.text_input("Complemento (Casa, Apto, Bloco...)")

        i_cond = st.text_input("Qual é o nome do Edifício ou Condomínio? 🏢 (Ex: Rio Wonder)")
        i_prop = st.text_input("Qual o nome do proprietário ou responsável por esse imóvel? 👤")
        
        st.write("") 
        st.markdown("### 🧹 2. Equipamentos, Climatização e Materiais")
        i_aspirador = st.text_input("Aí no apartamento tem um aspirador de pó funcionando direitinho? Ah, e a voltagem das tomadas é 110v ou 220v? 🔌")
        i_materiais = st.text_input("Posso contar com vassoura, rodo, balde, panos e escadinha aí no apto?")
        i_produtos = st.text_input("Sobre os produtos de limpeza: prefere que eu use o meu kit ou você fornece? Se você deixa os produtos, há alguma instrução especial de como gosta que os use? Ex: 'Tenho um Cheirinho de Ambiente específico que deixo aí. Peço que passe o spray nas roupas de cama e cortinas'")
        i_proibido = st.text_input("Isso é muito importante: tem algum produto que é PROIBIDO ou que não queira que seja usado nos pisos, nas bancadas ou nos móveis? 🚫")
        i_ventiladores = st.text_input("E sobre os ventiladores: tem ventilador de teto? Se sim, quantos? E de chão, tem algum? 🌬️")
        
        st.write("")
        st.markdown("### 🛏️ 3. Quartos e Roupa de Cama")
        i_guardar = st.text_input("Onde você costuma guardar as roupas de cama e banho limpas? 🧺")
        i_suja = st.text_input("Onde deixo a roupa suja que os hóspedes usaram? ")
        i_montar = st.text_area("Como você prefere que eu monte as camas? Quantos travesseiros? Edredom? Lençol de elástico? Peço para me contar com detalhes como é sua forma de trabalho pois cada casa dispõe de itens de cama mesa e banho distintos.")
        
        st.write("")
        st.markdown("### 🚿 4. Banheiros e Amenities")
        i_shampoo = st.text_input("Para o sabonete, shampoo e condicionador: você oferece? Quais oferece e onde ficam os itens de reposição? 🧴")
        i_toalhas = st.text_input("Onde você prefere que eu deixe as toalhas limpas? (Em cima da cama, no rack do banheiro...) Detalhe: Sei fazer arrumações de toalhas")
        
        st.write("")
        st.markdown("### 🍽️ 5. Cozinha e Geladeira")
        i_geladeira = st.text_input("Se tiver sobrado comida ou bebida dos hóspedes anteriores na geladeira, o que eu faço? Jogo tudo fora ou mantenho o que estiver fechado/lacrado? 🧊")
        i_louca = st.text_input("E se deixarem louça suja na pia: eu lavo (e já está incluso no meu serviço) ou você prefere anotar para cobrar uma taxa extra deles?")
        
        st.markdown("<br>Quais eletrodomésticos e equipamentos ficam disponíveis na cozinha para os hóspedes (e que vão precisar da minha atenção na limpeza)? Pode marcar tudo o que tiver na casa: 🍳", unsafe_allow_html=True)
        
        opcoes_cozinha = [
            "Fogão tradicional", "Cooktop", "Forno (elétrico ou a gás)", "Micro-ondas", 
            "Airfryer", "Panela elétrica de arroz", "Panela de pressão elétrica", 
            "Filtro / Purificador de água", "Coifa / Depurador / Exaustor", 
            "Sanduicheira / Grill", "Liquidificador", "Cafeteira", 
            "Torradeira", "Chaleira elétrica", "Batedeira", "Lava-louças"
        ]
        
        col1, col2 = st.columns(2)
        eletros_selecionados = {}
        
        for i, opcao in enumerate(opcoes_cozinha):
            if i % 2 == 0:
                with col1:
                    eletros_selecionados[opcao] = st.checkbox(opcao)
            else:
                with col2:
                    eletros_selecionados[opcao] = st.checkbox(opcao)
                    
        i_eletros_outros = st.text_input("Tem outros equipamentos na cozinha? Se sim, escreva aqui (Ex: Espremedor de laranjas, Nespresso...):")
            
        i_quantitativos = st.text_input("Para a gente manter o controle: você deixa um número exato de pratos, copos e talheres (facas, garfos, colheres de sopa e de sobremesa)? Se sim, me passa as quantidades para eu conferir na hora da limpeza e te avisar se faltar algo! 🍽️")
        i_cozinha = st.text_input("Tem mais algum detalhe na cozinha que eu deva deixar para os hóspedes (sal, açucar) ou algo que queira me contar?")
        
        st.write("")
        st.markdown("### ✨ 6. Finalização e Detalhes")
        i_mimos_guardados = st.text_input("Se houver mimos de boas vindas, (chocolates, biscoitos, etc) onde ficam guardados? (Para eu saber de onde pegar no dia da limpeza) 🍬")
        i_ambiente = st.text_input("Ao terminar e fechar a porta, como devo deixar o ambiente? (Ex: cortinas abertas ou fechadas, luzes acessas ou apagadas?) 🌬️")
        i_lixo = st.text_input("Onde eu faço o descarte final de todo o lixo aí no prédio? 🗑️")
        i_obs_finais = st.text_area("Para fecharmos: deseja acrescentar alguma observação importante ou detalhe sobre o apartamento que ainda não conversamos por aqui? 📝")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_imovel = st.form_submit_button("💾 Gerar Ficha Protegida")
        
    if btn_imovel:
        lista_eletros_texto = []
        for opcao, marcado in eletros_selecionados.items():
            marca = "[ X ]" if marcado else "[   ]"
            lista_eletros_texto.append(f"{marca} {opcao}")
            
        if i_eletros_outros:
            lista_eletros_texto.append(f"[ X ] Outros: {i_eletros_outros}")
        else:
            lista_eletros_texto.append("[   ] Outros")
            
        str_eletros = "\n".join(lista_eletros_texto)

        endereco_final = f"{i_rua}"
        if i_num: endereco_final += f", {i_num}"
        if i_comp: endereco_final += f" - {i_comp}"
        if i_bairro: endereco_final += f" - {i_bairro}"
        if i_cidade_uf: endereco_final += f", {i_cidade_uf}"
        
        cep_display = st.session_state.cep_input
        if cep_display: endereco_final += f" (CEP: {cep_display})"
            
        payload_imovel = {
            "nome_prop": i_prop,
            "categorias": [
                ("📍 IDENTIFICAÇÃO DO IMÓVEL", [
                    ("Qual o nome do proprietário ou responsável por esse imóvel? 👤", i_prop),
                    ("Endereço Completo", endereco_final),
                    ("Qual é o nome do Edifício ou Condomínio? 🏢", i_cond)
                ]),
                ("🧹 EQUIPAMENTOS, CLIMATIZAÇÃO E MATERIAIS", [
                    ("Aí no apartamento tem um aspirador de pó funcionando direitinho? Ah, e a voltagem das tomadas é 110v ou 220v? 🔌", i_aspirador),
                    ("Posso contar com vassoura, rodo, balde, panos e escadinha aí no apto?", i_materiais),
                    ("Sobre os produtos de limpeza: prefere que eu use o meu kit ou você fornece? Se você deixa os produtos, há alguma instrução especial de como gosta que os use?", i_produtos),
                    ("Isso é muito importante: tem algum produto que é PROIBIDO ou que não queira que seja usado nos pisos, nas bancadas ou nos móveis? 🚫", i_proibido),
                    ("E sobre os ventiladores: tem ventilador de teto? Se sim, quantos? E de chão, tem algum? 🌬️", i_ventiladores)
                ]),
                ("🛏️ QUARTOS E ROUPA DE CAMA", [
                    ("Onde você costuma guardar as roupas de cama e banho limpas? 🧺", i_guardar),
                    ("Onde deixo a roupa suja que os hóspedes usaram?", i_suja),
                    ("Como você prefere que eu monte as camas? Quantos travesseiros? Edredom? Lençol de elástico?", i_montar)
                ]),
                ("🚿 BANHEIROS E AMENITIES", [
                    ("Para o sabonete, shampoo e condicionador: você oferece? Quais oferece e onde ficam os itens de reposição? 🧴", i_shampoo),
                    ("Onde você prefere que eu deixe as toalhas limpas? (Em cima da cama, no rack do banheiro...)", i_toalhas)
                ]),
                ("🍽️ COZINHA E GELADEIRA", [
                    ("Se tiver sobrado comida ou bebida dos hóspedes anteriores na geladeira, o que eu faço? Jogo tudo fora ou mantenho o que estiver fechado/lacrado? 🧊", i_geladeira),
                    ("E se deixarem louça suja na pia: eu lavo ou você prefere anotar para cobrar uma taxa extra deles?", i_louca),
                    ("Para a gente manter o controle: você deixa um número exato de pratos, copos e talheres? Se sim, me passa as quantidades:", i_quantitativos),
                    ("Tem mais algum detalhe na cozinha que eu deva deixar para os hóspedes (sal, açucar) ou algo que queira me contar?", i_cozinha),
                    ("Quais eletrodomésticos e equipamentos ficam disponíveis na cozinha para os hóspedes?", str_eletros)
                ]),
                ("✨ FINALIZAÇÃO E DETALHES", [
                    ("Se houver mimos de boas vindas, onde ficam guardados? 🍬", i_mimos_guardados),
                    ("Ao terminar e fechar a porta, como devo deixar o ambiente? (Ex: cortinas abertas ou fechadas, luzes acessas ou apagadas?) 🌬️", i_ambiente),
                    ("Onde eu faço o descarte final de todo o lixo aí no prédio? 🗑️", i_lixo),
                    ("Para fecharmos: deseja acrescentar alguma observação importante ou detalhe sobre o apartamento que ainda não conversamos por aqui? 📝", i_obs_finais)
                ])
            ]
        }

        img_fch = criar_imagem_profissional(payload_imovel, "imovel")
        st.markdown("### Documento Gerado com Sucesso! 🎉")
        st.image(img_fch, use_container_width=True)
        
        msg_fch = f"Ficha Técnica Atualizada: {i_prop}. Muito obrigada por preencher!"
        injetar_botao_compartilhar(img_fch, msg_fch, f"Ficha_{i_prop}.png")

# --- ABA 2: SOLICITAÇÃO DE LIMPEZA ---
with tab_rotina:
    st.markdown("### 🗓️ Visão Geral da Agenda")
    st.markdown("<p style='text-align: center; color: #555; font-size: 15px; margin-bottom: 10px; background-color: #E8F5E9; padding: 10px; border-radius: 8px;'>Para verificar outras semanas ou datas, clique nas setinhas para <strong>&lt; (esquerda)</strong> ou <strong>&gt; (direita)</strong> na parte superior do calendário abaixo.</p>", unsafe_allow_html=True)
    
    cal_url = "https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&mode=WEEK"
    components.iframe(cal_url, height=650, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("form_rotina"):
        st.markdown("### 📝 Nova Solicitação de Serviço")
        st.write("Solicite limpezas abaixo")
        st.markdown("---")
        
        q_cadastro = st.radio("Me tira uma dúvida rápida: a gente já fez a Ficha Técnica desse seu imóvel antes, ou é a nossa primeira vez lá? 📝", ["Já fizemos a Ficha", "Primeira vez"])
        q_ident = st.text_input("Ah, maravilha! Então me lembra só qual é a Torre e o número do apartamento para eu puxar o seu padrão de qualidade aqui? 🏢🚪 (Ex: Torre Formosa, Apto 509)")
        q_data = st.date_input("Qual é a data gostaria de reservar? 🗓️✅", date.today())
        
        st.write("")
        st.markdown("### 🔑 Acesso")
        q_acesso = st.text_area("Como vai ser a minha entrada no dia dessa limpeza? 🔑 (Chave na portaria, senha na porta, cofre...) e se for senha, qual a senha?")
        
        st.write("")
        st.markdown("### 📋 Informações da Reserva")
        q_hospedes = st.text_input("Quantas pessoas entram nessa reserva? 👥 (Pergunto só para eu ter uma ideia do que será necessário preparar)")
        q_banho = st.text_input("Quantas toalhas de banho e de rosto eu devo separar no total? 🛁")
        q_cama = st.text_input("Quantas camas eu preciso preparar dessa vez? E deixo quantos travesseiros e cobertores? Peço que me fale tudo sobre as roupas de cama, incluindo se devo usar cobre leitos, edredoms, etc 🛏️")
        q_amenities = st.text_input("Quantos rolos de papel higiênico, sabonetes e shampoos eu devo deixar no total? 🧻🧴")
        q_mimos = st.text_input("Tem algum 'mimo' especial para essa reserva (chocolates, biscoitos, cápsulas de café)? Quantos eu deixo preparados? 🍬")
        q_notas = st.text_area("Para fecharmos a solicitação: deseja acrescentar alguma observação importante ou pedido especial para essa limpeza que ainda não conversamos? Pode me falar que dependendo do que for eu tento verificar! 😉✨")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_gen = st.form_submit_button("🚀 Gerar Ordem de Serviço de Limpeza")
    
    if btn_gen:
        dt_str = q_data.strftime("%d/%m/%Y")
        payload = {
            "data_limpeza": dt_str,
            "categorias": [
                ("📋 INFORMAÇÕES GERAIS", [
                    ("Me tira uma dúvida rápida: a gente já fez a Ficha Técnica desse seu imóvel antes, ou é a nossa primeira vez lá? 📝", q_cadastro),
                    ("Ah, maravilha! Então me lembra só qual é a Torre e o número do apartamento para eu puxar o seu padrão de qualidade aqui? 🏢🚪", q_ident),
                    ("Qual é a data gostaria de reservar? 🗓️✅", dt_str),
                    ("Quantas pessoas entram nessa reserva? 👥", q_hospedes)
                ]),
                ("🔑 ACESSO E SEGURANÇA", [
                    ("Como vai ser a minha entrada no dia dessa limpeza? 🔑", q_acesso)
                ]),
                ("🧺 ENXOVAL E PREPARAÇÃO", [
                    ("Quantas toalhas de banho e de rosto eu devo separar no total? 🛁", q_banho),
                    ("Quantas camas eu preciso preparar dessa vez? E deixo quantos travesseiros e cobertores? 🛏️", q_cama)
                ]),
                ("🧴 AMENITIES E MIMOS", [
                    ("Quantos rolos de papel higiênico, sabonetes e shampoos eu devo deixar no total? 🧻🧴", q_amenities),
                    ("Tem algum 'mimo' especial para essa reserva (chocolates, biscoitos, cápsulas de café)? Quantos eu deixo preparados? 🍬", q_mimos)
                ]),
                ("⚠️ NOTAS ESPECIAIS", [
                    ("Deseja acrescentar alguma observação importante ou pedido especial para essa limpeza que ainda não conversamos?", q_notas)
                ])
            ]
        }
        
        img_os = criar_imagem_profissional(payload, "rotina")
        st.markdown("### Documento Gerado com Sucesso! 🎉")
        st.image(img_os, use_container_width=True)
        
        msg_whatsapp = f"Olá! Segue a Ordem de Serviço confirmada para o dia {dt_str} no apto {q_ident}."
        injetar_botao_compartilhar(img_os, msg_whatsapp, f"OS_{dt_str.replace('/','-')}.png")
