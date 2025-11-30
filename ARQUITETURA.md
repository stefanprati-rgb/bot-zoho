# 🏗️ Arquitetura Técnica - Assistente Stefan

## Visão Geral da Arquitetura

O Assistente Stefan utiliza uma arquitetura modular baseada em camadas, com separação clara de responsabilidades.

## Camadas da Aplicação

### 1. Camada de Apresentação (UI)
- **Terminal Colorido**: Interface visual no CMD
- **Prompts Interativos**: Confirmações e inputs do usuário
- **Logging Estruturado**: Mensagens categorizadas e formatadas

### 2. Camada de Orquestração
- **ZohoDeskAutomator** (`core/zoho.py`)
  - Gerencia o fluxo completo de execução
  - Coordena navegador, Gemini e utilitários
  - Implementa modos Manual e Autopilot

### 3. Camada de Integração
- **GeminiWebClient** (`core/gemini_web.py`)
  - Dual-tab architecture
  - Comunicação com Gemini via web
  - Limpeza de respostas

- **Selenium Utils** (`core/selenium_utils.py`)
  - Automação do navegador
  - Extração de dados
  - Navegação e interação

### 4. Camada de Dados
- **Exportação**: JSON, CSV, TXT
- **Backup**: Conversas completas
- **Logging**: Histórico de execução

## Padrões de Design Utilizados

### 1. Singleton Pattern
- **Configurações**: `settings.py` centraliza todas as configurações

### 2. Strategy Pattern
- **Modos de Operação**: Manual vs Autopilot
- **Extração**: Múltiplos seletores com fallback

### 3. Observer Pattern
- **Staleness Detection**: Monitora mudanças no DOM

### 4. Factory Pattern
- **Criação de Exportações**: JSON, CSV, TXT

## Fluxo de Dados

```
┌─────────────┐
│   Usuário   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│   ZohoDeskAutomator (main)      │
│  - Gerencia sessão              │
│  - Coordena componentes         │
└──────┬──────────────────┬───────┘
       │                  │
       ▼                  ▼
┌──────────────┐   ┌──────────────┐
│ Selenium     │   │ Gemini Web   │
│ Utils        │   │ Client       │
│              │   │              │
│ - Extração   │   │ - Prompts    │
│ - Navegação  │   │ - Respostas  │
└──────┬───────┘   └──────┬───────┘
       │                  │
       ▼                  ▼
┌─────────────────────────────────┐
│      Processamento de Dados     │
│  - Limpeza                      │
│  - Formatação                   │
│  - Validação                    │
└──────┬──────────────────────────┘
       │
       ▼
┌─────────────────────────────────┐
│      Persistência               │
│  - Backup (JSON, CSV, TXT)      │
│  - Logs                         │
│  - Output                       │
└─────────────────────────────────┘
```

## Componentes Detalhados

### ZohoDeskAutomator

**Responsabilidades:**
- Inicialização do navegador
- Gerenciamento de login
- Loop de processamento
- Coordenação entre componentes

**Métodos Principais:**
```python
def start_browser() -> bool
def login() -> bool
def process_conversation() -> Tuple[bool, str, Dict]
def run() -> None
def run_autopilot() -> None
```

### GeminiWebClient

**Responsabilidades:**
- Gerenciamento de abas (Dual-Tab)
- Envio de prompts
- Captura de respostas
- Limpeza de formatação

**Métodos Principais:**
```python
def open_gemini() -> bool
def send_message(text: str) -> bool
def get_last_response(timeout: int) -> str
def switch_back_to_zoho() -> None
```

### Selenium Utils

**Responsabilidades:**
- Extração de conversas
- Detecção de mudanças
- Navegação entre seções
- Preenchimento de campos

**Funções Principais:**
```python
def extract_conversation_v2(driver, wait, logger) -> Dict
def wait_conversation_change(driver, old_root, timeout) -> WebElement
def wait_msgslist_ready(driver, timeout) -> WebElement
def preencher_resposta_no_zoho(driver, texto, timeout) -> None
```

## Gestão de Estado

### Estado da Sessão
- **Navegador**: WebDriver instance
- **Abas**: Zoho tab, Gemini tab
- **Conversa Atual**: Root element, mensagens

### Estado de Processamento
- **Conversas Processadas**: Set de IDs (Autopilot)
- **Última Conversa**: Root element para staleness detection

## Tratamento de Erros

### Estratégias

1. **Retry com Fallback**
   - Múltiplos seletores CSS
   - Tentativas com delays incrementais

2. **Graceful Degradation**
   - Continua execução em caso de falha não-crítica
   - Logs detalhados para debugging

3. **User Intervention**
   - Solicita ação manual quando necessário (OTP)
   - Confirmações antes de ações críticas

### Hierarquia de Exceções

```
Exception
├── TimeoutException (Selenium)
├── NoSuchElementException (Selenium)
├── StaleElementReferenceException (Selenium)
└── Custom Exceptions
    ├── LoginFailedException
    ├── ConversationExtractionException
    └── GeminiResponseException
```

## Performance e Otimização

### Técnicas Utilizadas

1. **Dual-Tab Architecture**
   - Gemini em aba separada
   - Evita recarregamentos
   - Reduz latência

2. **Staleness Detection**
   - Detecta mudanças sem polling excessivo
   - Espera inteligente por elementos

3. **Caching**
   - Perfil do navegador persistente
   - Sessão mantida entre execuções

4. **Lazy Loading**
   - Elementos carregados sob demanda
   - Scroll virtual suportado

## Segurança

### Medidas Implementadas

1. **Credenciais**
   - Armazenadas em `settings.py` (não commitado com valores reais)
   - Uso de variáveis de ambiente recomendado

2. **Sessão**
   - Perfil do navegador isolado
   - Cookies e cache gerenciados

3. **Dados**
   - Backups locais apenas
   - Sem transmissão de dados sensíveis

## Escalabilidade

### Limitações Atuais
- Processamento sequencial (uma conversa por vez)
- Dependência de interface web (Selenium)
- Single-threaded

### Possíveis Melhorias
- Processamento paralelo de conversas
- API direta do Zoho (se disponível)
- Multi-threading para I/O

## Manutenibilidade

### Boas Práticas

1. **Separação de Responsabilidades**
   - Cada módulo tem função clara
   - Baixo acoplamento

2. **Configuração Centralizada**
   - `settings.py` único ponto de configuração
   - Seletores CSS organizados

3. **Logging Abrangente**
   - Todos os passos logados
   - Níveis apropriados (INFO, WARNING, ERROR)

4. **Documentação**
   - Docstrings em funções
   - README detalhado
   - Comentários inline quando necessário

## Testes

### Estratégia de Testes

1. **Manual**
   - Execução completa do fluxo
   - Verificação visual das respostas

2. **Demonstração**
   - `demo_colors.py` para sistema de logging
   - Validação de componentes visuais

### Áreas para Testes Automatizados (Futuro)

- Unit tests para funções de processamento
- Integration tests para fluxo completo
- Mock do Selenium para testes rápidos

## Monitoramento

### Logs

- **Arquivo**: `logs/execucao_YYYYMMDD_HHMMSS.txt`
- **Console**: Output colorido em tempo real
- **Níveis**: INFO, WARNING, ERROR, CRITICAL

### Métricas

- Tempo de processamento por conversa
- Taxa de sucesso/falha
- Número de mensagens processadas

## Diagramas

### Diagrama de Sequência - Processamento de Conversa

```
Usuário -> Main: Seleciona conversa
Main -> Zoho: Extrai dados
Zoho -> SeleniumUtils: extract_conversation_v2()
SeleniumUtils --> Zoho: conversation_data
Zoho -> GeminiWeb: send_message(prompt)
GeminiWeb -> Gemini: POST prompt
Gemini --> GeminiWeb: response
GeminiWeb -> GeminiWeb: clean_markdown()
GeminiWeb --> Zoho: cleaned_response
Zoho -> SeleniumUtils: preencher_resposta()
SeleniumUtils --> Zoho: OK
Zoho -> Utils: export_to_csv/txt()
Utils --> Zoho: files_saved
Zoho --> Main: success
Main --> Usuário: Exibe resumo
```

### Diagrama de Classes (Simplificado)

```
┌─────────────────────┐
│ ZohoDeskAutomator   │
├─────────────────────┤
│ - driver            │
│ - gemini_web        │
├─────────────────────┤
│ + start_browser()   │
│ + login()           │
│ + process_conv()    │
│ + run()             │
└──────────┬──────────┘
           │
           │ uses
           ▼
┌─────────────────────┐
│ GeminiWebClient     │
├─────────────────────┤
│ - driver            │
│ - gemini_tab        │
│ - zoho_tab          │
├─────────────────────┤
│ + open_gemini()     │
│ + send_message()    │
│ + get_response()    │
└─────────────────────┘
```

## Conclusão

A arquitetura do Assistente Stefan foi projetada para ser:
- **Modular**: Fácil manutenção e extensão
- **Robusta**: Tratamento de erros e fallbacks
- **Eficiente**: Otimizações de performance
- **Escalável**: Preparada para crescimento futuro

---

**Documento técnico - Versão 3.17**
**Última atualização: 29/11/2024**
