import os

# Configuração de caminhos (portabilidade)
# Ajustado para subir um nível, já que agora estamos em config/settings.py
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_DIR = os.path.join(BASE_DIR, "logs")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
CONVERSAS_DIR = os.path.join(BASE_DIR, "conversas")
BACKUP_DIR = os.path.join(BASE_DIR, "backup")

# Criar diretórios automaticamente
for directory in [LOG_DIR, OUTPUT_DIR, CONVERSAS_DIR, BACKUP_DIR]:
    os.makedirs(directory, exist_ok=True)

# Configuração da API Gemini
GEMINI_API_KEY = "AIzaSyDGGVLMDCvC-tzBtqxWD7gzfyj8cuOsqho"

# URL específica do Zoho Desk
URL_ZOHO_DESK = "https://desk.zoho.com/agent/hubedesk/era-verde-energia/whatsapp/page#IM/-1/sessions/mine-all"

# Timeout para login manual (OTP)
TIMEOUT_LOGIN_MANUAL_SEGUNDOS = 900  # 15 minutos

# Sistema Prompt Otimizado V3.4 (com diretiva de concisão)
SYSTEM_PROMPT = """
Você é Stefan, assistente virtual especializado da Era Verde Energia, empresa líder em energia solar no Brasil. 

PERFIL E MISSÃO:
- Assistente profissional com expertise em atualizações contratuais
- Especialista em expansão da usina solar da Era Verde Energia
- Foco em auxiliar clientes existentes na atualização de contratos
- Garantir continuidade dos benefícios com desconto ainda maior na conta de luz

COMUNICAÇÃO:
- Tom profissional, amigável e direto
- Linguagem clara e acessível
- Foco em transparência e benefícios para o cliente
- Sempre mencionar os ganhos (desconto maior, qualidade do serviço)

PROCESSO DE ATUALIZAÇÃO:
- Todos os processos são 100% digitais
- Sem custo adicional para o cliente
- Mantém todas as condições atuais
- Processo rápido e sem burocracia

ARGUMENTOS PRINCIPAIS:
1. Expansão da usina solar = Benefícios ainda maiores
2. Atualização mantêm condições atuais + melhorias
3. Processo completamente digital e sem custo
4. Garantia de continuidade do serviço

OBJETIVO PRINCIPAL:
Conseguir agendamento de conversa ou、diretamente atualizar o contrato quando possível.

---

IMPORTANTE: ANÁLISE DA ÚLTIMA MENSAGEM DO CLIENTE
Antes de responder, identifique especificamente:
- Se a última mensagem contém uma pergunta direta
- Se há objeções ou dúvidas específicas  
- Qual é o contexto emocional (interessado, resistente, confuso)
- Baseado na última mensagem, determine o próximo passo mais apropriado

RESPOSTA DIRETA:
Se a última mensagem do cliente contém uma pergunta específica, responda diretamente à pergunta com informações claras e objetivas, mantendo o tom profissional do Stefan.

---

DIRETIVA DE CONCISÃO (OTIMIZAÇÃO DE LATÊNCIA - V3.4):
Responda em até 6 linhas, direto ao ponto, sem introdução, sem saudação. 
Use frases curtas e claras. Foque no próximo passo.
"""

# Seletores CSS/XPath Otimizados (LEGADO - USADO APENAS PARA LOGIN)
ZHOO_DESK_SELECTORS = {
    # Login (usando seletores funcionais da V2.2)
    "login": {
        "email_field": ["#login_id", "input#login_id", "[name='login_id']"],
        "password_field": ["#password", "input#password", "[name='password']"],
        "login_button": ["#nextbtn", "button#nextbtn", "button[type='submit']"],
        "login_problem_link": ["#problemsignin", "div#problemsignin", "a[href*='problem']"],
        "authenticator_option": ["input[value='authenticator']", "//div[contains(text(), 'Insira a OTP com base em tempo')]"],
        "otp_field": ["#otp", "input[name='otp']", "input[class*='otp']"],
        "dashboard_check": ["button[data-id='globalSearchIcon']", "[data-id='globalSearchIcon']"]
    },
    # Novos seletores mapeados (V3.17)
    "navegacao_superior": {
        "link_whatsapp": "a[href*='whatsapp']",
        "link_email": "a[href*='e-mail']",
        "link_clientes": "a[href*='contato']",
        "link_atividades": "a[href*='activities']",
        "link_analises": "a[href*='dashboards']",
        "link_base_conhecimento": "a[href*='knowledge-base']",
        "dropdown_era_verde": "button[aria-haspopup='menu']",
        "botao_novo_ticket": "a[href*='e-mail/new']",
        "busca_global": "button#GlobalSearch",
        "notificacoes": "button#Notification"
    },
    "menu_lateral": {
        "painel": "menuitem", # XPath: //menuitem[contains(text(), 'Painel')]
        "todos_os_canais": "menuitem", # XPath: //menuitem[contains(text(), 'Todos os canais')]
        "minhas_conversas": "menuitem", # XPath: //menuitem[contains(text(), 'Minhas Conversas')]
        "nao_atribuidas": "menuitem", # XPath: //menuitem[contains(text(), 'Nao Atribuidas')]
        "bloqueado": "menuitem", # XPath: //menuitem[contains(text(), 'Bloqueado')]
        "encerrado": "menuitem", # XPath: //menuitem[contains(text(), 'Encerrado')]
        "todas_as_conversas": "menuitem", # XPath: //menuitem[contains(text(), 'Todas As Conversas')]
        "conversas_do_bot": "menuitem" # XPath: //menuitem[contains(text(), 'Conversas Do Bot')]
    },
    "filtro_conversas": {
        "dropdown_todos": "button:nth-of-type(1)",
        "filtro_departamento": "button[aria-label*='Filtrar']",
        "busca_conversas": "button[id*='search']"
    },
    "lista_conversas": {
        "lista_principal": "div[role='region'] button",
        "conversa_amanda": "button#70778000001253570",
        "conversa_conceicao": "button#70778000001392560",
        "conversa_david": "button#70778000001392421"
    },
    "chat_central": {
        "cabecalho_contato": "heading", # XPath: //heading[contains(text(), 'Amanda Queiroz')]
        "assignado_para": "button[aria-label*='Caroline']"
    },
    "editor_resposta": {
        "campo_resposta": "div[contenteditable='true']",
        "inserir_artigo": "button:contains-text('artigo')", # Pseudo-selector, requires specific handling or XPath
        "templates_mensagem": "button:contains-text('modelo')",
        "adicionar_emoji": "button:contains-text('Emoji')",
        "adicionar_imagem": "button:contains-text('imagem')",
        "adicionar_arquivo": "button:contains-text('arquivo')",
        "encerrar_chat": "button:contains-text('Encerrar')"
    },
    "painel_direito": {
        "contato_informacoes": "heading:contains-text('Contato')",
        "email_label": "label#E-mail",
        "proprietario_contato": "label[id*='Proprietario']",
        "celular_label": "label#Celular",
        "detalhes_conversa": "heading:contains-text('Detalhes')",
        "email_heading": "heading:contains-text('E-Mail')"
    }
}

# PRÉ-PREENCHIMENTO DE CHAT (PATCH V3.10 - ProseMirror)
COMPOSER_CSS = "[contenteditable='true'].ProseMirror.ui-rte-editor-div.ui-rte-editor"
