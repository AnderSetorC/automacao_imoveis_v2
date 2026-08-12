"""
Script one-shot: acessa a URL nova, lista os cards, imprime a REF e marca
quais ainda nao estao em controle/postados.json.
"""
import json
import re
from playwright.sync_api import sync_playwright

URL = (
    "https://paulasouzaleiloes.com.br/pesquisa"
    "?transacao=Venda"
    "&estado=SP"
    "&pagina=1"
    "&tipo_imovel=caixa"
    "&cidade%5B%5D=BAURU"
    "&categoria%5B%5D=1"
    "&estado_imovel%5B%5D=Leil%C3%A3o"
    "&estado_imovel%5B%5D=Venda+Online"
    "&estado_imovel%5B%5D=Venda+Direta+Online"
    "&estado_imovel%5B%5D=Licita%C3%A7%C3%A3o+Aberta"
)
SELECTOR_CARD = "div.feat_property.search-feat-card"
REGEX_REF = re.compile(r"IMCX\d{10,20}SP")

with open("controle/postados.json", "r", encoding="utf-8") as f:
    postados = set(json.load(f))

print(f"Total de REFs ja postadas: {len(postados)}\n")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1200})
    page.goto(URL)
    page.wait_for_selector(f'{SELECTOR_CARD}:has-text("REF:")', timeout=30000)

    cards = page.locator(SELECTOR_CARD)
    total = cards.count()
    print(f"Cards na pagina: {total}\n")

    novos = []
    invalidos = []
    ja_postados = []

    for i in range(total):
        try:
            texto = cards.nth(i).inner_text()
        except Exception as e:
            invalidos.append((i + 1, f"falha leitura: {e}"))
            continue

        match = REGEX_REF.search(texto)
        if not match:
            invalidos.append((i + 1, texto[:60].replace("\n", " ")))
            continue

        ref = match.group(0)
        status = "JA POSTADO" if ref in postados else "*** NOVO ***"
        if ref in postados:
            ja_postados.append(ref)
        else:
            novos.append(ref)

        print(f"  card {i + 1:>2}/{total}  {ref}  {status}")

    print()
    print("=" * 60)
    print(f"Total capturados:    {total}")
    print(f"Ja postados:         {len(ja_postados)}")
    print(f"REF nao reconhecida: {len(invalidos)}")
    print(f"** NOVOS:           {len(novos)} **")
    for ref in novos:
        print(f"    {ref}")
    if invalidos:
        print("\nCards sem REF valida:")
        for i, snippet in invalidos:
            print(f"    card {i}: {snippet}")

    browser.close()