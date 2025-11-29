# Sistema de Logging Colorido - Assistente Stefan

## Visão Geral

O sistema de logging colorido melhora significativamente a legibilidade da saída no CMD do Windows, usando cores e formatação estruturada para facilitar o acompanhamento da execução do bot.

## Instalação

O sistema já está configurado! A dependência `colorama` já foi instalada.

## Demonstração

Para ver o sistema em ação, execute:

```bash
python demo_colors.py
```

## Funções Disponíveis

### 1. Cabeçalhos e Seções

```python
from utils.colored_logger import print_header, print_section

# Cabeçalho principal
print_header(
    title="ASSISTENTE STEFAN",
    subtitle="Automacao Zoho Desk + Gemini AI",
    version="3.17"
)

# Separador de seção
print_section("PROCESSAMENTO DE CONVERSA")
```

### 2. Mensagens de Status

```python
from utils.colored_logger import print_success, print_error, print_warning, print_info

print_success("Operacao concluida com sucesso!")  # Verde
print_error("Erro ao processar arquivo")           # Vermelho
print_warning("Atencao: Arquivo grande")           # Amarelo
print_info("Carregando modulos...")                # Ciano
```

### 3. Exibição de Dados

```python
from utils.colored_logger import print_data

print_data("Cliente", "Paulo Renato")
print_data("Email", "paulo@email.com")
print_data("Telefone", "+55-11-99999-9999")
```

### 4. Passos do Processo

```python
from utils.colored_logger import print_step

print_step(1, 5, "Iniciando navegador...")
print_step(2, 5, "Fazendo login...")
print_step(3, 5, "Carregando conversa...")
```

### 5. Barra de Progresso

```python
from utils.colored_logger import print_progress

for i in range(1, 101):
    print_progress(i, 100, f"Processando item {i}/100")
    time.sleep(0.05)
```

### 6. Caixas de Informação

```python
from utils.colored_logger import print_box

print_box(
    title="ULTIMA MENSAGEM",
    content_lines=[
        "De: Cliente",
        "Data: 29/11/2024",
        "",
        "Conteudo da mensagem aqui"
    ]
)
```

### 7. Resumo Final

```python
from utils.colored_logger import print_summary

print_summary(
    title="RESUMO DA EXECUCAO",
    data_dict={
        "Cliente": "Paulo Renato",
        "Mensagens": "20",
        "Tempo": "22.5s"
    },
    status="SUCESSO"  # ou "ERRO" ou "AVISO"
)
```

## Cores Utilizadas

- **Verde**: Sucesso, confirmações
- **Vermelho**: Erros, falhas
- **Amarelo**: Avisos, atenção
- **Ciano**: Informações, dados
- **Magenta**: Seções, separadores
- **Azul**: Passos do processo

## Integração no Código Existente

### Exemplo Simples

```python
from utils.colored_logger import print_info, print_success, print_error

print_info("Iniciando processo...")

try:
    # Seu código aqui
    resultado = processar_algo()
    print_success("Processo concluido!")
except Exception as e:
    print_error(f"Erro: {e}")
```

### Logging Configurável

```python
from utils.colored_logger import setup_colored_logging

# Configura logging com cores e arquivo
logger = setup_colored_logging(log_file="logs/execucao.log")

# Agora use o logging normal
import logging
logging.info("Mensagem com cor!")
logging.error("Erro com cor!")
```

## Notas Importantes

1. **Encoding**: O sistema foi otimizado para Windows CMD usando apenas caracteres ASCII
2. **Emojis**: Evite usar emojis nas mensagens (causam erro de encoding)
3. **Acentos**: Evite acentos em mensagens críticas (podem não aparecer corretamente)
4. **Cores**: As cores funcionam automaticamente no Windows graças ao `colorama`

## Próximos Passos

Para integrar no código principal (`core/zoho.py`), substitua:

```python
# Antes
logging.info("Mensagem")

# Depois
from utils.colored_logger import print_info
print_info("Mensagem")
```

Ou use o `setup_colored_logging()` para manter o logging padrão com cores.
