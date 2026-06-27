# automacao_imoveis_v2

Automacao de imoveis do Leilao Paula Souza (v2).

Acessa o site de leiloes, captura cards de imoveis (Venda Online / Venda Direta
Online) e gera posts 1080x1350 (4:5) prontos para Instagram, com 1 imovel por post.

## Estrutura

- `script.py` - script principal: raspa os cards e gera os posts
- `inspecionar.py` - utilitario de inspecao da pagina (ajuda a descobrir seletores)
- `abrir_chrome_automacao.bat` - atalho pra abrir o Chrome em modo debug
- `template.png` - template base do post 1080x1350
- `logo.png` - logo usado na composicao
- `controle/` - controle de execucao (estado, log, ja gerados)
- `legendas/` - legendas geradas por imovel
- `posts/` - imagens finais prontas pra postar

## Pre-requisitos

- Python 3.10+
- Playwright (`pip install playwright` + `playwright install chromium`)
- Pillow (`pip install pillow`)

## Como rodar

```bash
# da pasta do projeto
python script.py
```

## Configuracao

A URL ja vem filtrada para SP > Bauru > categoria 6 (imovel) > Venda Online /
Venda Direta Online. Ajuste no topo de `script.py` se precisar.