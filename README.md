# Gerenciador de Arquivos

Um gerenciador de arquivos simples desenvolvido em Python para organizar diretórios de forma rápida através do terminal.

O programa permite listar arquivos e pastas de um diretório específico e mover arquivos de acordo com sua extensão para outras pastas, facilitando a organização de downloads, documentos, imagens, músicas e outros tipos de arquivos.

## Funcionalidades

* Listagem de arquivos e pastas do diretório configurado
* Exibição do tamanho dos arquivos em formato legível
* Agrupamento de arquivos por extensão
* Movimentação de arquivos por tipo (extensão)
* Criação automática da pasta de destino, se necessário
* Proteção contra sobrescrita de arquivos existentes
* Interface simples via terminal
* Compatível com Windows, Linux e macOS

## Tecnologias Utilizadas

* Python 3
* Módulos padrão:

  * os
  * shutil
  * subprocess
  * sys
  * platform

## Instalação

Clone o repositório:

```bash
git clone https://github.com/GilvanPedro/GerenciadorDeArquivosPython.git
```

Entre na pasta do projeto:

```bash
cd gerenciador-arquivos
```

## Configuração

Antes de executar o programa, altere a variável `CAMINHO_BASE` no início do arquivo:

```python
CAMINHO_BASE = r"D:\Download"
```

Substitua pelo diretório que deseja gerenciar.

Exemplos:

### Windows

```python
CAMINHO_BASE = r"C:\Users\Usuario\Downloads"
```

### Linux

```python
CAMINHO_BASE = "/home/usuario/Downloads"
```

### macOS

```python
CAMINHO_BASE = "/Users/usuario/Downloads"
```

## Como Executar

Execute o script com:

```bash
python gerenciador.py
```

## Menu Principal

Ao iniciar o programa, serão exibidas as seguintes opções:

```text
[1] Listar arquivos
[2] Mover arquivos
[0] Sair
```

### Listar Arquivos

Mostra:

* Todas as pastas do diretório base
* Todos os arquivos agrupados por extensão
* Tamanho de cada arquivo

### Mover Arquivos

Permite mover arquivos de uma determinada extensão.

Exemplo:

```text
Tipo de arquivo: pdf
Destino: Documentos
```

Todos os arquivos `.pdf` encontrados no diretório base serão movidos para a pasta informada.

Caso a pasta não exista, o programa perguntará se deseja criá-la.

## Estrutura do Projeto

```text
gerenciador-arquivos/
│
├── gerenciador.py
└── README.md
```

## Exemplo de Uso

Organizar automaticamente os arquivos da pasta Downloads:

* PDFs → Documentos
* PNGs → Imagens
* MP3 → Músicas
* ZIP → Compactados

Basta executar a opção de movimentação e informar a extensão desejada.

## Tratamento de Erros

O sistema realiza validações para:

* Caminho base inexistente
* Tipo de arquivo não informado
* Destino inválido
* Falhas na movimentação de arquivos
* Tentativas de sobrescrever arquivos existentes

## Licença

Este projeto é de código aberto e pode ser utilizado livremente para fins de estudo, aprendizado e personalização.
