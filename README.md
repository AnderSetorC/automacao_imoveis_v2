# automacao_imoveis_v2

Automacao de imoveis do Leilao Paula Souza (v2).

Acessa o site de leiloes, captura cards de imoveis (Venda Online / Venda Direta
Online) e gera posts 1080x1350 (4:5) prontos para Instagram, com 1 imovel por post.

## Estrutura

- `script.py` - script principal: raspa os cards e gera os posts
- `executar_automacao.bat` - iniciador por duplo clique (roda `python script.py`)
- `inspecionar.py` - utilitario de inspecao da pagina (ajuda a descobrir seletores)
- `verificar_novos.py` - lista os cards de uma URL e marca quais ainda nao foram postados
- `rodar_url_nova.py` - roda a automacao uma vez com uma URL diferente, sem alterar a fixa
- `template.png` - template base do post 1080x1350
- `logo.png` - logo usado na composicao
- `controle/` - controle de execucao (postados.json: REFs ja geradas)
- `legendas/` - legendas geradas por imovel
- `posts/` - imagens finais prontas pra postar
- `arquivados/facebook/` - lote antigo de abrir o Chrome no Meta Business (fora da automacao de imoveis)

## Pre-requisitos

- Python 3.10+
- Playwright (`pip install playwright` + `playwright install chromium`)
- Pillow (`pip install pillow`)

Ou rode `instalar_dependencias.bat` (duplo clique) para instalar tudo de uma vez.

## Como rodar

Duplo clique em `executar_automacao.bat` (recomendado - ja entra na pasta certa
e mantem a janela aberta com o resumo no final).

Ou pelo terminal, da pasta do projeto:

```bash
python script.py
```

## Paginacao e controle de duplicatas

O script percorre **todas as paginas** que o site mostrar (le os botoes
`data-page`), rolando cada uma ate o fim para carregar os cards com lazy load.

Cada imovel tem uma REF unica (ex.: `IMCX8555540268685SP`). O arquivo
`controle/postados.json` guarda as REFs ja geradas e evita repetir imovel entre
execucoes - mesmo que ele apareca em outra pagina ou em outra URL de filtro.

A REF so entra no controle **depois** que o PNG e a legenda sao salvos com
sucesso. Se a geracao do arquivo falhar, a REF nao e registrada e o imovel pode
ser tentado de novo numa proxima execucao.

## Por que o numero de posts pode ser menor que o de cards

Uma pagina com 24 cards nem sempre gera 24 posts. Ao final da execucao o script
imprime um **resumo** que fecha a conta:

```
RESUMO DA EXECUCAO
Paginas processadas:    2
Cards encontrados:      24
Posts novos gerados:    13
Ja postados (pulados):  9
REF nao reconhecida:    2
Imagem nao carregou:    0
Duplicado na execucao:  0
Falha de leitura:       0
```

Os cards que nao viram post sao os ja postados antes, os sem REF valida, os que
tiveram falha de imagem/leitura, ou repetidos na mesma execucao. Cada card
tambem imprime seu status na hora (`NOVO / capturado`, `JA POSTADO`,
`REF NAO RECONHECIDA`, etc.), entao da pra auditar exatamente o que aconteceu.

## Limpeza de arquivos

Os PNGs em `posts/` e os TXTs em `legendas/` podem ser apagados depois de usar,
sem problema - o controle guarda so a REF. **Nao apague** `controle/postados.json`,
senao a proxima execucao vai regerar todos os imoveis de novo.

## Configuracao

A URL ja vem filtrada para SP > Bauru > categoria 6 (imovel) > Venda Online /
Venda Direta Online. Ajuste no topo de `script.py` se precisar.
