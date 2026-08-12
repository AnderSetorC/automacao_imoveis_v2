"""
Automacao de Imoveis - Leilao Paula Souza (v2)

Acessa o site de leiloes, captura cards de imoveis (Venda Online / Venda Direta
Online) e gera posts 1080x1350 (4:5) prontos para Instagram, com 1 imovel por post.

A moldura azul em volta do card ja vem desenhada no screenshot do site - o
template so recebe o card centralizado. Posts antigos (formato duplo) nao sao
mais gerados.
"""

import os
import json
import re
from datetime import datetime
from playwright.sync_api import sync_playwright
from PIL import Image


# URL filtrada: transacao=Venda, SP > Bauru, categoria 6 (imovel),
# tipo_imovel=caixa, financiamento=nao_aceita_financiamento,
# estados: Leilao / Venda Online / Venda Direta Online / Licitacao Aberta.
# Resultado atual: 2 paginas (~24 imoveis).
URL = (
    "https://paulasouzaleiloes.com.br/pesquisa"
    "?transacao=Venda"
    "&estado=SP"
    "&tipo_imovel=caixa"
    "&financiamento=nao_aceita_financiamento"
    "&cidade%5B%5D=BAURU"
    "&categoria%5B%5D=6"
    "&estado_imovel%5B%5D=Leil%C3%A3o"
    "&estado_imovel%5B%5D=Venda+Online"
    "&estado_imovel%5B%5D=Venda+Direta+Online"
    "&estado_imovel%5B%5D=Licita%C3%A7%C3%A3o+Aberta"
)

# Pagina do paginador: SPA com botoes data-page="0", data-page="1", ...
NAV_SELECTOR = "nav.results-pagination"
PAGE_BUTTON_SELECTOR = "nav.results-pagination button[data-page]"

# Diretorios do projeto (caminhos relativos ao script - rodar da pasta do projeto).
PASTA_POSTS = "posts"
PASTA_LEGENDAS = "legendas"
PASTA_CONTROLE = "controle"
ARQUIVO_TEMPLATE = "template.png"
ARQUIVO_CONTROLE = f"{PASTA_CONTROLE}/postados.json"

# Area onde o card do imovel entra no template (1080x1350).
# Medido no exemplo: card ocupa x=240..840 (largura 600) e y=240..1110 (altura 870).
AREA_CARD = (240, 240, 840, 1110)
AREA_CARD_W = AREA_CARD[2] - AREA_CARD[0]   # 600
AREA_CARD_H = AREA_CARD[3] - AREA_CARD[1]   # 870

# Regex validando REF conhecida (ex.: IMCX8555540268685SP).
# Se o card nao casar, e descartado - evita gravar REF quebrada em postados.json.
REGEX_REF = re.compile(r"IMCX\d{10,20}SP")

# Seletor do card: classe especifica do site (cada card individual).
# O site usa Bootstrap + classes proprias; cada card tem a classe
# "feat_property search-feat-card" e aparece com 1 imagem e ~130 chars de texto.
# Confirmado por inspecao do HTML (inspecionar.py).
SELECTOR_CARD = "div.feat_property.search-feat-card"


def inicializar_diretorios():
    """Garante que as pastas e o arquivo de controle existem."""
    os.makedirs(PASTA_POSTS, exist_ok=True)
    os.makedirs(PASTA_LEGENDAS, exist_ok=True)
    os.makedirs(PASTA_CONTROLE, exist_ok=True)

    if not os.path.exists(ARQUIVO_CONTROLE):
        with open(ARQUIVO_CONTROLE, "w", encoding="utf-8") as f:
            json.dump([], f)


def carregar_postados():
    with open(ARQUIVO_CONTROLE, "r", encoding="utf-8") as f:
        return json.load(f)


def salvar_postado(postados, ref):
    """Adiciona a REF ao arquivo de controle (persistente entre execucoes)."""
    postados.append(ref)
    with open(ARQUIVO_CONTROLE, "w", encoding="utf-8") as f:
        json.dump(postados, f)


def gerar_legenda():
    """Legenda padrao (mesmo texto do projeto antigo)."""
    return """
Voce esta em Bauru e sonha em comprar um imovel com desconto?
Com a Imobiliaria Paula Souza Bauru, voce participa de leiloes com todo o suporte necessario - e sem complicacoes!

Somos credenciados pela Caixa e cuidamos de tudo:
Avaliacao e analise do imovel
Apoio durante o processo de compra
Assessoria juridica completa
Registro do imovel sem dor de cabeca

E o melhor: a Caixa arca com os custos da corretagem!

Acesse os leiloes e indique a Imobiliaria Paula Souza como sua corretora!
Fale com a gente: (14) 98167-3727 | (14) 99637-1417

CRECI 35952J
https://paulasouzaleiloes.com.br/
""".strip()


def extrair_ref(texto):
    """Extrai e valida a REF do texto do card. Retorna REF ou None."""
    match = REGEX_REF.search(texto)
    return match.group(0) if match else None


def rolar_ate_final(page):
    """Rola a pagina ate todos os cards carregarem (lazy load)."""
    print("Rolando ate o final da pagina...")
    ultimo_total = 0
    sem_progresso = 0

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        # Espera semantica: novo conteudo carregou.
        try:
            page.wait_for_load_state("networkidle", timeout=5000)
        except Exception:
            page.wait_for_timeout(1500)

        cards = page.locator(SELECTOR_CARD)
        total = cards.count()
        print(f"  Imoveis carregados: {total}")

        if total == ultimo_total:
            sem_progresso += 1
            if sem_progresso >= 2:   # duas tentativas sem crescer = fim
                break
        else:
            sem_progresso = 0
            ultimo_total = total

    print(f"Total final de imoveis na pagina: {ultimo_total}")


def descobrir_total_paginas(page):
    """Le os botoes do paginador e devolve a quantidade de paginas.
    Se nao houver paginador (uma pagina so), devolve 1.
    """
    try:
        if page.locator(NAV_SELECTOR).count() == 0:
            return 1
        # Espera os botoes de pagina renderizarem (SPA monta sob demanda).
        page.wait_for_selector(PAGE_BUTTON_SELECTOR, timeout=5000)
    except Exception:
        return 1

    total = page.locator(PAGE_BUTTON_SELECTOR).count()
    return max(1, total)


def ir_para_pagina(page, indice):
    """Clica no botao data-page=N e espera os cards da nova pagina carregarem.

    O site faz a troca via JS (SPA), entao precisamos esperar:
      - o botao da pagina alvo ganhar a classe 'is-active'
      - os cards antigos sumirem / novos aparecerem
    """
    seletor_botao = f'{NAV_SELECTOR} button[data-page="{indice}"]'
    page.locator(seletor_botao).click()

    # Espera ate que o botao dessa pagina esteja ativo.
    page.wait_for_function(
        """(sel) => {
            const btn = document.querySelector(sel);
            return btn && btn.classList.contains('is-active');
        }""",
        arg=f'nav.results-pagination button[data-page="{indice}"]',
        timeout=10000,
    )

    # Espera os cards individuais da nova pagina estarem no DOM.
    page.wait_for_selector(SELECTOR_CARD, timeout=10000)

    # Descanso curto pra lazy load de imagens internas dos cards.
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except Exception:
        page.wait_for_timeout(1500)


def composite_card(template, card_img):
    """Cola o card do imovel na area central do template, preservando a moldura
    azul que ja vem no screenshot do site. Card e redimensionado para caber
    em AREA_CARD mantendo proporcao.
    """
    canvas = template.copy()

    cw, ch = card_img.size
    escala = min(AREA_CARD_W / cw, AREA_CARD_H / ch)
    novo_w = int(cw * escala)
    novo_h = int(ch * escala)
    card_resized = card_img.resize((novo_w, novo_h), Image.LANCZOS)

    # Centraliza dentro da area disponivel.
    off_x = AREA_CARD[0] + (AREA_CARD_W - novo_w) // 2
    off_y = AREA_CARD[1] + (AREA_CARD_H - novo_h) // 2

    canvas.paste(card_resized, (off_x, off_y))
    return canvas


def capturar_card(page, card):
    """Faz scroll ate o card, espera a imagem carregar e devolve a imagem PIL.
    Retorna None se a imagem nao estiver pronta.
    """
    card.scroll_into_view_if_needed()

    # Espera a imagem do card terminar de carregar.
    img_locator = card.locator("img").first
    try:
        img_locator.wait_for(state="visible", timeout=5000)
        # naturalWidth > 0 indica imagem realmente carregada.
        page.wait_for_function(
            """(img) => img.complete && img.naturalWidth > 0""",
            arg=img_locator.element_handle(),
            timeout=5000,
        )
    except Exception:
        return None

    nome_temp = f"_temp_card.png"
    card.screenshot(path=nome_temp)
    try:
        with Image.open(nome_temp) as img:
            return img.copy()
    finally:
        if os.path.exists(nome_temp):
            try:
                os.remove(nome_temp)
            except OSError:
                pass


def executar():
    inicializar_diretorios()
    postados = carregar_postados()
    template = Image.open(ARQUIVO_TEMPLATE).convert("RGB")
    legenda = gerar_legenda()

    capturados = []   # (ref, PIL.Image)
    erros_total = 0

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.set_viewport_size({"width": 1400, "height": 1200})

        print(f"Acessando: {URL}")
        page.goto(URL)
        # Antes: "text=REF" casava com o <option> do select de ordenacao
        # ("Referencia crescente"), que existe desde o load mas esta dentro de
        # um <select> fechado => Playwright considera "nao visivel" e estoura
        # timeout de 30s. Agora esperamos diretamente o card individual que
        # contem o texto "REF:" no corpo.
        page.wait_for_selector(f'{SELECTOR_CARD}:has-text("REF:")', timeout=30000)
        page.wait_for_selector(SELECTOR_CARD)   # garante que os cards individuais carregaram

        # Descobre quantas paginas existem. Se o paginador nao aparecer
        # (filtro com poucos imoveis), tudo cai em "uma pagina".
        total_paginas = descobrir_total_paginas(page)
        print(f"Paginas encontradas: {total_paginas}\n")

        for num_pagina in range(total_paginas):
            if num_pagina > 0:
                ir_para_pagina(page, num_pagina)

            rolar_ate_final(page)

            cards = page.locator(SELECTOR_CARD)
            total = cards.count()
            print(f"\n--- Pagina {num_pagina + 1}/{total_paginas}: {total} cards ---")

            erros_pagina = 0
            for i in range(total):
                card = cards.nth(i)
                try:
                    texto = card.inner_text()
                except Exception as e:
                    print(f"  [p{num_pagina+1} {i+1}/{total}] Falha ao ler texto: {e}")
                    erros_pagina += 1
                    continue

                ref = extrair_ref(texto)
                if ref is None:
                    print(f"  [p{num_pagina+1} {i+1}/{total}] REF nao reconhecida, ignorando")
                    continue

                if ref in postados:
                    continue   # ja processada, silencioso

                img = capturar_card(page, card)
                if img is None:
                    print(f"  [p{num_pagina+1} {i+1}/{total}] Imagem nao carregou para {ref}")
                    erros_pagina += 1
                    continue

                capturados.append((ref, img))
                salvar_postado(postados, ref)
                print(f"  [p{num_pagina+1} {i+1}/{total}] Capturado: {ref}")

            erros_total += erros_pagina

        browser.close()

    # Gera 1 PNG por card + 1 TXT de legenda, mesmo timestamp.
    if not capturados:
        print("\nNenhum imovel novo encontrado.")
        return

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    print(f"\nGerando {len(capturados)} posts com timestamp {timestamp}...\n")

    for contador, (ref, img) in enumerate(capturados, start=1):
        nome = f"{timestamp}_post_{contador}.png"
        caminho_post = f"{PASTA_POSTS}/{nome}"
        caminho_legenda = f"{PASTA_LEGENDAS}/{nome}.txt"

        composite_card(template, img).save(caminho_post, optimize=True)

        with open(caminho_legenda, "w", encoding="utf-8") as f:
            f.write(legenda)

        print(f"  Post gerado: {nome} (REF {ref})")

    print(f"\nFinalizado. {len(capturados)} posts, {erros_total} erros.")


if __name__ == "__main__":
    executar()
