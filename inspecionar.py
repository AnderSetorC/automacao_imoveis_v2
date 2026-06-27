"""
Script de inspeção: abre a URL, lista candidatos a "card de imovel"
e imprime classes / tags / estrutura para eu descobrir o seletor certo.
"""
import json
from playwright.sync_api import sync_playwright

URL = (
    "https://paulasouzaleiloes.com.br/pesquisa"
    "?estado=SP"
    "&cidade%5B%5D=BAURU"
    "&categoria%5B%5D=6"
    "&estado_imovel%5B%5D=Venda+Online"
    "&estado_imovel%5B%5D=Venda+Direta+Online"
)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1400, "height": 1200})
    page.goto(URL)
    page.wait_for_selector("text=REF")
    page.wait_for_timeout(2000)

    # Pega todos os elementos que contêm "REF:" e imprime info
    candidatos = page.evaluate("""() => {
        const all = document.querySelectorAll('*');
        const matches = [];
        for (const el of all) {
            const txt = (el.innerText || '').trim();
            if (!txt.includes('REF:')) continue;
            // só nos interessam elementos "folha-ish" - que tenham uma imagem e texto curto
            const imgs = el.querySelectorAll('img');
            if (imgs.length === 0) continue;
            // tamanho do texto: cards individuais tem texto moderado, nao gigante
            if (txt.length > 1500) continue;
            matches.push({
                tag: el.tagName,
                className: el.className,
                id: el.id,
                textLen: txt.length,
                imgs: imgs.length,
                // primeiros 80 chars do texto
                preview: txt.slice(0, 120).replace(/\\s+/g, ' '),
                // primeiros 3 níveis de filhos
                childTags: Array.from(el.children).slice(0, 8).map(c => c.tagName + (c.className ? '.' + (c.className.toString().split(' ')[0] || '') : ''))
            });
        }
        return matches.slice(0, 20);
    }""")

    print(json.dumps(candidatos, indent=2, ensure_ascii=False))
    browser.close()
