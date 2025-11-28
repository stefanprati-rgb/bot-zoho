import time
import logging
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pyperclip

from config.settings import GEMINI_WEB_URL, GEMINI_WEB_SELECTORS

class GeminiWebClient:
    """
    Cliente para automação via interface Web do Google Gemini (Dual-Tab).
    """
    def __init__(self, driver):
        self.driver = driver
        self.gemini_tab = None
        self.zoho_tab = None

    def open_gemini(self):
        """Abre o Gemini em uma nova aba se ainda não estiver aberto."""
        try:
            self.zoho_tab = self.driver.current_window_handle
            
            # Verifica se já existe uma aba do Gemini aberta
            for handle in self.driver.window_handles:
                self.driver.switch_to.window(handle)
                if "gemini.google.com" in self.driver.current_url:
                    self.gemini_tab = handle
                    logging.info("Aba do Gemini já encontrada. Reutilizando.")
                    return True
            
            # Se não encontrou, abre nova
            logging.info("Abrindo nova aba para o Gemini...")
            self.driver.switch_to.window(self.zoho_tab)
            self.driver.execute_script(f"window.open('{GEMINI_WEB_URL}', '_blank');")
            
            # Muda foco para nova aba
            time.sleep(2)
            new_handles = self.driver.window_handles
            self.gemini_tab = new_handles[-1]
            self.driver.switch_to.window(self.gemini_tab)
            
            # Espera carregar
            logging.info("Aguardando carregamento do Gemini...")
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, GEMINI_WEB_SELECTORS["input_prompt"]))
            )
            logging.info("Gemini carregado com sucesso.")
            return True
            
        except Exception as e:
            logging.error(f"Erro ao abrir Gemini Web: {e}")
            # Tenta voltar para o Zoho em caso de erro
            if self.zoho_tab:
                self.driver.switch_to.window(self.zoho_tab)
            return False

    def send_message(self, text):
        """Envia mensagem para o Gemini."""
        if not self.gemini_tab:
            logging.error("Gemini tab não inicializada.")
            return False
            
        try:
            self.driver.switch_to.window(self.gemini_tab)
            
            # Encontrar input
            input_el = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, GEMINI_WEB_SELECTORS["input_prompt"]))
            )
            
            # Limpar (se necessário) e digitar
            # O contenteditable às vezes é chato com clear(), melhor selecionar tudo e colar ou digitar
            input_el.click()
            # input_el.clear() # Pode falhar em divs
            
            # Digitação segura (colar texto grande é mais rápido)
            import pyperclip
            pyperclip.copy(text)
            input_el.send_keys(Keys.CONTROL, 'v')
            time.sleep(0.5)
            
            # Clicar em enviar
            send_btn = self.driver.find_element(By.CSS_SELECTOR, GEMINI_WEB_SELECTORS["botao_enviar"])
            send_btn.click()
            
            return True
        except Exception as e:
            logging.error(f"Erro ao enviar mensagem no Gemini: {e}")
            return False

    def get_last_response(self, timeout=60):
        """Aguarda e captura a última resposta gerada (Via Clipboard)."""
        try:
            self.driver.switch_to.window(self.gemini_tab)
            
            logging.info("Aguardando resposta do Gemini...")
            time.sleep(3) # Espera inicial
            
            # 1. Esperar botão de enviar voltar (indica fim da geração)
            WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, GEMINI_WEB_SELECTORS["botao_enviar"]))
            )
            
            # 2. Tentar clicar no botão de copiar da última resposta
            # O seletor do botão de copiar geralmente fica no footer da resposta
            # Vamos tentar encontrar o último botão de copiar visível
            try:
                # Seletor genérico para botões de copiar (ícone de copy)
                # Geralmente tem aria-label="Copy" ou "Copiar"
                copy_buttons = self.driver.find_elements(By.CSS_SELECTOR, GEMINI_WEB_SELECTORS["botao_copiar"])
                
                if copy_buttons:
                    last_copy_btn = copy_buttons[-1]
                    # Scroll para o botão
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", last_copy_btn)
                    time.sleep(0.5)
                    last_copy_btn.click()
                    logging.info("Botão de copiar clicado.")
                    
                    # Pegar do clipboard
                    time.sleep(0.5)
                    import pyperclip
                    response_text = pyperclip.paste()
                    
                    if response_text:
                        return response_text
                        
            except Exception as e:
                logging.warning(f"Falha ao usar botão de copiar: {e}")
            
            # 3. Fallback: Extração via JS (Melhorada)
            logging.info("Usando fallback de extração de texto via JS...")
            last_text = self.driver.execute_script("""
                // Pega todos os containers de mensagem do modelo
                // O seletor exato depende da estrutura, mas geralmente são 'model-response' ou similar
                // Vamos tentar pegar o último elemento que tenha texto significativo dentro do histórico
                
                var history = document.querySelector(arguments[0]);
                if (!history) return null;
                
                // Tenta pegar os containers de resposta direta (ex: message-content)
                // Se não souber a classe, pega os filhos diretos e filtra
                var children = Array.from(history.children);
                if (children.length === 0) return null;
                
                // Pega o último filho (assumindo que é a resposta)
                var lastChild = children[children.length - 1];
                
                // Se o último for o input ou footer, pega o penúltimo
                if (lastChild.tagName === 'DIV' && lastChild.querySelector('textarea')) {
                     lastChild = children[children.length - 2];
                }
                
                return lastChild.innerText;
            """, GEMINI_WEB_SELECTORS["chat_history"])
            
            return last_text or "Erro: Resposta vazia."

        except Exception as e:
            logging.error(f"Erro ao capturar resposta do Gemini: {e}")
            return None
            
    def switch_back_to_zoho(self):
        """Volta o foco para a aba do Zoho."""
        if self.zoho_tab:
            self.driver.switch_to.window(self.zoho_tab)
