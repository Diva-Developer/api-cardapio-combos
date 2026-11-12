# api-cardapio-combos

API pequena em FastAPI com o cardápio de uma hamburgueria fictícia e um endpoint que sugere um combo pro cliente com base no que ele já pediu.

A sugestão é feita pelo Claude. Se não tiver chave configurada, ou se a chamada falhar, a API cai numa regra simples: o par de itens que mais saiu junto, mais a bebida mais pedida. Fiz assim porque sugestão é um extra e não pode derrubar a rota.

## Endpoints

| Método | Rota | O que faz |
| --- | --- | --- |
| GET | `/cardapio?categoria=bebida` | lista os itens, com filtro opcional |
| POST | `/pedidos` | registra um pedido (`cliente_id`, `itens`) |
| GET | `/clientes/{id}/combo` | sugere um combo com 10% de desconto |

Exemplo de resposta do combo:

```json
{
  "nome": "Combo da casa",
  "itens": ["X-Burger", "Batata frita", "Refrigerante lata"],
  "preco_cheio": 43.4,
  "preco_combo": 39.06,
  "motivo": "Itens que mais saem juntos nos seus pedidos.",
  "origem": "frequencia"
}
```

O campo `origem` diz se a sugestão veio do `claude` ou da regra de `frequencia`.

## Rodando

```
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sua_chave   # opcional
uvicorn app.main:app --reload
```

A documentação interativa fica em http://localhost:8000/docs.

Testes:

```
python -m pytest
```

## Observações

- Os dados ficam em memória, carregados de `dados/`. Reiniciou, perdeu os pedidos novos.
- O modelo às vezes devolve id que não existe no cardápio, então filtro a resposta antes de calcular o preço.
