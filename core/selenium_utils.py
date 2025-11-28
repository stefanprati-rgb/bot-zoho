import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from config.settings import COMPOSER_CSS, ZHOO_DESK_SELECTORS

def _get_selected_tab_name(driver):
    """
    Lê o nome do cliente de múltiplas fontes possíveis (V3.16 - correção)
    """
    # Estratégia 1: Nome no topo da janela do chat (mais confiável para conversa ativa)
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            ".zim4e2bf0ddf6.zim4af66c9aeb[data-title]"
        )
        nome = el.get_attribute("data-title") or el.text.strip()
        if nome:
            return nome
    except Exception:
        pass
    
    # Estratégia 2: Nome na aba direita de informações
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            ".zim0af53622fd.zim4af66c9aeb[data-title]"
        )
        nome = el.get_attribute("data-title") or el.text.strip()
        if nome:
            return nome
    except Exception:
        pass
    
    # Estratégia 3: Item ativo do menu lateral (fallback)
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            "[data-test-id^='tabListItem_'][data-a11y-focus='true'] [data-test-id='actorName']"
        )
        nome = el.text.strip()
        if nome:
            return nome
    except Exception:
        pass
    
    # Estratégia 4: Qualquer elemento actorName visível (último recurso)
    try:
        el = driver.find_element(
            By.CSS_SELECTOR,
            "[data-test-id='actorName'][data-title]"
        )
        nome = el.get_attribute("data-title") or el.text.strip()
        if nome:
            return nome
    except Exception:
        pass
    
    return None

def extract_client_details(driver):
    """
    (V3.17) Extrai detalhes do cliente do painel lateral direito.
    Retorna dict com nome, email, telefone, etc.
    """
    details = {
        "email": "",
        "phone": "",
        "owner": ""
    }
    
    try:
        # Email
        try:
            # Tenta pegar pelo label e depois o valor associado (geralmente próximo ou por estrutura)
            # Simplificação: Busca elementos que pareçam email no painel direito
            # Ou usa o seletor específico se mapeado
            email_el = driver.find_element(By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["painel_direito"]["email_label"])
            # O valor costuma estar em um elemento irmão ou filho próximo. 
            # Assumindo estrutura padrão Zoho: Label <br> Value ou Label -> Parent -> Value
            # Vamos tentar pegar o texto do container pai do label
            parent = email_el.find_element(By.XPATH, "./..")
            text = parent.text
            # Extrair email do texto (regex simples)
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            if emails:
                details["email"] = emails[0]
        except Exception:
            pass

        # Telefone
        try:
            phone_el = driver.find_element(By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["painel_direito"]["celular_label"])
            parent = phone_el.find_element(By.XPATH, "./..")
            text = parent.text
            # Limpeza básica para pegar o número
            details["phone"] = text.replace("Celular", "").strip()
        except Exception:
            pass
            
        # Proprietário
        try:
            owner_el = driver.find_element(By.CSS_SELECTOR, ZHOO_DESK_SELECTORS["painel_direito"]["proprietario_contato"])
            parent = owner_el.find_element(By.XPATH, "./..")
            text = parent.text
            details["owner"] = text.replace("Proprietário do Contato", "").strip()
        except Exception:
            pass

    except Exception as e:
        logging.warning(f"Erro ao extrair detalhes do cliente: {e}")
        
    return details

def navigate_to_section(driver, section_name="minhas_conversas"):
    """
    (V3.17) Navega para uma seção do menu lateral.
    """
    try:
        # Busca direta pelo XPath mapeado em settings.py
        xpath = ZHOO_DESK_SELECTORS["menu_lateral"].get(section_name)
        
        if not xpath:
            # Fallback para nomes padronizados se a chave não bater exata
            if section_name == "minhas_conversas":
                xpath = ZHOO_DESK_SELECTORS["menu_lateral"]["minhas_conversas"]
            elif section_name == "nao_atribuidas":
                xpath = ZHOO_DESK_SELECTORS["menu_lateral"]["nao_atribuidas"]
            else:
                logging.warning(f"Seção '{section_name}' não encontrada nos seletores.")
                return False
            
        el = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        el.click()
        time.sleep(2) # Espera carregar a lista
        return True
    except Exception as e:
        logging.error(f"Erro ao navegar para {section_name}: {e}")
        return False

def get_conversation_items(driver):
    """
    (V3.17) Retorna lista de elementos de conversa na lista principal.
    """
    try:
        # Seletor genérico para itens da lista (ajustar conforme DOM real)
        # Baseado no mapeamento: div[role='region'] button
        # Mas precisamos de algo que pegue TODOS os itens
        # Vamos tentar um seletor mais amplo na região da lista
        items = driver.find_elements(By.CSS_SELECTOR, "div[role='region'] button[id^='7077']")
        return items
    except Exception as e:
        logging.error(f"Erro ao buscar itens de conversa: {e}")
        return []

def close_current_chat(driver):
    """
    (V3.17) Encerra o chat atual clicando no botão 'Encerrar'.
    """
    try:
        # Usa o XPath mapeado em settings.py
        xpath = ZHOO_DESK_SELECTORS["chat_ativo"]["acoes"]["encerrar_chat"]
        btn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath)))
        btn.click()
        logging.info("Botão 'Encerrar' clicado.")
        
        # Pode haver um modal de confirmação. Se houver, confirmar.
        # (Implementação futura se necessário)
        return True
    except Exception as e:
        logging.warning(f"Não foi possível encerrar o chat (ou botão não encontrado): {e}")
        return False

def wait_msgslist_ready(driver, timeout=20):
    """
    (SUBSTITUÍDO V3.8)
    Retorna o container msgsList NOVO e estável (com pelo menos 1 bubble OU mensagem de sistema).
    Re-localiza sempre (evita 'stale element').
    """
    wait = WebDriverWait(driver, timeout)
    # 1) garantir que existe um msgsList no DOM
    root = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-test-id='msgsList']")))
    # 2) garantir que tem conteúdo (bolha ou msg de sistema)
    wait.until(
        lambda d: len(d.find_elements(
            By.CSS_SELECTOR,
            "[data-id^='msgBubble_'], [data-test-id^='msgCont_'], "
            "[data-test-id='chatLayoutMessage'], [data-id^='msgtime_']"
        )) > 0
    )
    return root

def wait_conversation_change(driver, old_root, timeout=20):
    """
    (SUBSTITUÍDO V3.8)
    Espera o msgsList ANTIGO ficar 'stale' (DOM re-renderizou) e devolve o msgsList NOVO pronto.
    Use quando o usuário clicar em outra conversa.
    """
    wait = WebDriverWait(driver, timeout)
    try:
        logging.info(f"Aguardando 'staleness' do root antigo (ID: {old_root.id})")
        wait.until(EC.staleness_of(old_root))
        logging.info("Detecção: Root antigo ficou 'stale'.")
    except TimeoutException:
        # Se não ficou stale, pode ter sido mesma conversa; força re-busca assim mesmo.
        logging.warning("Timeout: Root antigo não ficou 'stale' (talvez a conversa não mudou?). Re-buscando mesmo assim.")
        pass
    
    logging.info("Aguardando novo root (msgsList) ficar pronto...")
    return wait_msgslist_ready(driver, timeout=timeout)

def extract_conversation_v2(driver, wait, logger):
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
    import time

    def safe_text(el):
        try:
            return (el.text or "").strip()
        except Exception:
            return ""

    def get_msgs_container():
        # container principal da timeline de mensagens (V3.8 - esta função é chamada por extract_conversation_v2)
        # Usamos a função global V3.8 para garantir que está pronto
        return wait_msgslist_ready(driver, timeout=wait._timeout)


    def scroll_through_all(container, logger):
        # lista pode ser virtualizada. Estratégia:
        # 1) roda pra cima até não aumentar o número de bubbles (p/ carregar histórico)
        # 2) roda pra baixo até estabilizar (p/ garantir finais recentes)
        seen = set()
        stable_hits = 0

        # Seletor de Bubble Refinado (V3.3)
        bubble_selector = "div.zim99e01f504d[data-id^='msgBubble_']"

        def count_bubbles():
            return len(container.find_elements(By.CSS_SELECTOR, bubble_selector))

        # fase 1: pra cima (histórico)
        for _ in range(40):
            before = count_bubbles()
            driver.execute_script("arguments[0].scrollTop = 0;", container)
            time.sleep(0.6)
            after = count_bubbles()
            # Refinado V3.3
            ids = [e.get_attribute("data-id") for e in container.find_elements(By.CSS_SELECTOR, bubble_selector)]
            new = 0
            for i in ids:
                if i not in seen:
                    seen.add(i); new += 1
            if after == before or new == 0:
                stable_hits += 1
            else:
                stable_hits = 0
            if stable_hits >= 3:
                break

        # fase 2: pra baixo (parte recente)
        stable_hits = 0
        for _ in range(40):
            before = count_bubbles()
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", container)
            time.sleep(0.6)
            after = count_bubbles()
            # Refinado V3.3
            ids = [e.get_attribute("data-id") for e in container.find_elements(By.CSS_SELECTOR, bubble_selector)]
            new = 0
            for i in ids:
                if i not in seen:
                    seen.add(i); new += 1
            if after == before or new == 0:
                stable_hits += 1
            else:
                stable_hits = 0
            if stable_hits >= 3:
                break

        logger.info(f"📜 Varredura concluída. Bubbles vistos (únicos): {len(seen)}")
        return seen

    def classify_author(bubble_el, nome_cliente_guess):
        # 1) avatar -> cliente vs agente
        avatar_title = ""
        try:
            av = bubble_el.find_element(By.CSS_SELECTOR, "[data-test-id='Avatar'] [data-test-id='Avatar_AvatarImg']")
            src = av.get_attribute("src") or ""
            # tenta obter nome pelo container do avatar (irmãos)
            try:
                avatar_box = bubble_el.find_element(By.CSS_SELECTOR, "[data-test-id='Avatar']")
                t = avatar_box.get_attribute("data-title") or ""
                if t.strip():
                    avatar_title = t.strip()
            except Exception:
                pass

            if "contactAvatar" in src:
                # geralmente é contato/cliente
                return "cliente", avatar_title or nome_cliente_guess
            if "defaultAvatar" in src:
                # tende a ser agente
                return "agente", avatar_title or ""
        except Exception:
            pass

        # 2) “msg informativa / sistema” (Seletores V3.2/V3.3)
        try:
            if bubble_el.find_elements(By.CSS_SELECTOR, ".zima045fbd324, [data-id^='msgContent_'], [data-test-id='chatLayoutMessage']"):
                # ex: “O chat foi encerrado”, “Chat atribuído…”, “Resposta/Feedback” layout
                return "sistema", "Sistema"
        except Exception:
            pass

        # 3) fallback por pistas visuais
        try:
            # duplo check geralmente em mensagens do time
            if bubble_el.find_elements(By.CSS_SELECTOR, "#IM_doubleTick, #GC_doubletick"):
                return "agente", avatar_title or ""
        except Exception:
            pass

        # 4) heurística pelo nome do cabeçalho do bubble (quando existe)
        if avatar_title:
            if nome_cliente_guess and avatar_title.strip().lower() == nome_cliente_guess.strip().lower():
                return "cliente", avatar_title
            return "agente", avatar_title

        # último recurso: desconhecido -> tratar como cliente (para não zerar “última do cliente”)
        return "cliente", nome_cliente_guess

    def extract_time(bubble_el):
        # blocos com <div class="zimee70af722c ... " data-title="27/10/2025 10:54">
        try:
            t = bubble_el.find_element(By.CSS_SELECTOR, ".zimee70af722c[data-title], [data-title][class*='zimee70af']")
            return t.get_attribute("data-title") or ""
        except Exception:
            pass
        # às vezes vem no container pai
        try:
            t = bubble_el.find_element(By.CSS_SELECTOR, "[data-msgtime]")
            iso = t.get_attribute("data-msgtime") or ""
            return iso  # deixa ISO se não tiver conversão
        except Exception:
            return ""

    def extract_text(bubble_el):
        # texto principal
        parts = []

        # Seletores Refinados V3.3
        for sel in [
            ".zimf03631d94c > span.zim732f7a00a1",  # texto comum (Refinado V3.3)
            "[data-id^='msgContent_']",             # mensagens de sistema
            ".zima045fbd324",                       # encerramento (Refinado V3.3)
            "[data-test-id='chatLayoutMessage']",   # GC/Bot (Refinado V3.3)
            "[data-test-id='containerComponent'] .zimd14c2bce7e span",  # “Resposta ...”/feedback
            ".zim95a432ad35",                       # anexos: cabeçalho
            ".zim5acc4ea294",                       # nome do arquivo (anexo)
        ]:
            try:
                for n in bubble_el.find_elements(By.CSS_SELECTOR, sel):
                    txt = safe_text(n)
                    if txt:
                        parts.append(txt)
            except Exception:
                pass

        # de-duplicação simples mantendo ordem
        seen = set()
        ordered = []
        for p in parts:
            if p not in seen:
                seen.add(p)
                ordered.append(p)
        return " | ".join(ordered).strip()

    # ===== execução =====
    logger.info("[BUSCAR] Iniciando extração V3.3 (lista virtualizada, seletores refinados)...")
    
    # nome do cliente no header/topo (usando lógica V3.3)
    nome_cliente = _get_selected_tab_name(driver)
    if nome_cliente:
        logger.info(f"👤 Nome do cliente (menu lateral): {nome_cliente}")
    else:
        logger.warning("Não foi possível ler o nome do cliente no menu lateral.")

    # (V3.17) Extrair detalhes adicionais do painel lateral
    client_details = extract_client_details(driver)
    if client_details.get("email"):
        logger.info(f"📧 Email detectado: {client_details['email']}")
    if client_details.get("phone"):
        logger.info(f"📱 Telefone detectado: {client_details['phone']}")

    # pega container e varre toda a lista
    container = get_msgs_container()
    _ = scroll_through_all(container, logger)

    # Seletor de Bubble Refinado (V3.3)
    bubbles = container.find_elements(By.CSS_SELECTOR, "div.zim99e01f504d[data-id^='msgBubble_']")
    logger.info(f"🧩 Bubbles (reais) localizados para extração: {len(bubbles)}")
    
    # Incluir mensagens de sistema que não são 'bubbles' (Refinado V3.3)
    system_msgs = container.find_elements(By.CSS_SELECTOR, ".zima045fbd324, [data-test-id='chatLayoutMessage']")
    logger.info(f"🧩 Mensagens (sistema/GC) localizadas: {len(system_msgs)}")
    
    all_elements = bubbles + system_msgs
    logger.info(f"Total de elementos para processar: {len(all_elements)}")

    msgs = []
    for b in all_elements:
        try:
            texto = extract_text(b)
            if not texto:
                continue
            data_hora = extract_time(b)
            autor_tipo, autor_nome = classify_author(b, nome_cliente_guess=nome_cliente)
            
            # Se o nome do cliente ainda não foi pego e apareceu no avatar, atualiza
            if not nome_cliente and autor_tipo == 'cliente' and autor_nome:
                nome_cliente = autor_nome
                logger.info(f"👤 Nome do cliente (fallback avatar): {nome_cliente}")

            msgs.append({
                "author_type": autor_tipo,
                "author_name": autor_nome,
                "text": texto,
                "time": data_hora
            })
        except StaleElementReferenceException:
            # em listas virtualizadas, pode sumir; ignora e segue
            continue
        except Exception as e:
            logger.warning(f"Erro ao processar elemento: {e}")
            continue

    # ordenar por tempo quando possível (mantém ordem natural como fallback)
    def time_key(m):
        return (m.get("time") or "", m.get("text") or "")
    msgs_sorted = sorted(msgs, key=time_key)
    logger.info(f"[OK] Mensagens extraídas e ordenadas: {len(msgs_sorted)}")

    # calcula últimas
    ultima_cli = next((m["text"] for m in reversed(msgs_sorted) if m["author_type"] == "cliente" and m.get("text")), "")
    ultima_age = next((m["text"] for m in reversed(msgs_sorted) if m["author_type"] == "agente" and m.get("text")), "")
    
    logger.info(f"💬 Última do cliente: {ultima_cli[:140] if ultima_cli else '(—)'}")
    logger.info(f"[USUARIO] Última do agente: {ultima_age[:140] if ultima_age else '(—)'}")

    return {
        "cliente_nome": nome_cliente or "",
        "cliente_detalhes": client_details, # (V3.17)
        "ultima_msg_cliente": ultima_cli,
        "ultima_msg_agente": ultima_age,
        "mensagens": msgs_sorted
    }

def _ensure_composer_visible(driver, timeout=15):
    wait = WebDriverWait(driver, timeout)
    composer = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, COMPOSER_CSS)))
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", composer)
    return composer

def _js_set_html_and_fire(driver, el, html):
    driver.execute_script("""
        const el = arguments[0];
        const html = arguments[1];
        // substitui o conteúdo mantendo a estrutura esperada pelo ProseMirror
        el.innerHTML = html;

        // move caret para o fim
        const sel = window.getSelection();
        const range = document.createRange();
        range.selectNodeContents(el);
        range.collapse(false);
        sel.removeAllRanges();
        sel.addRange(range);

        // dispara eventos para o app "sentir" a digitação
        el.dispatchEvent(new InputEvent('input', {bubbles: true, cancelable: true, inputType: 'insertText'}));
        el.dispatchEvent(new Event('change', {bubbles: true}));
        el.dispatchEvent(new KeyboardEvent('keyup', {bubbles:true, key:' ', code:'Space'}));
    """, el, html)

def preencher_resposta_no_zoho(driver, texto, timeout=15):
    """
    (V3.10) Escreve a resposta no composer do Zoho **sem enviar**.
    Aceita texto com \n e formata em <p>...</p>.
    """
    composer = _ensure_composer_visible(driver, timeout=timeout)

    # 1) foco
    composer.click()

    # 2) limpeza por teclado (placeholder + texto prévio)
    composer.send_keys(Keys.CONTROL, 'a')
    composer.send_keys(Keys.DELETE)

    # 3) limpeza defensiva (JS) caso algo resista
    #    (remove nós residuais de placeholder)
    try:
        driver.execute_script("""
            const el = arguments[0];
            if (el) {
                el.innerHTML = '<p><br></p>';
            }
        """, composer)
    except Exception:
        pass

    # 4) normaliza o texto: quebra em parágrafos
    linhas = [ln.strip() for ln in texto.replace("\r\n", "\n").split("\n")]
    # cria <p> para cada linha; linhas vazias viram <p><br></p>
    partes = [f"<p>{ln if ln else '<br>'}</p>" for ln in linhas]
    html = "".join(partes)

    # 5) injeta e dispara eventos
    _js_set_html_and_fire(driver, composer, html)

    # 6) toque final: teclado leve p/ garantir estado “dirty”
    composer.send_keys(" ")
    composer.send_keys(Keys.BACKSPACE)
