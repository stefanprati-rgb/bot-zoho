import logging
import time
from typing import Dict, List, Any
import google.generativeai as genai

from config.settings import SYSTEM_PROMPT

class GeminiAnalyzer:
    """Analisador e gerador de respostas com Google Gemini (V3.4)"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = None
        self._configure_gemini()
    
    def _configure_gemini(self):
        """Configura a API do Gemini com parâmetros otimizados (V3.15)"""
        try:
            genai.configure(api_key=self.api_key)
    
            # Configuração otimizada V3.16 - Ajuste de max_output_tokens
            generation_config = {
                "candidate_count": 1,
                "max_output_tokens": 2048,  # permite respostas mais longas
                "temperature": 0.6,
                "top_p": 0.8,
                "top_k": 32,
            }
    
            # Safety Settings V3.15 - Mais permissivo para contexto empresarial
            safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            ]
    
            self.model = genai.GenerativeModel(
                'gemini-2.5-flash',
                generation_config=generation_config,
                safety_settings=safety_settings
            )
    
            logging.info("[OK] API Gemini configurada com sucesso (Modo V3.15 - Com Safety Settings)!")
            logging.info(f"[CONFIG] Parâmetros: {generation_config}")
            logging.info(f"[SEGUR] Safety: BLOCK_NONE (contexto empresarial)")
    
        except Exception as e:
            logging.error(f"[ERRO] Erro ao configurar Gemini: {e}")
            raise
    
    def analyze_conversation(self, conversation_data: Dict[str, Any]) -> str:
        """
        Analisa conversa e gera resposta contextualizada (V3.14 - CORREÇÃO COMPLETA)
    
        Args:
            conversation_data: Dados da conversa extraídos (FORMATO V3.3)
    
        Returns:
            Resposta gerada pelo Gemini
        """
        try:
            # CORREÇÃO: O texto solto abaixo foi removido
            # Gere uma resposta adequada como Stefan da Era Verde Energia (lembre-se da diretiva de concisão):"""
            
            # Construir o prompt (V3.4 - Otimizado)
            client_name = conversation_data.get("cliente_nome", "Cliente")
            client_details = conversation_data.get("cliente_detalhes", {})
            ultima_msg = conversation_data.get("ultima_msg_cliente", "")
            historico_formatado = self._format_conversation_history(conversation_data.get("mensagens", []))
    
            # Formatar detalhes do cliente para o prompt
            detalhes_str = ""
            if client_details:
                detalhes_str = f"""
DADOS DO CLIENTE (Do CRM):
- Email: {client_details.get('email', 'N/A')}
- Telefone: {client_details.get('phone', 'N/A')}
- Proprietário: {client_details.get('owner', 'N/A')}
"""

            prompt_completo = f"""{SYSTEM_PROMPT}

---
HISTÓRICO DA CONVERSA (Últimos 20):
{historico_formatado}
---
{detalhes_str}
---
ÚLTIMA MENSAGEM DO CLIENTE ({client_name}):
{ultima_msg}
---

INSTRUÇÃO DE AÇÃO:
Se o cliente estiver encerrando a conversa (ex: "Obrigado", "Tchau", "Resolvido"), adicione a tag [ACTION: CLOSE] no final da sua resposta.

Gere uma resposta adequada como Stefan da Era Verde Energia (lembre-se da diretiva de concisão):"""
    
            try:
                logging.info("⏳ Enviando para API do Gemini (modelo: gemini-2.5-flash, MODO STREAMING)...")
                start_time = time.time()
                resp_stream = self.model.generate_content(
                    [prompt_completo],
                    stream=True,
                )
        
                print(f"\n{'='*60}")
                print("💡 RESPOSTA GERADA (V3.16 - STREAMING):")
                print(f"{'='*60}")
                print("[TEXTO] ", end="", flush=True)
        
                resp_parts = []
                finish_reason = None
        
                for ch in resp_stream:
                    # Captura o finish_reason se existir
                    if hasattr(ch, 'candidates') and ch.candidates:
                        # V 3.16 - Check robusto por finish_reason
                        candidate = ch.candidates[0]
                        if hasattr(candidate, 'finish_reason'):
                            finish_reason = candidate.finish_reason # Armazena o enum
        
                    if ch.text:
                        print(ch.text, end="", flush=True)
                        resp_parts.append(ch.text)
                print()
                print(f"{'='*60}")
        
                resposta_final = "".join(resp_parts)
        
                processing_time = time.time() - start_time
        
                # Verificar se foi truncado por MAX_TOKENS
                if finish_reason and finish_reason.name == "MAX_TOKENS":
                    logging.warning(f"[WARN]️ Resposta truncada por limite de tokens (max_output_tokens={self.model._generation_config.get('max_output_tokens', 'N/A')})")
                    logging.info("💡 Sugestão: Aumente max_output_tokens na configuração do modelo")
                    resposta_final += "\n\n[Resposta truncada - considere aumentar o limite de tokens]"
        
                if resposta_final:
                    logging.info(f"[OK] Resposta (streaming) gerada com sucesso! (tempo: {processing_time:.1f}s)")
                    logging.info(f"  Tamanho da resposta: {len(resposta_final)} caracteres")
                    return resposta_final
                else:
                    logging.error("[ERRO] Resposta vazia do Gemini")
                    # Tentar fallback
                    raise Exception("Resposta vazia - tentando fallback")
    
            except Exception as e:
                logging.error(f"[ERRO] Erro ao gerar resposta: {str(e)}")
                logging.error(f"   Tipo do erro: {type(e).__name__}")
    
                # Tentar gerar resposta mais conservadora (sem streaming)
                try:
                    logging.info("🔄 Tentando gerar resposta sem streaming (modo fallback)...")
                    
                    client_name = conversation_data.get("cliente_nome", "Cliente")
                    ultima_msg = conversation_data.get("ultima_msg_cliente", "")
        
                    prompt_simples = f"""Cliente {client_name} precisa de resposta sobre atualização de contrato de energia solar.
Última mensagem: {ultima_msg}
Gere uma resposta breve e profissional do Stefan (Era Verde Energia)."""
            
                    resp_fallback = self.model.generate_content([prompt_simples])
            
                    # Verificar finish_reason no fallback também
                    if resp_fallback.candidates:
                        fb_reason = resp_fallback.candidates[0].finish_reason
                        if fb_reason.name == "MAX_TOKENS":
                            logging.warning("[WARN]️ Fallback também foi truncado por MAX_TOKENS")
            
                    if resp_fallback.text:
                        logging.info("[OK] Resposta gerada no modo fallback")
                        print(f"\n{'='*60}")
                        print("💡 RESPOSTA GERADA (V3.16 - FALLBACK):")
                        print(f"{'='*60}")
                        print(resp_fallback.text)
                        print(f"{'='*60}")
                        return resp_fallback.text
                    else:
                        # Tenta acessar parts diretamente se text estiver vazio
                        if resp_fallback.candidates and resp_fallback.candidates[0].content.parts:
                            text_parts = [p.text for p in resp_fallback.candidates[0].content.parts if p.text]
                            if text_parts:
                                fallback_text = "".join(text_parts)
                                logging.info("[OK] Resposta extraída dos parts (fallback)")
                                return fallback_text
                        
                        raise Exception("Fallback retornou resposta vazia")
    
                except Exception as e2:
                    logging.error(f"[ERRO] Falha no fallback: {str(e2)}")
                
                return f"Erro na análise: {str(e)}"
        
        except Exception as e_outer:
            # Captura erros que podem ocorrer antes do prompt_completo ser definido
            # (embora agora o texto solto tenha sido removido, mantemos por segurança)
            logging.error(f"[ERRO FATAL] Erro na preparação da análise: {e_outer}")
            return f"Erro fatal na preparação: {e_outer}"

    def _format_conversation_history(self, messages: List[Dict[str, Any]]) -> str:
        """Formata histórico de mensagens para o Gemini (Compatível com V3.3)"""
        if not messages:
            return "Histórico não disponível."
        
        historico = []
        for i, msg in enumerate(messages, 1):
            # 'author_type' e 'text'
            sender = "Cliente" if msg.get("author_type") == "cliente" else "Stefan"
            content = msg.get("text", "").strip()
            
            # Não incluir mensagens de sistema no prompt do Gemini
            if msg.get("author_type") == "sistema":
                continue
                
            if content:
                historico.append(f"{i}. {sender}: {content}")
        
        # Otimização V3.4 - Limitar o histórico enviado (ex: últimas 15 mensagens)
        # se for muito longo, pode aumentar a latência
        if len(historico) > 20:
            logging.info(f"Histórico truncado para o Gemini (de {len(historico)} para 20 mensagens)")
            historico = historico[-20:]
        
        return "\n".join(historico) if historico else "Histórico vazio."
