import os
import time
import logging
import json
import re
from datetime import datetime
from typing import Tuple, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config.settings import (
    LOG_DIR, OUTPUT_DIR, BACKUP_DIR, URL_ZOHO_DESK, 
    TIMEOUT_LOGIN_MANUAL_SEGUNDOS, ZHOO_DESK_SELECTORS, GEMINI_API_KEY
)
from core.gemini import GeminiAnalyzer
from core.selenium_utils import (
    _get_selected_tab_name, wait_msgslist_ready, wait_conversation_change, 
    extract_conversation_v2, preencher_resposta_no_zoho
)
from utils.text_processing import export_conversation_to_csv, export_conversation_to_txt

class ZohoDeskAutomator:
    """Automatizador principal para Zoho Desk"""
    
    def __init__(self):
        self.driver = None
        self.gemini_analyzer = None
        
        # Configurações de login
        self.email = "gestao.gdc@grupogera.com"
        self.password = "Ger@2357"
        
        # Configurar logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configura sistema de logging dual"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"execucao_{timestamp}.txt"
        log_path = os.path.join(LOG_DIR, log_filename)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='[%(asctime)s] %(levelname)s: %(message)s',
            handlers=[
                logging.FileHandler(log_path, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        
        logging.info("=== SISTEMA DE LOGGING INICIADO (V3.15 - SAFETY SETTINGS) ===")
        logging.info(f"Arquivo de log: {log_path}")
    
    def start_browser(self) -> bool:
        """Inicia navegador Edge com configurações otimizadas e perfil persistente"""
        try:
            logging.info("Iniciando navegador Edge...")
            
            options = EdgeOptions()
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
            
            # Configuração de Perfil Persistente (Corrige erro de login/passkey)
            from config.settings import BROWSER_PROFILE_DIR, BROWSER_PROFILE_NAME
            logging.info(f"Carregando perfil do navegador: {BROWSER_PROFILE_NAME}")
            options.add_argument(f"user-data-dir={BROWSER_PROFILE_DIR}")
            options.add_argument(f"profile-directory={BROWSER_PROFILE_NAME}") # Usa o perfil real do usuário
            
            options.add_experimental_option("useAutomationExtension", False)
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            
            self.driver = webdriver.Edge(options=options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            start_time = time.time()
            self.driver.get("https://desk.zoho.com/")
            time.sleep(3)
            
            load_time = time.time() - start_time
            logging.info(f"[OK] Navegador iniciado com sucesso! (tempo: {load_time:.1f}s)")
            
            return True
            
        except Exception as e:
            logging.error(f"[ERRO] Erro ao iniciar navegador: {e}")
            logging.error("DICA: Feche todas as janelas do Edge antes de rodar o bot.")
            return False
    
    def _inserir_texto_seguro(self, elemento, texto, nome_campo):
        """Insere texto de forma segura com verificação"""
        try:
            # Clicar no campo para garantir foco
            elemento.click()
            time.sleep(0.3)
            
            # Limpar campo existente
            elemento.clear()
            time.sleep(0.2)
            
            # Inserir texto caractere por caractere (mais confiável)
            for char in texto:
                elemento.send_keys(char)
                time.sleep(0.05)  # Delay pequeno entre caracteres
            
            # Verificar se o texto foi inserido
            time.sleep(0.3)
            valor_atual = elemento.get_attribute("value")
            
            if valor_atual == texto:
                logging.info(f"[OK] {nome_campo} '{texto}' inserido com sucesso.")
                return True
            else:
                logging.warning(f"[WARN] {nome_campo} não foi inserido corretamente. Tentando novamente...")
                # Segunda tentativa - mais rápida
                elemento.clear()
                time.sleep(0.2)
                elemento.send_keys(texto)
                time.sleep(0.3)
                
                valor_atual = elemento.get_attribute("value")
                if valor_atual == texto:
                    logging.info(f"[OK] {nome_campo} '{texto}' inserido com sucesso (2ª tentativa).")
                    return True
                else:
                    logging.error(f"[ERRO] Falha ao inserir {nome_campo}. Valor esperado: '{texto}', Valor atual: '{valor_atual}'")
                    return False
                    
        except Exception as e:
            logging.error(f"[ERRO] Erro ao inserir {nome_campo}: {e}")
            return False
    
    def login(self) -> bool:
        """Realiza login no Zoho Desk com inserção segura de texto"""
        try:
            logging.info("Iniciando processo de login no Zoho Desk...")
            
            self.driver.get(URL_ZOHO_DESK)
            wait = WebDriverWait(self.driver, 20)
            
            # Verificar se já está logado
            if self._is_logged_in():
                logging.info("[OK] Login já estava ativo (sessão em cache). Pulando para a aplicação.")
                return True
            
            logging.info("⏳ Não está logado. Iniciando processo de login...")
            
            # Processo de login com inserção segura
            try:
                # Esperar e localizar campo de email - AGORA ESPERANDO SER CLICÁVEL
                logging.info("[BUSCAR] Aguardando campo de email estar pronto...")
                email_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["email_field"][0])))
                
                # Inserir email com verificação
                if not self._inserir_texto_seguro(email_input, self.email, "Email"):
                    logging.error("[ERRO] Falha ao inserir email. Abortando login.")
                    return False
                
                # Clicar no botão Next
                time.sleep(0.5)
                next_button = self.driver.find_element(By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["login_button"][0])
                next_button.click()
                logging.info("[OK] Botão 'Next' clicado após email.")
                
                # Esperar e inserir senha
                try:
                    logging.info("[BUSCAR] Aguardando campo de senha estar pronto...")
                    password_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["password_field"][0])))
                    
                    # Inserir senha com verificação
                    if not self._inserir_texto_seguro(password_input, self.password, "Senha"):
                        logging.error("[ERRO] Falha ao inserir senha. Abortando login.")
                        return False
                    
                    # Clicar no botão Next
                    time.sleep(0.5)
                    next_button = self.driver.find_element(By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["login_button"][0])
                    next_button.click()
                    logging.info("[OK] Botão 'Next' clicado após senha.")
                    
                except TimeoutException:
                    logging.warning("[WARN] Campo de senha não apareceu, possivelmente já na tela de OTP.")
                
                # Tenta selecionar o método OTP (se a tela aparecer)
                try:
                    logging.info("[BUSCAR] Procurando opção 'Problema ao fazer login?'...")
                    problem_link = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["login_problem_link"][0]))
                    )
                    problem_link.click()
                    logging.info("[OK] Clicado em 'Problema ao fazer login?'.")
                    
                    time.sleep(1)
                    auth_option = self.driver.find_element(By.XPATH, ZHOO_DESK_SELECTORS["login"]["authenticator_option"][1])
                    auth_option.click()
                    logging.info("[OK] Selecionado método de verificação por App Autenticador.")
                except TimeoutException:
                    logging.warning("[WARN] A tela de OTP já está visível ou não foi necessária a etapa 'Problema ao fazer login?'.")
                
                # Aguardar login
                logging.info("⏳ Aguardando conclusão do login (OTP manual)...")
                if self._wait_for_login():
                    logging.info("[OK] LOGIN CONCLUÍDO COM SUCESSO!")
                    return True
                
                logging.error("[ERRO] Timeout aguardando conclusão do login.")
                return False
                
            except TimeoutException:
                logging.error("[ERRO] Erro no processo de login: campo não encontrado (timeout)")
                return False
            
        except Exception as e:
            logging.error(f"[ERRO] Erro no login: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Verifica se já está logado (usando método da V2.2)"""
        try:
            self.driver.get(URL_ZOHO_DESK)
            time.sleep(3)
            
            # Verificar se já está logado usando o seletor que funcionava na V2.2
            short_wait = WebDriverWait(self.driver, 3)
            short_wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["dashboard_check"][0])))
            logging.info("[OK] Login já estava ativo (sessão em cache). Pulando para a aplicação.")
            return True
            
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def _wait_for_otp(self, timeout=300) -> bool:
        """Aguarda código OTP"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Verificar se apareceu campo de OTP
                otp_field = self.driver.find_element(By.CSS_SELECTOR, "#otp, input[name='otp']")
                if otp_field.is_displayed():
                    logging.info("[OK] Campo OTP detectado. Aguardando entrada do usuário...")
                    time.sleep(5)
                    
                    # Aguardar preenchimento do OTP
                    while time.time() - start_time < timeout:
                        otp_value = otp_field.get_attribute("value")
                        if otp_value and len(otp_value) >= 6:
                            logging.info("[OK] OTP inserido. Prosseguindo...")
                            return True
                        time.sleep(2)
                    
                    return False
                    
            except NoSuchElementException:
                time.sleep(2)
                continue
            
            return False
        
        return False
    
    def _check_login_completed(self) -> bool:
        """Verifica se login foi concluído SEM recarregar a página"""
        try:
            # Verificar se elemento do dashboard está presente
            short_wait = WebDriverWait(self.driver, 2)
            short_wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["login"]["dashboard_check"][0])
            ))
            return True
        except TimeoutException:
            return False
        except Exception:
            return False
    
    def _wait_for_login(self, timeout=None) -> bool:
        """Aguarda conclusão do login pelo usuário (inserção manual de OTP)"""
        if timeout is None:
            timeout = TIMEOUT_LOGIN_MANUAL_SEGUNDOS
        
        start_time = time.time()
        elapsed_minutes = 0
        
        logging.info(f"⏳ Aguardando usuário completar OTP (timeout: {timeout//60} minutos)...")
        
        while time.time() - start_time < timeout:
            try:
                # Verificar se login foi concluído
                if self._check_login_completed():
                    logging.info("[OK] Login detectado como concluído!")
                    return True
                
                # Log de progresso a cada minuto
                current_elapsed = int((time.time() - start_time) // 60)
                if current_elapsed > elapsed_minutes:
                    elapsed_minutes = current_elapsed
                    remaining = (timeout // 60) - elapsed_minutes
                    logging.info(f"⏳ Aguardando OTP... ({elapsed_minutes}/{timeout//60} min - resta {remaining} min)")
                
                time.sleep(3)  # Verificar a cada 3 segundos
                
            except Exception as e:
                logging.warning(f"[WARN] Erro ao aguardar login: {e}")
                time.sleep(3)
        
        logging.error(f"[ERRO] Timeout após {timeout//60} minutos aguardando conclusão do login.")
        return False
    
    def _select_conversation_prompt(self):
        """
        (Refatorado V3.3)
        Apenas exibe as instruções e captura o input do usuário.
        A verificação agora é feita por wait_conversation_change.
        """
        logging.info("Aguardando usuário selecionar conversa no Zoho Desk...")
        
        input("\n📋 INSTRUÇÕES:\n"
              "1. No Zoho Desk, selecione uma conversa na lista\n"
              "2. Clique na conversa que deseja processar\n"
              "3. Aguarde a conversa carregar completamente\n"
              "4. Pressione ENTER quando estiver pronto...\n")
        
        logging.info("Usuário pressionou ENTER. Verificando mudança de conversa...")
    
    def process_conversation(self) -> Tuple[bool, str, Dict]:
        """
        Processa conversa ativa e gera resposta (ADAPTADO V3.18 - Gemini Web)
        
        Returns:
            Tupla (sucesso, resposta, dados_conversa)
        """
        try:
            # ==================================
            # INÍCIO DA EXTRAÇÃO V3.3
            # ==================================
            
            # Criar o objeto 'wait'
            wait = WebDriverWait(self.driver, 20)
            
            # Chamar a nova função de extração V3.2 (refinada V3.3)
            conversation_data = extract_conversation_v2(self.driver, wait, logging)
            
            # Adaptar as chaves
            client_name = conversation_data.get("cliente_nome", "Cliente Não Identificado")
            
            if client_name == "Cliente Não Identificado" or not client_name:
                logging.warning("[WARN]️ Nome do cliente não identificado")
                client_name = "Cliente Não Identificado"
                conversation_data["cliente_nome"] = client_name
            
            # ==================================
            # FIM DA EXTRAÇÃO V3.3
            # ==================================
            
            # Confirmar com usuário
            if not self._confirm_processing(client_name):
                return False, "", conversation_data
            
            # Salvar conversa extraída (JSON)
            self._save_conversation_backup(conversation_data)
            
            # Exportar CSV (e opcionalmente TXT)
            try:
                csv_arquivo = export_conversation_to_csv(conversation_data, base_dir=BACKUP_DIR, logger=logging)
                txt_arquivo = export_conversation_to_txt(conversation_data, base_dir=BACKUP_DIR, logger=logging)
                logging.info(f"[OK] Exportações concluídas: CSV={csv_arquivo}, TXT={txt_arquivo}")
            except Exception as e:
                logging.warning(f"[WARN]️ Falha ao exportar CSV/TXT: {e}")
            
            # ==================================
            # GERAÇÃO DE RESPOSTA (V3.18 - Gemini Web Dual-Tab)
            # ==================================
            logging.info("🤖 Enviando contexto para o Gemini Web...")
            
            # Construir prompt
            # Instancia temporária apenas para formatar
            analyzer = GeminiAnalyzer(GEMINI_API_KEY) 
            historico_fmt = analyzer._format_conversation_history(conversation_data.get("mensagens", []))
            
            client_details = conversation_data.get("cliente_detalhes", {})
            detalhes_str = ""
            if client_details:
                detalhes_str = f"DADOS CLIENTE: Email: {client_details.get('email')} | Tel: {client_details.get('phone')}"

            prompt_text = f"""
Analisar conversa:
{historico_fmt}
{detalhes_str}
Última msg: {conversation_data.get('ultima_msg_cliente')}

Responda como Stefan.
"""
            # Enviar para Gemini Web
            if not self.gemini_web.send_message(prompt_text):
                logging.error("Falha ao enviar mensagem para Gemini Web.")
                return False, "", conversation_data
            
            # Pegar resposta
            response = self.gemini_web.get_last_response()
            if not response:
                logging.error("Falha ao obter resposta do Gemini Web.")
                return False, "", conversation_data

            # Limpar citações do Gemini (ex: [cite_start], [cite: 9])
            import re
            response = re.sub(r"\[cite.*?\]", "", response).strip()
                
            logging.info(f"🤖 Resposta gerada (Web): {response[:50]}...")
            
            # Voltar para Zoho
            self.gemini_web.switch_back_to_zoho()
            
            # Salvar resposta
            response_path = self._save_response(response, client_name)
            logging.info(f"[OK] Resposta salva em: {response_path}")

            # ==================================
            # PREENCHIMENTO E AÇÕES
            # ==================================
            try:
                # Verificar se há ação de fechar
                if "[ACTION: CLOSE]" in response:
                    logging.info("🛑 Ação de encerramento detectada pelo Gemini.")
                    response = response.replace("[ACTION: CLOSE]", "").strip()
                    should_close = True
                else:
                    should_close = False

                logging.info("[ESCREVER] Preenchendo a resposta no chat...")
                preencher_resposta_no_zoho(self.driver, response, timeout=15)
                logging.info("[OK] Mensagem escrita no composer do Zoho (não enviada).")
                
                if should_close:
                    logging.info("⚠️ Sugestão de encerramento: O bot identificou que este chat pode ser fechado.")
                    
            except Exception as e:
                logging.error(f"[WARN]️ Não consegui escrever no composer automaticamente: {e}")

            return True, response, conversation_data
                
        except Exception as e:
            logging.error(f"[ERRO] Erro ao processar conversa: {e}")
            return False, "", {}
    
    def _confirm_processing(self, client_name: str) -> bool:
        """Confirma processamento com usuário"""
        while True:
            confirm = input(f"\n❓ ATUAR na conversa de {client_name}? (s/n): ").lower()
            if confirm in ['s', 'sim', 'y', 'yes']:
                logging.info(f"[OK] Usuário confirmou: ATUAR na conversa de {client_name}")
                return True
            elif confirm in ['n', 'nao', 'não', 'no']:
                logging.info("[ERRO] Usuário cancelou o processamento")
                return False
            else:
                print("Por favor, digite 's' para sim ou 'n' para não.")
    
    def _save_conversation_backup(self, conversation_data: Dict):
        """Salva backup da conversa extraída (JSON)"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Sanitizar nome do cliente para o arquivo (V3.1)
            cliente = conversation_data.get("cliente_nome") or "sem_nome"
            cliente_sanit = re.sub(r"[^A-Za-z0-9_\- ]+", "_", cliente)[:60]
            
            backup_filename = f"conversa_{cliente_sanit}_{timestamp}.json"
            backup_path = os.path.join(BACKUP_DIR, backup_filename)
            
            # Criar uma cópia para não modificar o original (especialmente para remover HTML)
            data_to_save = json.loads(json.dumps(conversation_data))
            
            # Opcional: remover HTML grande do backup para economizar espaço
            if 'mensagens' in data_to_save:
                for msg in data_to_save['mensagens']:
                    if 'outerHTML' in msg:
                        del msg['outerHTML']

            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=2)
            
            logging.info(f"[SALVAR] Backup da conversa (JSON) salvo: {backup_path}")
            
        except Exception as e:
            logging.warning(f"Erro ao salvar backup JSON: {e}")
    
    def _save_response(self, response: str, client_name: str) -> str:
        """Salva resposta gerada"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitizar nome do cliente para o arquivo (V3.1)
        cliente_sanit = re.sub(r"[^A-Za-z0-9_\- ]+", "_", client_name)[:60]
        
        filename = f"resposta_stefan_{cliente_sanit}_{timestamp}.txt"
        file_path = os.path.join(OUTPUT_DIR, filename)
        
        content = f"""ASSISTENTE STEFAN - RESPOSTA GERADA
Data/Hora: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}
Cliente: {client_name}
Versão: 3.16 (MAX_TOKENS Fix)

===============================================

{response}

===============================================
Gerado por: Assistente Stefan V3.16
Interface: Extrator V3.3 (Staleness V3.8, Virtualizado)
Modelo: Gemini 2.5-flash (temperature=0.6, max_tokens=1024)
"""
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return file_path
    
    def generate_execution_summary(self, conversation_data: Dict, processing_time: float):
        """Gera resumo detalhado da execução (ADAPTADO V3.8)"""
        try:
            client_name = conversation_data.get("cliente_nome", "Desconhecido")
            message_count = len(conversation_data.get("mensagens", []))
            total_chars = sum(len(msg.get("text", "")) for msg in conversation_data.get("mensagens", []))
            
            # (V3.17) - Substituído box de caracteres UTF-8 por ASCII simples para evitar SyntaxError no Windows
            # (V3.18) - CORRIGIDO o caractere de espaço inválido (linha 1291)
            # (V3.18) - CORRIGIDO o strftime (linha 1292)
            summary = f"""
+----------------------------------------------------------------------+
|                    RESUMO DA EXECUÇÃO V3.16                          |
+----------------------------------------------------------------------+
| Status: OK CONCLUIDO COM SUCESSO                                 |
| Cliente: {client_name:<50} |
| Mensagens processadas: {message_count:<44} |
| Tamanho total: {total_chars} caracteres                               |
| Tempo de processamento: {processing_time:.1f} segundos              |
| Data/Hora: {datetime.now().strftime("%d/%m/%Y às %H:%M:%S"):<50} |
+----------------------------------------------------------------------+
| NOVAS FUNCIONALIDADES V3.16 (PATCH):                        |
| • Corrigido erro de MAX_TOKENS (limite aumentado p/ 1024)    |
| • Corrigida captura de nome de cliente (multi-fallback)     |
+----------------EM RECURSOS V3.15 (MANTIDOS)-------------------------+
| • Adicionado Safety Settings (BLOCK_NONE) para API Gemini   |
| • Evita bloqueios por "finish_reason: 2" (SAFETY)           |
| • Pré-preenchimento (V3.10) focado em ProseMirror (HTML <p>) |
+----------------------------------------------------------------------+
"""
            
            print(summary)
            logging.info("[OK] Resumo da execução exibido com sucesso")
            
        except Exception as e:
            logging.warning(f"Erro ao gerar resumo: {e}")
    
    def close(self):
        """Fecha navegador e limpa recursos"""
        if self.driver:
            try:
                logging.info("Fechando navegador...")
                self.driver.quit()
                logging.info("[OK] Navegador fechado com sucesso")
            except Exception as e:
                logging.warning(f"Erro ao fechar navegador: {e}")
    
    def run(self):
        """Executa fluxo completo de automação (Refatorado V3.8)"""
        
        print("\n🤖 MODO DE OPERAÇÃO:")
        print("1. Manual (Você seleciona as conversas)")
        print("2. Autopilot (O bot navega e processa sozinho)")
        mode = input("Escolha (1/2): ").strip()
        
        if mode == "2":
            self.run_autopilot()
            return

        msgs_root = None # V3.8: Armazena o container da conversa atual
        
        try:
            # Configurar Gemini (Web ou API)
            # V3.18: Usando Gemini Web (Dual-Tab)
            logging.info("Configurando Gemini Web Client...")
            # Importação local para evitar ciclo se houver
            from core.gemini_web import GeminiWebClient
            # A inicialização do driver acontece em start_browser, então instanciamos o client lá ou aqui após start
            
            # Iniciar navegador
            if not self.start_browser():
                return False
            
            # Inicializar Client Web com o driver já aberto
            self.gemini_web = GeminiWebClient(self.driver)
            if not self.gemini_web.open_gemini():
                logging.error("Falha ao abrir Gemini Web. Abortando.")
                return False
            
            # Voltar para Zoho para login
            self.gemini_web.switch_back_to_zoho()
            
            # Login
            if not self.login():
                return False
            
            # --- FLUXO V3.8: PRIMEIRA EXECUÇÃO ---
            logging.info("Login concluído. Exibindo instruções para a PRIMEIRA conversa...")
            self._select_conversation_prompt()
            
            try:
                # V3.8: Na primeira vez, apenas esperamos o 'new'
                msgs_root = wait_msgslist_ready(self.driver, timeout=40)
                logging.info(f"[OK] Primeira conversa carregada (Root: {msgs_root.id}).")
            except Exception as e:
                logging.error(f"[ERRO] Erro ao carregar a primeira conversa: {e}")
                return False

            # Processar a primeira conversa
            start_time = time.time()
            success, response, conversation_data = self.process_conversation()
            processing_time = time.time() - start_time
            
            if success:
                self.generate_execution_summary(conversation_data, processing_time)
                
                # V3.x: Resposta já foi impressa/preenchida
                
                # --- FLUXO V3.8: LOOP DE CONTINUAÇÃO ---
                while True:
                    continue_choice = input("\nProcessar outra conversa? (s/n): ").lower()
                    if continue_choice in ['s', 'sim', 'y', 'yes']:
                        
                        # === INÍCIO DO PATCH V3.8 (Stale Wait) ===
                        if not msgs_root:
                            logging.error("Estado 'msgs_root' perdido. Tentando re-sincronizar.")
                            # Tenta se recuperar pegando o root atual
                            try:
                                msgs_root = wait_msgslist_ready(self.driver, timeout=20)
                            except Exception as e_recupera:
                                logging.error(f"Falha ao re-sincronizar: {e_recupera}")
                                break # Sai do loop
                        
                        logging.info(f"Capturando estado atual (Root: {msgs_root.id}) antes da troca...")
                        
                        # 2. Pedir para o usuário trocar
                        self._select_conversation_prompt() 
                        
                        # 3. Esperar a troca (lógica do patch V3.8)
                        try:
                            # Passa o root antigo (msgs_root) e espera o novo
                            msgs_root = wait_conversation_change(self.driver, msgs_root, timeout=40) 
                            
                            new_client = _get_selected_tab_name(self.driver)
                            logging.info(f"[OK] Nova conversa detectada e carregada: {new_client} (Novo Root: {msgs_root.id})")
                        except Exception as e:
                            logging.error(f"[ERRO] Erro ao detectar mudança de conversa: {e}")
                            logging.error("Pode ser necessário reiniciar o script se o estado estiver instável.")
                            try:
                                # Tenta se recuperar pegando o root atual se o staleness falhou
                                msgs_root = wait_msgslist_ready(self.driver, timeout=20)
                            except:
                                continue # Pula para o próximo 'Processar outra?'
                        # === FIM DO PATCH V3.8 ===

                        # 4. Processar a nova conversa
                        start_time = time.time()
                        success, response, conversation_data = self.process_conversation()
                        processing_time = time.time() - start_time
                        
                        if success:
                            self.generate_execution_summary(conversation_data, processing_time)
                            # V3.x: Resposta já foi impressa/preenchida
                                
                    elif continue_choice in ['n', 'nao', 'não', 'no']:
                        logging.info("Usuário optou por encerrar o assistente")
                        break
                    else:
                        print("Por favor, digite 's' para sim ou 'n' para não.")
            
            return True
            
        except KeyboardInterrupt:
            logging.info("Execução interrompida pelo usuário")
            return False
        except Exception as e:
            logging.error(f"[ERRO] Erro durante execução: {e}")
            return False
        finally:
            self.close()

    def run_autopilot(self):
        """
        (V3.17) Modo Autônomo: Navega e processa conversas automaticamente.
        """
        try:
            logging.info("🚀 INICIANDO MODO AUTOPILOT (Gemini Web)")
            
            # Importação local
            from core.gemini_web import GeminiWebClient
            
            if not self.start_browser(): return
            
            # Inicializar Client Web
            self.gemini_web = GeminiWebClient(self.driver)
            if not self.gemini_web.open_gemini():
                logging.error("Falha ao abrir Gemini Web. Abortando.")
                return

            # Voltar para Zoho
            self.gemini_web.switch_back_to_zoho()
            
            if not self.login(): return
            
            # 1. Ir para "Minhas Conversas"
            from core.selenium_utils import navigate_to_section, get_conversation_items
            if not navigate_to_section(self.driver, "minhas_conversas"):
                logging.error("Falha ao acessar Minhas Conversas")
                return

            # Memória de sessão para evitar loop na mesma conversa
            processed_ids = set()

            # 2. Loop de processamento
            while True:
                logging.info("🔄 Buscando conversas pendentes...")
                items = get_conversation_items(self.driver)
                
                # Filtrar itens já processados
                pending_items = []
                for item in items:
                    try:
                        c_id = item.get_attribute("id")
                        if c_id not in processed_ids:
                            pending_items.append((c_id, item))
                    except:
                        continue

                logging.info(f"Encontradas {len(items)} conversas ({len(pending_items)} novas).")
                
                if not pending_items:
                    logging.info("Nenhuma conversa nova encontrada. Aguardando 30s...")
                    time.sleep(30)
                    # Refresh para pegar novas
                    self.driver.refresh()
                    # Re-navegar para garantir foco correto (às vezes refresh joga para home)
                    navigate_to_section(self.driver, "minhas_conversas")
                    continue
                
                # Processar a primeira da lista de pendentes
                try:
                    c_id, current_item = pending_items[0]
                    logging.info(f"Abrindo conversa ID: {c_id}")
                    current_item.click()
                    
                    # Espera carregar
                    wait_msgslist_ready(self.driver)
                    
                    # Processa
                    success, _, _ = self.process_conversation()
                    
                    # Marca como processado independentemente do sucesso (para não travar)
                    # Se falhou, provavelmente precisa de intervenção humana ou tentar mais tarde
                    processed_ids.add(c_id)
                    
                    if success:
                        logging.info("Conversa processada com sucesso.")
                        time.sleep(5)
                    
                    # Volta para a lista
                    navigate_to_section(self.driver, "minhas_conversas")
                    
                except Exception as e:
                    logging.error(f"Erro no loop do autopilot: {e}")
                    time.sleep(5)
                    # Tenta recuperar navegação
                    navigate_to_section(self.driver, "minhas_conversas")
                    
        except KeyboardInterrupt:
            logging.info("Autopilot interrompido.")
        finally:
            self.close()
