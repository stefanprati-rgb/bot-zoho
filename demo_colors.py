"""
Script de demonstração do sistema de logging colorido.
Execute este arquivo para ver como ficará a saída no CMD.
"""

from utils.colored_logger import (
    print_header, print_section, print_success, print_error,
    print_warning, print_info, print_data, print_box,
    print_summary, print_step, print_progress, setup_colored_logging
)
import time

def demo():
    """Demonstração do sistema colorido"""
    
    # Cabeçalho principal
    print_header(
        title="ASSISTENTE STEFAN",
        subtitle="Sistema de Logging Colorido - Demonstração",
        version="3.17"
    )
    
    # Informações iniciais
    print_info("Inicializando sistema...")
    print_info("Carregando módulos...")
    print_success("Módulos carregados com sucesso!")
    print()
    
    # Seção de configuração
    print_section("CONFIGURACAO DO SISTEMA")
    
    print_data("Navegador", "Microsoft Edge")
    print_data("Perfil", "Profile 1")
    print_data("Gemini Model", "2.5-flash")
    print_data("Temperature", "0.6")
    print()
    
    # Simulando passos
    print_section("PROCESSO DE LOGIN")
    
    print_step(1, 3, "Abrindo navegador...")
    time.sleep(0.5)
    print_success("Navegador aberto!")
    
    print_step(2, 3, "Carregando Zoho Desk...")
    time.sleep(0.5)
    print_success("Zoho Desk carregado!")
    
    print_step(3, 3, "Verificando sessao...")
    time.sleep(0.5)
    print_success("Sessao ativa detectada!")
    print()
    
    # Seção de extração
    print_section("EXTRACAO DE CONVERSA")
    
    print_info("Aguardando selecao de conversa...")
    time.sleep(0.3)
    print_success("Conversa selecionada: Paulo Renato")
    
    print_data("Cliente", "Paulo Renato Goncalves")
    print_data("Email", "paulorenatosantos1967@gmail.com")
    print_data("Telefone", "+55-179-916-47078")
    print_data("Mensagens", "20")
    print()
    
    # Barra de progresso
    print_info("Processando mensagens...")
    for i in range(1, 21):
        print_progress(i, 20, f"Mensagem {i}/20")
        time.sleep(0.1)
    print()
    
    # Avisos e erros (exemplos)
    print_warning("Atencao: Algumas mensagens contem anexos")
    print_info("Exportando para CSV...")
    print_success("CSV exportado com sucesso!")
    print()
    
    # Box com informações
    print_box(
        title="ULTIMA MENSAGEM DO CLIENTE",
        content_lines=[
            "De: Paulo Renato",
            "Data: 28/11/2024 16:49",
            "",
            "Sim este e o meu mail",
        ]
    )
    
    # Seção Gemini
    print_section("PROCESSAMENTO GEMINI AI")
    
    print_info("Enviando contexto para Gemini...")
    time.sleep(0.5)
    print_success("Contexto enviado!")
    
    print_info("Aguardando resposta...")
    time.sleep(1)
    print_success("Resposta recebida!")
    
    print_data("Tokens usados", "450")
    print_data("Tempo de resposta", "6.2s")
    print()
    
    # Resumo final
    print_summary(
        title="RESUMO DA EXECUCAO",
        data_dict={
            "Cliente": "Paulo Renato Goncalves",
            "Mensagens processadas": "20",
            "Tamanho total": "4.737 caracteres",
            "Tempo de processamento": "22.5 segundos",
            "Data/Hora": "28/11/2024 as 16:58:08"
        },
        status="SUCESSO"
    )
    
    # Exemplo de erro (comentado para não assustar)
    # print_error("Erro ao conectar com o servidor!")
    
    print_success("Demonstracao concluida com sucesso!")
    print()

if __name__ == "__main__":
    demo()
