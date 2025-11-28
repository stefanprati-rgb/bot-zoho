import sys
from core.zoho import ZohoDeskAutomator

def main():
    """Função principal"""
    print("⚡ ASSISTENTE STEFAN V3.16 - CORREÇÃO MAX_TOKENS E NOME")
    print("=" * 60)
    print("Versão com Safety Settings para evitar bloqueios de API")
    print("Recursos: Extração (JSON, CSV, TXT), Gemini 2.5-flash (rápido)")
    print("=" * 60)
    
    automator = ZohoDeskAutomator()
    
    try:
        automator.run()
    except KeyboardInterrupt:
        print("\n[ERRO] Execução interrompida pelo usuário")
    except Exception as e:
        print(f"[ERRO] Erro fatal: {e}")
    finally:
        print("\n👋 Assistente finalizado.")

if __name__ == "__main__":
    main()
