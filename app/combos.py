import json
import os
import re
from collections import Counter
from itertools import combinations

MODELO = os.getenv("MODELO_CLAUDE", "claude-haiku-5-5")


def combo_por_frequencia(pedidos, cardapio):
    """Sem IA: pega o par de itens que mais saiu junto e completa com a bebida mais pedida."""
    pares = Counter()
    for pedido in pedidos:
        for par in combinations(sorted(set(pedido["itens"])), 2):
            pares[par] += 1
    if not pares:
        return []
    itens = list(pares.most_common(1)[0][0])

    por_id = {i["id"]: i for i in cardapio}
    if not any(por_id[i]["categoria"] == "bebida" for i in itens):
        bebidas = Counter(
            i for p in pedidos for i in p["itens"] if por_id[i]["categoria"] == "bebida"
        )
        if bebidas:
            itens.append(bebidas.most_common(1)[0][0])
    return itens


def combo_por_ia(pedidos, cardapio):
    import anthropic

    nomes = {i["id"]: i["nome"] for i in cardapio}
    historico = "\n".join(", ".join(nomes[i] for i in p["itens"]) for p in pedidos)
    pergunta = (
        "Cardapio (id - nome - categoria - preco):\n"
        + "\n".join(f'{i["id"]} - {i["nome"]} - {i["categoria"]} - {i["preco"]}' for i in cardapio)
        + "\n\nUltimos pedidos do cliente:\n"
        + historico
        + "\n\nMonte um combo de 2 a 4 itens que esse cliente provavelmente pediria. "
        'Responda so com JSON: {"itens": [ids], "nome": "nome curto do combo", "motivo": "uma frase"}'
    )
    resposta = anthropic.Anthropic().messages.create(
        model=MODELO,
        max_tokens=200,
        messages=[{"role": "user", "content": pergunta}],
    )
    dados = json.loads(re.search(r"\{.*\}", resposta.content[0].text, re.DOTALL).group(0))
    # o modelo de vez em quando inventa id, entao filtro pelo cardapio
    dados["itens"] = [i for i in dados["itens"] if i in nomes]
    return dados


def sugerir(pedidos, cardapio, desconto=0.10):
    origem = "frequencia"
    nome, motivo = "Combo da casa", "Itens que mais saem juntos nos seus pedidos."
    itens = []

    if os.getenv("ANTHROPIC_API_KEY"):
        try:
            dados = combo_por_ia(pedidos, cardapio)
            itens, nome, motivo, origem = dados["itens"], dados["nome"], dados["motivo"], "claude"
        except Exception:
            itens = []  # se a API falhar a sugestao nao pode cair junto

    if len(itens) < 2:
        itens, origem = combo_por_frequencia(pedidos, cardapio), "frequencia"

    por_id = {i["id"]: i for i in cardapio}
    cheio = sum(por_id[i]["preco"] for i in itens)
    return {
        "nome": nome,
        "itens": [por_id[i]["nome"] for i in itens],
        "preco_cheio": round(cheio, 2),
        "preco_combo": round(cheio * (1 - desconto), 2),
        "motivo": motivo,
        "origem": origem,
    }
