import pytest
from fastapi.testclient import TestClient

from app.main import app

api = TestClient(app)


@pytest.fixture(autouse=True)
def sem_chave(monkeypatch):
    # garante que os testes usam so a regra de frequencia
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)


def test_filtra_cardapio_por_categoria():
    bebidas = api.get("/cardapio", params={"categoria": "bebida"}).json()
    assert [b["nome"] for b in bebidas] == ["Refrigerante lata", "Suco de cajá", "Milk-shake"]


def test_combo_usa_o_que_o_cliente_mais_pede():
    combo = api.get("/clientes/1/combo").json()
    assert combo["itens"] == ["X-Burger", "Batata frita", "Refrigerante lata"]
    assert combo["preco_cheio"] == 43.4
    assert combo["preco_combo"] == 39.06
    assert combo["origem"] == "frequencia"


def test_cliente_sem_pedido_da_404():
    assert api.get("/clientes/999/combo").status_code == 404


def test_pedido_com_item_que_nao_existe():
    r = api.post("/pedidos", json={"cliente_id": 5, "itens": [1, 99]})
    assert r.status_code == 422


def test_pedido_novo_entra_no_historico():
    api.post("/pedidos", json={"cliente_id": 7, "itens": [2, 4]})
    combo = api.get("/clientes/7/combo").json()
    assert combo["itens"][:2] == ["X-Bacon", "Onion rings"]
