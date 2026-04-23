def notificar_pedido_criado(pedido_id, usuario_id):
    print("ENVIANDO EMAIL: Pedido " + str(pedido_id) + " criado para usuario " + str(usuario_id))
    print("ENVIANDO SMS: Seu pedido foi recebido!")
    print("ENVIANDO PUSH: Novo pedido recebido pelo sistema")


def notificar_status_pedido(pedido_id, novo_status):
    if novo_status == "aprovado":
        print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " foi aprovado! Preparar envio.")
    if novo_status == "cancelado":
        print("NOTIFICAÇÃO: Pedido " + str(pedido_id) + " cancelado. Devolver estoque.")
