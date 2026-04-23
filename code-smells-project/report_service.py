import report_repository


def _calcular_desconto(faturamento):
    if faturamento > 10000:
        return faturamento * 0.1
    if faturamento > 5000:
        return faturamento * 0.05
    if faturamento > 1000:
        return faturamento * 0.02
    return 0


def relatorio_vendas():
    dados = report_repository.get_sales_summary()
    faturamento = dados["faturamento_bruto"]
    desconto = _calcular_desconto(faturamento)

    return {
        "total_pedidos": dados["total_pedidos"],
        "faturamento_bruto": round(faturamento, 2),
        "desconto_aplicavel": round(desconto, 2),
        "faturamento_liquido": round(faturamento - desconto, 2),
        "pedidos_pendentes": dados["pedidos_pendentes"],
        "pedidos_aprovados": dados["pedidos_aprovados"],
        "pedidos_cancelados": dados["pedidos_cancelados"],
        "ticket_medio": round(faturamento / dados["total_pedidos"], 2) if dados["total_pedidos"] > 0 else 0,
    }
