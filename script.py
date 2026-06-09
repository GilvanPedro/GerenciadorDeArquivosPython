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

# ──────────────────────────────────────────────
#  CONFIGURAÇÃO — edite apenas esta variável
# ──────────────────────────────────────────────
CAMINHO_BASE = r"D:\Download"   # <── mude aqui
# ──────────────────────────────────────────────


# ── helpers de terminal ────────────────────────

def limpar():
    os.system("cls" if platform.system() == "Windows" else "clear")

def cabecalho():
    print("=" * 52)
    print("  GERENCIADOR DE ARQUIVOS")
    print(f"  Base: {CAMINHO_BASE}")
    print("=" * 52)

def pausar():
    input("\n  [ENTER para voltar ao menu] ")

def cor(texto, codigo):
    """Retorna texto colorido (ANSI). Funciona no terminal padrão."""
    return f"\033[{codigo}m{texto}\033[0m"

def ok(msg):   print(cor(f"  [OK]  {msg}", "32"))
def erro(msg): print(cor(f"  [!!]  {msg}", "31"))
def info(msg): print(cor(f"  [>>]  {msg}", "36"))


# ── validações ────────────────────────────────

def verificar_base():
    """Garante que o CAMINHO_BASE existe antes de qualquer operação."""
    if not os.path.isdir(CAMINHO_BASE):
        erro(f"Caminho base não encontrado: {CAMINHO_BASE}")
        erro("Edite a variável CAMINHO_BASE no início do script.")
        sys.exit(1)

def resolver_destino(destino_raw: str) -> str | None:
    """
    Aceita caminho absoluto ou só o nome de uma pasta dentro do CAMINHO_BASE.
    Retorna o caminho absoluto resolvido, ou None se inválido.
    """
    destino_raw = destino_raw.strip()

    # Caminho absoluto informado diretamente
    if os.path.isabs(destino_raw):
        return destino_raw

    # Nome de subpasta dentro do CAMINHO_BASE
    candidato = os.path.join(CAMINHO_BASE, destino_raw)
    return candidato


# ── funcionalidade 1: mover por tipo ─────────

def mover_arquivos():
    limpar()
    cabecalho()
    print("\n  MOVER ARQUIVOS POR TIPO\n")

    # Pergunta o tipo
    tipo = input("  Tipo de arquivo (ex: png, pdf, mp3): ").strip().lstrip(".")
    if not tipo:
        erro("Tipo não informado.")
        pausar()
        return

    # Lista arquivos do tipo no CAMINHO_BASE (não recursivo, só raiz)
    arquivos = [
        f for f in os.listdir(CAMINHO_BASE)
        if os.path.isfile(os.path.join(CAMINHO_BASE, f))
        and f.lower().endswith(f".{tipo.lower()}")
    ]

    if not arquivos:
        info(f"Nenhum arquivo .{tipo} encontrado em: {CAMINHO_BASE}")
        pausar()
        return

    print(f"\n  {len(arquivos)} arquivo(s) .{tipo} encontrado(s):")
    for f in arquivos:
        print(f"    • {f}")

    # Pergunta o destino
    print()
    destino_raw = input("  Destino (caminho completo ou nome de subpasta): ").strip()
    if not destino_raw:
        erro("Destino não informado.")
        pausar()
        return

    destino = resolver_destino(destino_raw)

    # Cria a pasta de destino se não existir
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

    # Move os arquivos
    print()
    movidos = 0
    for nome in arquivos:
        origem = os.path.join(CAMINHO_BASE, nome)
        alvo   = os.path.join(destino, nome)

        # Evita sobrescrever sem avisar
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

# ── funcionalidade 2: listar arquivos ────────

def listar_arquivos():
    limpar()
    cabecalho()
    print("\n  LISTAR ARQUIVOS\n")

    itens = os.listdir(CAMINHO_BASE)
    arquivos = [f for f in itens if os.path.isfile(os.path.join(CAMINHO_BASE, f))]
    pastas   = [f for f in itens if os.path.isdir(os.path.join(CAMINHO_BASE, f))]

    if pastas:
        print(f"  Pastas ({len(pastas)}):")
        for p in sorted(pastas):
            print(f"    📁 {p}")
        print()

    if arquivos:
        print(f"  Arquivos ({len(arquivos)}):")
        # Agrupa por extensão para facilitar leitura
        por_ext: dict[str, list] = {}
        for f in sorted(arquivos):
            ext = os.path.splitext(f)[1].lower() or "(sem extensão)"
            por_ext.setdefault(ext, []).append(f)

        for ext in sorted(por_ext):
            print(f"    [{ext}]")
            for f in por_ext[ext]:
                tamanho = os.path.getsize(os.path.join(CAMINHO_BASE, f))
                tamanho_fmt = _formatar_tamanho(tamanho)
                print(f"      • {f:<40} {tamanho_fmt:>10}")
    else:
        info("Nenhum arquivo no caminho base.")

    pausar()

def _formatar_tamanho(bytes_: int) -> str:
    for unidade in ["B", "KB", "MB", "GB"]:
        if bytes_ < 1024:
            return f"{bytes_:.1f} {unidade}"
        bytes_ /= 1024
    return f"{bytes_:.1f} TB"


# ── menu principal ────────────────────────────

def menu():
    verificar_base()

    opcoes = {
        "1": ("Listar arquivos",              listar_arquivos),
        "2": ("Mover arquivos",               mover_arquivos),
        "0": ("Sair",                         None),
    }

    while True:
        limpar()
        cabecalho()
        print()
        for chave, (descricao, _) in opcoes.items():
            print(f"  [{chave}] {descricao}")
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
