"""
Sistema de logging colorido e formatado para o terminal.
Usa colorama para compatibilidade com Windows CMD.
"""

from colorama import Fore, Back, Style, init
import logging
from datetime import datetime

# Inicializa colorama para Windows
init(autoreset=True)

class ColoredFormatter(logging.Formatter):
    """Formatter customizado com cores para diferentes níveis de log."""
    
    # Cores para cada nível de log
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE + Style.BRIGHT,
    }
    
    # Ícones para cada tipo de mensagem
    ICONS = {
        'DEBUG': '🔍',
        'INFO': '✓',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🚨',
    }
    
    def format(self, record):
        # Pega a cor e ícone baseado no nível
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        icon = self.ICONS.get(record.levelname, '•')
        
        # Formata a mensagem
        timestamp = datetime.fromtimestamp(record.created).strftime('%H:%M:%S')
        
        # Mensagem colorida
        formatted = f"{Fore.CYAN}[{timestamp}]{Style.RESET_ALL} {color}{icon} {record.msg}{Style.RESET_ALL}"
        
        return formatted


def print_header(title, subtitle="", version=""):
    """Imprime um cabeçalho estilizado."""
    width = 70
    
    print("\n" + Fore.CYAN + "=" * width + Style.RESET_ALL)
    print(Fore.GREEN + Style.BRIGHT + f"  {title}".center(width) + Style.RESET_ALL)
    
    if version:
        print(Fore.YELLOW + f"v{version}".center(width) + Style.RESET_ALL)
    
    if subtitle:
        print(Fore.WHITE + subtitle.center(width) + Style.RESET_ALL)
    
    print(Fore.CYAN + "=" * width + Style.RESET_ALL + "\n")


def print_section(title):
    """Imprime um separador de seção."""
    print(f"\n{Fore.MAGENTA}{'-' * 70}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA + Style.BRIGHT}> {title}{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}{'-' * 70}{Style.RESET_ALL}\n")


def print_success(message):
    """Imprime mensagem de sucesso."""
    print(f"{Fore.GREEN}[OK] {message}{Style.RESET_ALL}")


def print_error(message):
    """Imprime mensagem de erro."""
    print(f"{Fore.RED}[ERRO] {message}{Style.RESET_ALL}")


def print_warning(message):
    """Imprime mensagem de aviso."""
    print(f"{Fore.YELLOW}[AVISO] {message}{Style.RESET_ALL}")


def print_info(message):
    """Imprime mensagem informativa."""
    print(f"{Fore.CYAN}[INFO] {message}{Style.RESET_ALL}")


def print_step(step_number, total_steps, description):
    """Imprime um passo do processo."""
    print(f"{Fore.BLUE}[{step_number}/{total_steps}]{Style.RESET_ALL} {description}")


def print_data(label, value, color=Fore.WHITE):
    """Imprime um par label-valor formatado."""
    print(f"{Fore.CYAN}{label}:{Style.RESET_ALL} {color}{value}{Style.RESET_ALL}")


def print_box(title, content_lines, color=Fore.GREEN):
    """Imprime conteúdo em uma caixa."""
    width = 70
    
    print(f"\n{color}+{'-' * (width - 2)}+{Style.RESET_ALL}")
    print(f"{color}|{Style.RESET_ALL} {Style.BRIGHT}{title.center(width - 4)}{Style.RESET_ALL} {color}|{Style.RESET_ALL}")
    print(f"{color}+{'-' * (width - 2)}+{Style.RESET_ALL}")
    
    for line in content_lines:
        # Preenche com espaços para alinhar
        padding = width - 4 - len(line)
        print(f"{color}|{Style.RESET_ALL} {line}{' ' * padding} {color}|{Style.RESET_ALL}")
    
    print(f"{color}+{'-' * (width - 2)}+{Style.RESET_ALL}\n")


def print_summary(title, data_dict, status="SUCESSO"):
    """Imprime um resumo formatado."""
    width = 70
    
    # Define cor baseada no status
    if status == "SUCESSO":
        status_color = Fore.GREEN
        icon = "OK"
    elif status == "ERRO":
        status_color = Fore.RED
        icon = "ERRO"
    else:
        status_color = Fore.YELLOW
        icon = "AVISO"
    
    print(f"\n{Fore.CYAN}{'=' * width}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}|{Style.RESET_ALL} {Style.BRIGHT}{title.center(width - 4)}{Style.RESET_ALL} {Fore.CYAN}|{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * width}{Style.RESET_ALL}")
    
    # Status
    status_line = f"{icon} Status: {status}"
    padding = width - 4 - len(status_line)
    print(f"{Fore.CYAN}|{Style.RESET_ALL} {status_color}{status_line}{Style.RESET_ALL}{' ' * padding} {Fore.CYAN}|{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'-' * width}{Style.RESET_ALL}")
    
    # Dados
    for label, value in data_dict.items():
        line = f"{label}: {value}"
        padding = width - 4 - len(line)
        print(f"{Fore.CYAN}|{Style.RESET_ALL} {line}{' ' * padding} {Fore.CYAN}|{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'=' * width}{Style.RESET_ALL}\n")


def print_progress(current, total, description=""):
    """Imprime uma barra de progresso."""
    percentage = int((current / total) * 100)
    filled = int((current / total) * 40)
    bar = "#" * filled + "-" * (40 - filled)
    
    print(f"\r{Fore.CYAN}[{bar}]{Style.RESET_ALL} {percentage}% {description}", end="", flush=True)
    
    if current == total:
        print()  # Nova linha ao completar


def setup_colored_logging(log_file=None):
    """Configura o sistema de logging com cores."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove handlers existentes
    logger.handlers.clear()
    
    # Handler para console com cores
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(ColoredFormatter())
    logger.addHandler(console_handler)
    
    # Handler para arquivo (sem cores)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger
