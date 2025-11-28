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
    
    # --- NAVEGAÇÃO E ESTRUTURA (V3.17) ---
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
        "notificacoes": "button#Notification",
        "quick_action": "button[aria-haspopup='menu']", # Ref C10
        "apps_menu": "button[aria-label*='menu']" # Ref C17
    },
    
    "menu_lateral": {
        "painel": "//menuitem[contains(text(), 'Painel')]",
        "todos_os_canais": "//menuitem[contains(text(), 'canais')]",
        "minhas_conversas": "//menuitem[contains(text(), 'Minhas')]",
        "nao_atribuidas": "//menuitem[contains(text(), 'Atribuída')]",
        "bloqueado": "//menuitem[contains(text(), 'Bloqueado')]",
        "encerrado": "//menuitem[contains(text(), 'Encerrado')]",
        "todas_as_conversas": "//menuitem[contains(text(), 'Todas')]",
        "conversas_do_bot": "//menuitem[contains(text(), 'Bot')]"
    },
    
    "filtro_conversas": {
        "dropdown_todos": "//button[contains(text(), 'Todos')]",
        "filtro_departamento": "//button[contains(text(), 'Filtrar')]",
        "busca_conversas": "button[aria-label*='search']",
        "limpar_filtro": "//button[contains(text(), 'Limpar')]"
    },
    
    "lista_conversas": {
        "lista_principal": "div[role='region'] button",
        # Exemplos de IDs dinâmicos para referência
        "exemplo_item": "button[id^='7077']" 
    },
    
    # --- CHAT ATIVO (V3.17) ---
    "chat_ativo": {
        "header": {
            "titulo_contato": "heading", # XPath: //heading[contains(text(), 'Nome')]
            "atribuido_para": "//button[contains(text(), 'Caroline')]" # Exemplo
        },
        "mensagens": {
            "generico": "button", # Mensagens são botões clicáveis geralmente
            "data": "generic", # Elementos de texto com data
            "sistema": "generic" # Mensagens de sistema "Hoje", "Você reabriu"
        },
        "acoes": {
            "resposta_tab": "//link[contains(text(), 'RESPOSTA')]",
            "escolher_modelo": "//button[contains(text(), 'Modelo')]",
            "encerrar_chat": "//button[contains(text(), 'Encerrar')]",
            "anexar": "button:contains-text('arquivo')", # Pseudo
            "emoji": "button:contains-text('Emoji')"
        },
        "editor": {
            "campo_resposta": "div[contenteditable='true']"
        }
    },
    
    # --- PAINEL DIREITO (V3.17) ---
    "painel_direito": {
        "contato_info_header": "//heading[contains(text(), 'Contato Informações')]",
        "email_label": "label#E-mail", # Ou busca por texto
        "email_value": "//text()[contains(., '@')]", # Genérico para busca
        "proprietario_label": "label[id*='Proprietario']",
        "celular_label": "label#Celular",
        "detalhes_conversa": "//heading[contains(text(), 'Detalhes')]"
    },
    
    # --- MODAL TEMPLATES (V3.17) ---
    "modal_templates": {
        "modal_container": "generic[aria-current='true']",
        "titulo": "//text()[contains(., 'MODELOS DE MENSAGEM')]",
        "campo_pesquisa": "textbox[placeholder*='Pesquisar']",
        "lista_modelos": "button", # Botões dentro da lista
        "botao_fechar": "//button[contains(text(), 'Fechar')]",
        "botao_enviar": "//button[contains(text(), 'Enviar Mensagem')]",
        "preview_corpo": "//text()[contains(., 'Olá Cliente')]" # Exemplo
    },
    
    # --- CHAT ENCERRADO (V3.17) ---
    "chat_encerrado": {
        "botao_reabrir": "//button[contains(text(), 'Reabrir')]",
        "status_texto": "//text()[contains(., 'Chat foi encerrado')]"
    }
}

# PRÉ-PREENCHIMENTO DE CHAT (PATCH V3.10 - ProseMirror)
COMPOSER_CSS = "[contenteditable='true'].ProseMirror.ui-rte-editor-div.ui-rte-editor"
