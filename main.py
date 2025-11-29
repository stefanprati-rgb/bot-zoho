import sys
from core.zoho import ZohoDeskAutomator
from utils.colored_logger import print_header, print_error, print_success, print_info

def main():
    """Função principal"""
    # Cabeçalho estilizado
    print_header(
        title="ASSISTENTE STEFAN",
        subtitle="Automação Zoho Desk + Gemini AI",
        version="3.17"
    )
    
    print_info("🚀 Inicializando sistema...")
    print_info("📦 Recursos: Extração (JSON, CSV, TXT), Gemini 2.5-flash")
    print_info("🔒 Safety Settings ativado para evitar bloqueios")
    print()
    
    automator = ZohoDeskAutomator()
    
    try:
        automator.run()
    except KeyboardInterrupt:
        print()
        print_error("Execução interrompida pelo usuário")
    except Exception as e:
        print()
        print_error(f"Erro fatal: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print()
        print_success("👋 Assistente finalizado com sucesso!")

if __name__ == "__main__":
    main()
