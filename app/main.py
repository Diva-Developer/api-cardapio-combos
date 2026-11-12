import json
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.combos import sugerir

DADOS = Path(__file__).parent.parent / "dados"

app = FastAPI(title="API de cardápio com sugestão de combo")

# tudo em memoria mesmo, a ideia aqui e testar a sugestao e nao o banco
cardapio = json.loads((DADOS / "cardapio.json").read_text(encoding="utf-8"))
pedidos = json.loads((DADOS / "pedidos.json").read_text(encoding="utf-8"))


class Pedido(BaseModel):
    cliente_id: int
    itens: list[int]


@app.get("/cardapio")
def listar_cardapio(categoria: str | None = None):
    if categoria:
        return [i for i in cardapio if i["categoria"] == categoria]
    return cardapio


@app.post("/pedidos", status_code=201)
def criar_pedido(pedido: Pedido):
    ids = {i["id"] for i in cardapio}
    fora = [i for i in pedido.itens if i not in ids]
    if not pedido.itens or fora:
        raise HTTPException(422, f"itens invalidos: {fora}")
    pedidos.append(pedido.model_dump())
    return pedido


@app.get("/clientes/{cliente_id}/combo")
def combo_do_cliente(cliente_id: int):
    historico = [p for p in pedidos if p["cliente_id"] == cliente_id]
    if not historico:
        raise HTTPException(404, "cliente sem pedidos")
    return sugerir(historico[-10:], cardapio)
