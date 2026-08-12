"""
Wrapper one-shot: roda a mesma logica de script.py mas com a URL nova
(fornecida pelo usuario). NAO altera a URL fixa em script.py.
"""
import script


URL_NOVA = (
    "https://paulasouzaleiloes.com.br/pesquisa"
    "?transacao=Venda"
    "&estado=SP"
    "&tipo_imovel=caixa"
    "&cidade%5B%5D=BAURU"
    "&categoria%5B%5D=16"
    "&categoria%5B%5D=60"
    "&categoria%5B%5D=132"
    "&categoria%5B%5D=20"
    "&categoria%5B%5D=130"
    "&categoria%5B%5D=37"
    "&categoria%5B%5D=32"
    "&estado_imovel%5B%5D=Leil%C3%A3o"
    "&estado_imovel%5B%5D=Venda+Online"
    "&estado_imovel%5B%5D=Venda+Direta+Online"
    "&estado_imovel%5B%5D=Licita%C3%A7%C3%A3o+Aberta"
)


# Sobrescreve a URL no modulo ja importado antes de executar().
script.URL = URL_NOVA
script.executar()