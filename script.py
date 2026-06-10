"""
============================================================
  GERENCIADOR DE ARQUIVOS
  Altere o CAMINHO_BASE abaixo para o diretório que deseja
  gerenciar.
============================================================
"""

import os
import shutil
import subprocess
import sys
import platform
import struct
import zipfile

# ──────────────────────────────────────────────
#  CONFIGURAÇÃO — edite apenas esta variável
# ──────────────────────────────────────────────
CAMINHO_BASE = r"D:\Download"   # <── mude aqui
# ──────────────────────────────────────────────


# ════════════════════════════════════════════
#  HELPERS DE TERMINAL
# ════════════════════════════════════════════

def limpar():
    os.system("cls" if platform.system() == "Windows" else "clear")

def cabecalho():
    print("=" * 54)
    print("  GERENCIADOR DE ARQUIVOS")
    print(f"  Base: {CAMINHO_BASE}")
    print("=" * 54)

def pausar():
    input("\n  [ENTER para voltar ao menu] ")

def cor(texto, codigo):
    return f"\033[{codigo}m{texto}\033[0m"

def ok(msg):      print(cor(f"  [OK]  {msg}", "32"))
def erro(msg):    print(cor(f"  [!!]  {msg}", "31"))
def info(msg):    print(cor(f"  [>>]  {msg}", "36"))
def aviso(msg):   print(cor(f"  [!!]  {msg}", "33"))

def _formatar_tamanho(bytes_: int) -> str:
    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unidade}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


# ════════════════════════════════════════════
#  VALIDAÇÕES
# ════════════════════════════════════════════

def verificar_base():
    if not os.path.isdir(CAMINHO_BASE):
        erro(f"Caminho base não encontrado: {CAMINHO_BASE}")
        erro("Edite a variável CAMINHO_BASE no início do script.")
        sys.exit(1)

def resolver_destino(destino_raw: str) -> str:
    destino_raw = destino_raw.strip()
    if os.path.isabs(destino_raw):
        return destino_raw
    return os.path.join(CAMINHO_BASE, destino_raw)


# ════════════════════════════════════════════
#  DETECÇÃO DE CORRUPÇÃO (sem abrir janelas)
# ════════════════════════════════════════════

# Assinaturas mágicas de formatos comuns
_MAGIC = {
    b"\xFF\xD8\xFF":               "jpg/jpeg",
    b"\x89PNG\r\n\x1a\n":         "png",
    b"GIF87a":                     "gif",
    b"GIF89a":                     "gif",
    b"BM":                         "bmp",
    b"II\x2A\x00":                 "tiff",
    b"MM\x00\x2A":                 "tiff",
    b"%PDF":                       "pdf",
    b"PK\x03\x04":                 "zip/docx/xlsx/pptx",
    b"PK\x05\x06":                 "zip (vazio)",
    b"\xD0\xCF\x11\xE0":          "doc/xls/ppt (Office antigo)",
    b"RIFF":                       "avi/wav",
    b"\x1A\x45\xDF\xA3":          "mkv/webm",
    b"\x00\x00\x00\x18ftyp":      "mp4",
    b"\x00\x00\x00\x20ftyp":      "mp4",
    b"OggS":                       "ogg",
    b"fLaC":                       "flac",
    b"ID3":                        "mp3",
    b"\xFF\xFB":                   "mp3",
    b"\xFF\xF3":                   "mp3",
    b"\xFF\xF2":                   "mp3",
    b"MZ":                         "exe/dll",
    b"\x7fELF":                    "elf (linux exec)",
}

def _verificar_magic(caminho: str) -> tuple[bool, str]:
    """
    Lê os primeiros bytes do arquivo e compara com assinaturas conhecidas.
    Retorna (ok, mensagem).
    """
    try:
        with open(caminho, "rb") as f:
            header = f.read(32)
    except Exception as e:
        return False, f"Não foi possível ler o arquivo: {e}"

    if len(header) == 0:
        return False, "Arquivo vazio (0 bytes)"

    for magic, tipo in _MAGIC.items():
        if header[:len(magic)] == magic:
            return True, f"Assinatura válida ({tipo})"

    # Extensão não tem assinatura mapeada — não podemos julgar
    return None, "Formato sem verificação de assinatura"


def _verificar_zip_interno(caminho: str) -> tuple[bool, str]:
    """Para .zip, .docx, .xlsx, .pptx — verifica integridade do ZIP."""
    try:
        with zipfile.ZipFile(caminho, "r") as z:
            resultado = z.testzip()
            if resultado is None:
                return True, "ZIP íntegro"
            else:
                return False, f"Arquivo corrompido dentro do ZIP: {resultado}"
    except zipfile.BadZipFile:
        return False, "Não é um arquivo ZIP válido"
    except Exception as e:
        return False, str(e)


def _verificar_imagem_pillow(caminho: str) -> tuple[bool, str]:
    """Tenta carregar imagem com Pillow (se disponível)."""
    try:
        from PIL import Image
        with Image.open(caminho) as img:
            img.verify()
        return True, "Imagem válida (Pillow)"
    except ImportError:
        return None, "Pillow não instalado — verificação de imagem limitada"
    except Exception as e:
        return False, f"Imagem corrompida: {e}"


def verificar_corrupcao(caminho: str, nome: str) -> tuple[bool | None, str]:
    """
    Análise em camadas:
      1. Arquivo vazio
      2. Assinatura mágica
      3. Verificação específica por tipo (zip, imagem)
    Retorna (True=ok | False=corrompido | None=indeterminado, mensagem).
    """
    ext = os.path.splitext(nome)[1].lower().lstrip(".")

    # Camada 1 — arquivo vazio
    try:
        if os.path.getsize(caminho) == 0:
            return False, "Arquivo vazio (0 bytes)"
    except Exception as e:
        return False, f"Não foi possível acessar: {e}"

    # Camada 2 — assinatura mágica
    magic_ok, magic_msg = _verificar_magic(caminho)
    if magic_ok is False:
        return False, magic_msg

    # Camada 3 — verificação específica por tipo
    if ext in ("zip", "docx", "xlsx", "pptx", "odt", "ods", "odp", "epub", "jar"):
        zip_ok, zip_msg = _verificar_zip_interno(caminho)
        return zip_ok, zip_msg

    if ext in ("jpg", "jpeg", "png", "gif", "bmp", "tiff", "webp"):
        pil_ok, pil_msg = _verificar_imagem_pillow(caminho)
        if pil_ok is not None:
            return pil_ok, pil_msg
        # Pillow não disponível — confia na assinatura mágica
        if magic_ok is True:
            return True, magic_msg
        return None, "Verificação parcial (instale Pillow para análise completa)"

    # Para outros tipos sem verificador específico
    if magic_ok is True:
        return True, magic_msg

    return None, magic_msg  # formato desconhecido


# ════════════════════════════════════════════
#  OPÇÃO 1 — LISTAR ARQUIVOS
# ════════════════════════════════════════════

def listar_arquivos():
    limpar()
    cabecalho()
    print("\n  LISTAR ARQUIVOS\n")

    itens    = os.listdir(CAMINHO_BASE)
    arquivos = [f for f in itens if os.path.isfile(os.path.join(CAMINHO_BASE, f))]
    pastas   = [f for f in itens if os.path.isdir(os.path.join(CAMINHO_BASE, f))]

    if pastas:
        print(f"  Pastas ({len(pastas)}):")
        for p in sorted(pastas):
            print(f"    📁 {p}")
        print()

    if arquivos:
        por_ext: dict[str, list] = {}
        for f in sorted(arquivos):
            ext = os.path.splitext(f)[1].lower() or "(sem extensão)"
            por_ext.setdefault(ext, []).append(f)

        print(f"  Arquivos ({len(arquivos)}):")
        for ext in sorted(por_ext):
            print(f"    [{ext}]")
            for f in por_ext[ext]:
                tam = _formatar_tamanho(os.path.getsize(os.path.join(CAMINHO_BASE, f)))
                print(f"      • {f:<42} {tam:>10}")
    else:
        info("Nenhum arquivo encontrado.")

    pausar()


# ════════════════════════════════════════════
#  OPÇÃO 2 — MOVER POR TIPO
# ════════════════════════════════════════════

def mover_arquivos():
    limpar()
    cabecalho()
    print("\n  MOVER ARQUIVOS POR TIPO\n")

    tipo = input("  Tipo de arquivo (ex: png, pdf, mp3): ").strip().lstrip(".")
    if not tipo:
        erro("Tipo não informado.")
        pausar()
        return

    arquivos = [
        f for f in os.listdir(CAMINHO_BASE)
        if os.path.isfile(os.path.join(CAMINHO_BASE, f))
        and f.lower().endswith(f".{tipo.lower()}")
    ]

    if not arquivos:
        info(f"Nenhum arquivo .{tipo} encontrado.")
        pausar()
        return

    print(f"\n  {len(arquivos)} arquivo(s) .{tipo} encontrado(s):")
    for f in arquivos:
        print(f"    • {f}")

    print()
    destino_raw = input("  Destino (caminho completo ou nome de subpasta): ").strip()
    if not destino_raw:
        erro("Destino não informado.")
        pausar()
        return

    destino = resolver_destino(destino_raw)

    if not os.path.exists(destino):
        criar = input(f"\n  A pasta '{destino}' não existe. Criar? (s/n): ").strip().lower()
        if criar == "s":
            try:
                os.makedirs(destino)
                ok(f"Pasta criada: {destino}")
            except Exception as e:
                erro(f"Não foi possível criar a pasta: {e}")
                pausar()
                return
        else:
            info("Operação cancelada.")
            pausar()
            return

    print()
    movidos = 0
    for nome in arquivos:
        origem = os.path.join(CAMINHO_BASE, nome)
        alvo   = os.path.join(destino, nome)
        if os.path.exists(alvo):
            resp = input(f"  '{nome}' já existe no destino. Substituir? (s/n): ").strip().lower()
            if resp != "s":
                info(f"Pulando: {nome}")
                continue
        try:
            shutil.move(origem, alvo)
            ok(f"Movido: {nome}")
            movidos += 1
        except Exception as e:
            erro(f"Erro ao mover '{nome}': {e}")

    print(f"\n  Total movido: {movidos}/{len(arquivos)} arquivo(s).")
    pausar()


# ════════════════════════════════════════════
#  OPÇÃO 3 — ABRIR ARQUIVO
# ════════════════════════════════════════════

def abrir_arquivo():
    limpar()
    cabecalho()
    print("\n  ABRIR ARQUIVO\n")

    itens = [
        f for f in os.listdir(CAMINHO_BASE)
        if os.path.isfile(os.path.join(CAMINHO_BASE, f))
    ]

    if not itens:
        info("Nenhum arquivo encontrado.")
        pausar()
        return

    print("  Arquivos disponíveis:")
    for i, nome in enumerate(itens, 1):
        print(f"    {i:>3}. {nome}")

    print()
    escolha = input("  Número ou nome do arquivo: ").strip()

    if escolha.isdigit():
        idx = int(escolha) - 1
        if 0 <= idx < len(itens):
            nome_arquivo = itens[idx]
        else:
            erro("Número fora do intervalo.")
            pausar()
            return
    else:
        if escolha in itens:
            nome_arquivo = escolha
        else:
            erro(f"Arquivo '{escolha}' não encontrado.")
            pausar()
            return

    caminho_arquivo = os.path.join(CAMINHO_BASE, nome_arquivo)
    info(f"Abrindo: {nome_arquivo}")
    _abrir_com_programa_padrao(caminho_arquivo, nome_arquivo)
    pausar()


def _abrir_com_programa_padrao(caminho: str, nome: str):
    sistema = platform.system()
    try:
        if sistema == "Windows":
            resultado = subprocess.run(
                ["cmd", "/c", "start", "", caminho],
                capture_output=True, timeout=10
            )
        elif sistema == "Darwin":
            resultado = subprocess.run(["open", caminho], capture_output=True, timeout=10)
        else:
            resultado = subprocess.run(["xdg-open", caminho], capture_output=True, timeout=10)

        if resultado.returncode != 0:
            _tratar_corrupcao_abertura(caminho, nome,
                                       resultado.stderr.decode(errors="replace"))
            return
        ok(f"Arquivo aberto: {nome}")

    except subprocess.TimeoutExpired:
        ok("Arquivo enviado para abertura (timeout normal — programa pode demorar).")
    except FileNotFoundError:
        erro("Nenhum programa encontrado para abrir este tipo de arquivo.")
    except Exception as e:
        _tratar_corrupcao_abertura(caminho, nome, str(e))


def _tratar_corrupcao_abertura(caminho: str, nome: str, detalhe: str):
    print()
    erro(f"Não foi possível abrir '{nome}'.")
    erro(f"Detalhe: {detalhe or 'erro desconhecido'}")
    aviso("O arquivo pode estar corrompido.")
    resp = input("\n  Deseja EXCLUIR este arquivo agora? (s/n): ").strip().lower()
    if resp == "s":
        try:
            os.remove(caminho)
            ok(f"Arquivo excluído: {nome}")
        except Exception as e:
            erro(f"Não foi possível excluir: {e}")
    else:
        info("Arquivo mantido.")


# ════════════════════════════════════════════
#  OPÇÃO 4 — EXCLUIR POR TIPO  (NOVO)
# ════════════════════════════════════════════

def excluir_por_tipo():
    limpar()
    cabecalho()
    print("\n  EXCLUIR ARQUIVOS POR TIPO\n")

    tipo = input("  Tipo de arquivo a excluir (ex: tmp, log, bak): ").strip().lstrip(".")
    if not tipo:
        erro("Tipo não informado.")
        pausar()
        return

    arquivos = [
        f for f in os.listdir(CAMINHO_BASE)
        if os.path.isfile(os.path.join(CAMINHO_BASE, f))
        and f.lower().endswith(f".{tipo.lower()}")
    ]

    if not arquivos:
        info(f"Nenhum arquivo .{tipo} encontrado.")
        pausar()
        return

    print(f"\n  {len(arquivos)} arquivo(s) .{tipo} encontrado(s):")
    for f in arquivos:
        tam = _formatar_tamanho(os.path.getsize(os.path.join(CAMINHO_BASE, f)))
        print(f"    • {f:<42} {tam:>10}")

    # Tamanho total que será liberado
    total_bytes = sum(
        os.path.getsize(os.path.join(CAMINHO_BASE, f)) for f in arquivos
    )
    print(f"\n  Espaço que será liberado: {_formatar_tamanho(total_bytes)}")

    print()
    aviso(f"ATENÇÃO: Esta ação excluirá PERMANENTEMENTE {len(arquivos)} arquivo(s).")
    confirmacao = input(f'\n  Digite  CONFIRMAR  para prosseguir (ou ENTER para cancelar): ').strip()

    if confirmacao != "CONFIRMAR":
        info("Operação cancelada.")
        pausar()
        return

    print()
    excluidos = 0
    for nome in arquivos:
        caminho = os.path.join(CAMINHO_BASE, nome)
        try:
            os.remove(caminho)
            ok(f"Excluído: {nome}")
            excluidos += 1
        except Exception as e:
            erro(f"Erro ao excluir '{nome}': {e}")

    print(f"\n  Total excluído: {excluidos}/{len(arquivos)} arquivo(s).")
    print(f"  Espaço liberado: {_formatar_tamanho(total_bytes)}")
    pausar()


# ════════════════════════════════════════════
#  OPÇÃO 5 — VERIFICAR CORRUPÇÃO EM MASSA  (NOVO)
# ════════════════════════════════════════════

def verificar_todos():
    limpar()
    cabecalho()
    print("\n  VERIFICAR CORRUPÇÃO — TODOS OS ARQUIVOS\n")

    arquivos = [
        f for f in os.listdir(CAMINHO_BASE)
        if os.path.isfile(os.path.join(CAMINHO_BASE, f))
    ]

    if not arquivos:
        info("Nenhum arquivo encontrado.")
        pausar()
        return

    print(f"  Analisando {len(arquivos)} arquivo(s)...\n")

    resultados_corrompidos = []
    resultados_ok          = []
    resultados_indefinidos = []

    for nome in arquivos:
        caminho = os.path.join(CAMINHO_BASE, nome)
        status, msg = verificar_corrupcao(caminho, nome)

        if status is True:
            resultados_ok.append((nome, msg))
            print(cor(f"  [OK] {nome}", "32") + f"  —  {msg}")
        elif status is False:
            resultados_corrompidos.append((nome, msg))
            print(cor(f"  [!!] {nome}", "31") + f"  —  {msg}")
        else:
            resultados_indefinidos.append((nome, msg))
            print(cor(f"  [??] {nome}", "33") + f"  —  {msg}")

    # Resumo
    print("\n" + "─" * 54)
    print(f"  {cor('OK         ', '32')} {len(resultados_ok):>3} arquivo(s)")
    print(f"  {cor('Corrompidos', '31')} {len(resultados_corrompidos):>3} arquivo(s)")
    print(f"  {cor('Indefinidos', '33')} {len(resultados_indefinidos):>3} arquivo(s)  "
          f"(formato sem verificador ou Pillow ausente)")
    print("─" * 54)

    # Se há corrompidos, oferece exclusão
    if resultados_corrompidos:
        print()
        aviso(f"{len(resultados_corrompidos)} arquivo(s) corrompido(s) detectado(s):")
        for nome, msg in resultados_corrompidos:
            print(f"    • {nome}  ({msg})")

        print()
        resp = input("  Deseja EXCLUIR todos os corrompidos agora? (s/n): ").strip().lower()
        if resp == "s":
            print()
            excluidos = 0
            for nome, _ in resultados_corrompidos:
                caminho = os.path.join(CAMINHO_BASE, nome)
                try:
                    os.remove(caminho)
                    ok(f"Excluído: {nome}")
                    excluidos += 1
                except Exception as e:
                    erro(f"Erro ao excluir '{nome}': {e}")
            print(f"\n  Total excluído: {excluidos}/{len(resultados_corrompidos)} arquivo(s).")
        else:
            # Pergunta um a um
            resp2 = input("  Deseja revisar e excluir um a um? (s/n): ").strip().lower()
            if resp2 == "s":
                print()
                for nome, msg in resultados_corrompidos:
                    caminho = os.path.join(CAMINHO_BASE, nome)
                    aviso(f"Corrompido: {nome}  ({msg})")
                    dec = input("    Excluir este arquivo? (s/n): ").strip().lower()
                    if dec == "s":
                        try:
                            os.remove(caminho)
                            ok(f"Excluído: {nome}")
                        except Exception as e:
                            erro(f"Erro: {e}")
                    else:
                        info("Mantido.")

    pausar()


# ════════════════════════════════════════════
#  MENU PRINCIPAL
# ════════════════════════════════════════════

def menu():
    verificar_base()

    opcoes = {
        "1": ("Listar arquivos",                    listar_arquivos),
        "2": ("Mover arquivos por tipo",            mover_arquivos),
        "3": ("Abrir arquivo",                      abrir_arquivo),
        "4": ("Excluir arquivos por tipo",          excluir_por_tipo),
        "5": ("Verificar corrupção em todos",       verificar_todos),
        "0": ("Sair",                               None),
    }

    while True:
        limpar()
        cabecalho()
        print()
        for chave, (descricao, _) in opcoes.items():
            marcador = cor("►", "36") if chave != "0" else " "
            print(f"  {marcador} [{chave}] {descricao}")
        print()

        escolha = input("  Opção: ").strip()

        if escolha == "0":
            limpar()
            print("\n  Até logo!\n")
            break
        elif escolha in opcoes:
            _, funcao = opcoes[escolha]
            funcao()
        else:
            erro("Opção inválida.")
            pausar()


if __name__ == "__main__":
    menu()
