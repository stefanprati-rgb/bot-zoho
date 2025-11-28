import os
import re
import csv
from datetime import datetime
import logging

def _clean_text_for_csv(s: str) -> str:
    if not s:
        return ""
    # normaliza espaços e quebras (Excel lida melhor)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    # comprime espaços excessivos
    s = re.sub(r"[ \t]+", " ", s)
    # tira espacinhos nas bordas de cada linha
    s = "\n".join(line.strip() for line in s.split("\n"))
    return s.strip()

def export_conversation_to_csv(dados: dict, base_dir: str = "backups", logger=None) -> str:
    """
    Exporta a conversa completa para CSV (UTF-8 BOM, abre bonito no Excel).
    Colunas: data_hora, autor_tipo, autor_nome, mensagem.
    Retorna o caminho do arquivo gerado.
    """
    os.makedirs(base_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    # deixa o nome do cliente no arquivo (sanitizado)
    cliente = dados.get("cliente_nome") or "sem_nome"
    cliente_sanit = re.sub(r"[^A-Za-z0-9_\- ]+", "_", cliente)[:60]  # evita path muito grande
    csv_path = os.path.join(base_dir, f"conversa_{cliente_sanit}_{ts}.csv")

    rows = []
    for m in dados.get("mensagens", []):
        rows.append({
            "data_hora": (m.get("time") or "").strip(),
            "autor_tipo": (m.get("author_type") or "").strip(),
            "autor_nome": (m.get("author_name") or "").strip(),
            "mensagem": _clean_text_for_csv(m.get("text") or ""),
        })

    # cabeçalho fixo
    fieldnames = ["data_hora", "autor_tipo", "autor_nome", "mensagem"]

    # UTF-8 BOM para o Excel reconhecer automaticamente
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, quoting=csv.QUOTE_MINIMAL)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    if logger:
        logger.info(f"📤 CSV exportado: {csv_path} (linhas: {len(rows)})")
    return csv_path

def export_conversation_to_txt(dados: dict, base_dir: str = "backups", logger=None) -> str:
    """
    (Opcional) Exporta transcript simples em TXT (humano-legível).
    """
    os.makedirs(base_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    cliente = dados.get("cliente_nome") or "sem_nome"
    cliente_sanit = re.sub(r"[^A-Za-z0-9_\- ]+", "_", cliente)[:60]
    txt_path = os.path.join(base_dir, f"conversa_{cliente_sanit}_{ts}.txt")

    lines = []
    header = f"Cliente: {dados.get('cliente_nome','')}\nÚltima do cliente: {dados.get('ultima_msg_cliente','')}\nÚltima do agente: {dados.get('ultima_msg_agente','')}\n"
    lines.append(header)
    lines.append("-" * 60)
    for m in dados.get("mensagens", []):
        ts_m = m.get("time") or ""
        who  = m.get("author_name") or m.get("author_type") or "?"
        txt  = _clean_text_for_csv(m.get("text") or "")
        lines.append(f"[{ts_m}] {who}: {txt}")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    if logger:
        logger.info(f"📄 TXT exportado: {txt_path} (linhas: {len(dados.get('mensagens',[]))})")
    return txt_path
