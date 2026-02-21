import streamlit as st
import streamlit.components.v1 as components
from datetime import datetime, date
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import textwrap
import base64

# --- CONFIGURAÇÕES DO AMBIENTE ---
st.set_page_config(page_title="Gestão de Limpeza Automatizada", page_icon="✨", layout="centered")

# --- ESTILOS VISUAIS (O "BANHO DE LOJA" CORRIGIDO) ---
st.markdown("""
    <style>
    /* Força um fundo claro na tela inteira */
    .stApp {
        background-color: #F4F7F6;
        font-family: 'Inter', 'Helvetica Neue', sans-serif;
    }
    
    /* 🔴 CORREÇÃO AQUI: Força TODOS os textos das perguntas a ficarem escuros! */
    div[data-testid="stWidgetLabel"] p, 
    div[data-testid="stWidgetLabel"] span,
    div[data-baseweb="radio"] p,
    div[data-baseweb="tab"] p,
    .stMarkdown p,
    .stText,
    h1, h2, h3, label {
        color: #2b2b2b !important;
    }

    /* Customiza os formulários para parecerem 'Cartões' */
    [data-testid="stForm"] {
        background-color: #FFFFFF !important;
        border-radius: 20px;
        padding: 30px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
        border: 1px solid #f0f0f0;
    }

    /* Estiliza os botões principais (A letra do botão continua branca!) */
    .stButton>button { 
        width: 100%; 
        border-radius: 12px; 
        height: 3.5em; 
        font-weight: bold; 
        font-size: 16px;
        color: #FFFFFF !important; 
        background: linear-gradient(135deg, #34A853 0%, #188038 100%);
        border: none;
        box-shadow: 0 4px 10px rgba(24, 128, 56, 0.2);
        transition: all 0.3s ease; 
    }
    .stButton>button:hover { 
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(24, 128, 56, 0.3);
    }
    /* Garante que o texto DENTRO do botão fique branco */
    .stButton>button p, .stButton>button span {
        color: #FFFFFF !important;
    }

    /* Estiliza as caixas de texto (onde a pessoa digita) */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea, .stDateInput>div>div>input {
        border-radius: 10px !important;
        border: 1px solid #E0E0E0 !important;
        background-color: #FAFAFA !important;
        padding: 12px !important;
        font-size: 15px !important;
        color: #2b2b2b !important; /* Cor do texto digitado */
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #34A853 !important;
        box-shadow: 0 0 0 2px rgba(52, 168, 83, 0.2) !important;
    }

    /* Estiliza as Abas (Tabs) */
    [data-baseweb="tab-list"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 5px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.02);
        gap: 10px;
    }
    [data-baseweb="tab"] {
        border-radius: 8px !important;
        padding: 10px 20px !important;
        background-color: transparent !important;
    }
    [data-baseweb="tab"][aria-selected="true"] {
        background-color: #E8F5E9 !important;
    }
    [data-baseweb="tab"][aria-selected="true"] p {
        color: #188038 !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# FUNÇÃO: GERAÇÃO TÉCNICA DE IMAGEM
# ==============================================================================
def criar_imagem_profissional(dados, tipo):
    width = 850
    height = 2800 if tipo == "imovel" else 1500
    
    image = Image.new("RGBA", (width, height), "white")
    draw = ImageDraw.Draw(image)

    try:
        font_alert = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
        font_watermark = ImageFont.truetype("DejaVuSans-Bold.ttf", 55)
        font_title = ImageFont.truetype("DejaVuSans-Bold.ttf", 45)
        font_header = ImageFont.truetype("DejaVuSans-Bold.ttf", 22)
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

    draw.rectangle([(0, offset_y), (width, 160 + offset_y)], fill=cor_topo)
    draw.text((45, 45 + offset_y), titulo, font=font_title, fill="white")
    draw.text((45, 105 + offset_y), subtitulo, font=font_text, fill="#e1f5fe")

    y_pos, margin = 200 + offset_y, 45

    for categoria, campos in dados.get("categorias", []):
        draw.text((margin, y_pos), categoria, font=font_header, fill=cor_topo)
        y_pos += 40
        for rotulo, valor in campos:
            val_str = str(valor) if valor else "Não informado"
            draw.text((margin, y_pos), f"{rotulo}:", font=font_header, fill="#424242")
            y_pos += 30
            for linha in textwrap.wrap(val_str, width=80):
                draw.text((margin, y_pos), linha, font=font_text, fill="#757575")
                y_pos += 25
            y_pos += 15
        draw.line([(margin, y_pos), (width-margin, y_pos)], fill="#eeeeee", width=2)
        y_pos += 25

    draw.text((margin, height-60), "Documento Gerado por Ecossistema Digital de Limpeza", font=font_text, fill="#bdbdbd")

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
    image = image.crop((0, 0, width, min(y_pos + 100, height)))
    
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

tab_rotina, tab_imovel = st.tabs(["📅 Rotina Operacional", "🏢 Ficha do Imóvel"])

# --- ABA 1: ROTINA OPERACIONAL ---
with tab_rotina:
    st.markdown("### 🗓️ Visão Geral da Agenda")
    cal_url = "https://calendar.google.com/calendar/embed?src=sandramjo26%40gmail.com&mode=AGENDA"
    components.iframe(cal_url, height=350, scrolling=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    with st.form("form_rotina"):
        st.markdown("### 📝 Nova Ordem de Serviço")
        st.write("Esta aba é para o dia a dia, soando como uma confirmação rápida e amigável.")
        st.markdown("---")
        
        q_cadastro = st.radio("Me tira uma dúvida rápida: a gente já fez a Ficha Técnica desse seu imóvel antes, ou é a nossa primeira vez lá? 📝", ["Já fizemos a Ficha", "Primeira vez"])
        q_ident = st.text_input("Ah, maravilha! Então me lembra só qual é a Torre e o número do apartamento para eu puxar o seu padrão de qualidade aqui? 🏢🚪 (Ex: Torre Formosa, Apto 509)")
        q_data = st.date_input("Que ótimo, mais uma limpeza agendada! Qual é a data que está reservada para nós? 🗓️✅", date.today())
        q_hospedes = st.text_input("Quantas pessoas entram nessa reserva? 👥 (Pergunto só para eu ter uma ideia do volume da casa e preparar tudo direitinho)")
        q_banho = st.text_input("Para essa estadia, quantas toalhas de banho e de rosto eu devo separar e deixar prontinhas? 🛁")
        q_cama = st.text_input("Quantas camas eu preciso preparar dessa vez? E deixo quantos travesseiros e cobertores extras disponíveis no armário? 🛏️")
        q_amenities = st.text_input("Quantos rolos de papel higiênico, sabonetes e shampoos eu devo deixar para esses hóspedes? 🧻🧴")
        q_mimos = st.text_input("Tem algum 'mimo' especial para essa reserva (bombom, cápsulas de café, bilhetinho)? Quantos eu deixo preparados? 🍬")
        q_notas = st.text_area("Tem algum detalhe especial ou pedido diferente para essa limpeza de hoje? (Ex: 'Sandra, o moço do ar-condicionado vai lá às 14h'). Pode me falar que eu cuido! 😉✨")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_gen = st.form_submit_button("🚀 Gerar Ordem com Segurança")
    
    if btn_gen:
        dt_str = q_data.strftime("%d/%m/%Y")
        payload = {
            "data_limpeza": dt_str,
            "categorias": [
                ("📋 INFORMAÇÕES GERAIS", [
                    ("Status do Cadastro", q_cadastro),
                    ("Identificação Rápida", q_ident),
                    ("Data da Limpeza", dt_str),
                    ("Qtd. Hóspedes", q_hospedes)
                ]),
                ("🧺 ENXOVAL E PREPARAÇÃO", [
                    ("Enxoval de Banho", q_banho),
                    ("Enxoval de Cama", q_cama)
                ]),
                ("🧴 AMENITIES E MIMOS", [
                    ("Consumíveis", q_amenities),
                    ("Mimos", q_mimos)
                ]),
                ("⚠️ NOTAS ESPECIAIS", [
                    ("Observações", q_notas)
                ])
            ]
        }
        
        img_os = criar_imagem_profissional(payload, "rotina")
        st.markdown("### Documento Gerado com Sucesso! 🎉")
        st.image(img_os, use_container_width=True)
        
        msg_whatsapp = f"Olá! Segue a Ordem de Serviço confirmada para o dia {dt_str} no apto {q_ident}."
        injetar_botao_compartilhar(img_os, msg_whatsapp, f"OS_{dt_str.replace('/','-')}.png")

# --- ABA 2: FICHA DO IMÓVEL ---
with tab_imovel:
    st.info("Olá! Para eu deixar tudo impecável e seguir exatamente o seu padrão de qualidade (e não te incomodar com perguntas bem na hora da limpeza), preparei este checklist rápido. Respondendo isso uma única vez, eu salvo no meu sistema e sigo sempre o seu jeito! Quando puder, me confirma? 🥰✨")
    
    with st.form("form_imovel"):
        st.markdown("### 📍 1. Identificação do Imóvel")
        i_prop = st.text_input("Para começar, qual o nome do proprietário ou responsável por esse imóvel? 👤")
        i_end = st.text_input("Qual é o endereço completo do imóvel? (Rua, número, bairro e CEP, se souber) 📍")
        i_cond = st.text_input("Qual é o nome do Edifício ou Condomínio? 🏢 (Ex: Rio Wonder)")
        i_apto = st.text_input("E para eu achar rapidinho: qual é a Torre ou Bloco, e o número do apartamento? 🏗️🚪")
        
        st.markdown("<br>### 🔑 2. Acesso e Segurança", unsafe_allow_html=True)
        i_acesso = st.text_area("Como vai ser a minha entrada no dia da limpeza? 🔑 (Chave na portaria, senha na porta, cofre...)")
        i_senhas = st.text_input("Quais são as senhas que vou precisar? (Da portaria, da porta principal...)")
        i_cofre = st.text_input("Se a gente for usar um cofre de chaves (lockbox), qual é a senha e onde ele costuma ficar escondidinho? 🤫")
        i_emerg = st.text_input("Sabe como é, né? Se a bateria da fechadura eletrônica acabar, tem alguma chave física de emergência? Onde ela fica? 😅")
        i_alarme = st.text_input("O imóvel tem alarme? Se sim, me passa o código para eu desativar assim que entrar? 🚨")
        
        st.markdown("<br>### 🧹 3. Equipamentos e Materiais", unsafe_allow_html=True)
        i_aspirador = st.text_input("Aí no apartamento tem um aspirador de pó funcionando direitinho? Ah, e a voltagem das tomadas é 110v ou 220v? 🔌")
        i_materiais = st.text_input("Posso contar com vassoura, rodo, balde, panos e escadinha aí no apto, ou é melhor eu levar os meus?")
        i_produtos = st.text_input("Sobre os produtos de limpeza: você costuma fornecer tudo (detergente, desinfetante) ou prefere que eu leve o meu kit?")
        i_proibido = st.text_input("Isso é muito importante: tem algum produto que é PROIBIDO usar no piso ou nas bancadas para não manchar de jeito nenhum? 🚫")
        
        st.markdown("<br>### 🛏️ 4. Quartos e Roupa de Cama", unsafe_allow_html=True)
        i_guardar = st.text_input("Onde você costuma guardar as roupas de cama e banho limpas? 🧺")
        i_suja = st.text_input("O que eu faço com a roupa suja que os hóspedes usaram? (Lavo na máquina do apto, deixo no cesto, coloco em sacola pra lavanderia?)")
        i_montar = st.text_input("Como você prefere que eu monte as camas? Aquele padrão de hotel (bem esticadinho com a peseira) ou mais simples (só as roupas dobradas em cima)?")
        
        st.markdown("<br>### 🚿 5. Banheiros e Amenities", unsafe_allow_html=True)
        i_shampoo = st.text_input("Para o sabonete e shampoo: você prefere que eu reabasteça aqueles frascos grandes ou que eu coloque miniaturas novas a cada check-in? 🧴")
        i_toalhas = st.text_input("Onde você prefere que eu arrume as toalhas limpas? (Em cima da cama, no rack do banheiro...)")
        
        st.markdown("<br>### 🍽️ 6. Cozinha e Geladeira", unsafe_allow_html=True)
        i_geladeira = st.text_input("Se tiver sobrado comida ou bebida dos hóspedes anteriores na geladeira, o que eu faço? Jogo tudo fora ou mantenho o que estiver fechado/lacrado? 🧊")
        i_louca = st.text_input("E se deixarem louça suja na pia: eu lavo (e já está incluso no meu serviço) ou você prefere anotar para cobrar uma taxa extra deles?")
        i_cozinha = st.text_input("Tem mais algum detalhe na cozinha que você gosta que eu fique de olho? (Ex: limpar o filtro da cafeteira, dar uma geral dentro do forno...)")
        
        st.markdown("<br>### ✨ 7. Finalização e Detalhes", unsafe_allow_html=True)
        i_mimos_guardados = st.text_input("Onde ficam guardados os mimos de boas-vindas? (Para eu saber de onde pegar no dia da limpeza) 🍬")
        i_ambiente = st.text_input("Ao terminar e fechar a porta, como devo deixar o ambiente? (Ex: ar-condicionado ligado no 24ºC pra não dar mofo, cortinas abertas ou fechadas?) 🌬️")
        i_lixo = st.text_input("Onde eu faço o descarte final de todo o lixo aí no prédio? 🗑️")
        
        st.markdown("<br>", unsafe_allow_html=True)
        btn_imovel = st.form_submit_button("💾 Gerar Ficha Protegida")
        
    if btn_imovel:
        payload_imovel = {
            "nome_prop": i_prop,
            "categorias": [
                ("📍 IDENTIFICAÇÃO DO IMÓVEL", [
                    ("Responsável", i_prop),
                    ("Endereço", i_end),
                    ("Condomínio", i_cond),
                    ("Torre/Apto", i_apto)
                ]),
                ("🔑 ACESSO E SEGURANÇA", [
                    ("Entrada", i_acesso),
                    ("Senhas", i_senhas),
                    ("Lockbox", i_cofre),
                    ("Chave de Emergência", i_emerg),
                    ("Alarme", i_alarme)
                ]),
                ("🧹 EQUIPAMENTOS E MATERIAIS", [
                    ("Aspirador/Voltagem", i_aspirador),
                    ("Materiais Básicos", i_materiais),
                    ("Produtos de Limpeza", i_produtos),
                    ("PRODUTOS PROIBIDOS", i_proibido)
                ]),
                ("🛏️ QUARTOS E ROUPA DE CAMA", [
                    ("Local do Enxoval Limpo", i_guardar),
                    ("Roupa Suja", i_suja),
                    ("Montagem das Camas", i_montar)
                ]),
                ("🚿 BANHEIROS E AMENITIES", [
                    ("Sabonete/Shampoo", i_shampoo),
                    ("Disposição das Toalhas", i_toalhas)
                ]),
                ("🍽️ COZINHA E GELADEIRA", [
                    ("Sobras na Geladeira", i_geladeira),
                    ("Louça Suja", i_louca),
                    ("Atenção Especial", i_cozinha)
                ]),
                ("✨ FINALIZAÇÃO E DETALHES", [
                    ("Local dos Mimos", i_mimos_guardados),
                    ("Clima/Ambiente Final", i_ambiente),
                    ("Descarte de Lixo", i_lixo)
                ])
            ]
        }

        img_fch = criar_imagem_profissional(payload_imovel, "imovel")
        st.markdown("### Documento Gerado com Sucesso! 🎉")
        st.image(img_fch, use_container_width=True)
        
        msg_fch = f"Ficha Técnica Atualizada: {i_prop}. Muito obrigada por preencher!"
        injetar_botao_compartilhar(img_fch, msg_fch, f"Ficha_{i_prop}.png")
