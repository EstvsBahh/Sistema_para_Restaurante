from models.mesa import Mesa
from models.produto import Produto
from models.pedido import Pedido
from models.garcom import Garcom
from models.caixa import Caixa

#É tudo teste professor, nao leva isso em consideracao nao 🙏🏻

print("Sistema para Restaurante - Teste\n")

#Mesa
mesa1 = Mesa(numero=1)
print(f"Mesa {mesa1.numero} está: {mesa1.situacao}")

#Garçom abre pedido na mesa
garcom = Garcom(nome="João")
mesa1.ocupar()
pedido = Pedido(mesa=mesa1, garcom=garcom)
print(f"Garçom {garcom.nome} abriu um pedido na mesa {mesa1.numero}")
print(f"Mesa {mesa1.numero} está agora: {mesa1.situacao}\n")

#Produtos do cardápio
prato = Produto("Feijoada", 35.00)
refrigerante = Produto("Refrigerante", 8.00)

#Cliente pede
pedido.adicionar_item(prato, 2)
pedido.adicionar_item(refrigerante, 2)

print("Itens do pedido:")
for item in pedido.itens:
    print(f" - {item.quantidade}x {item.produto.nome} = R$ {item.calcular_subtotal():.2f}")

print(f"\nValor total do pedido: R$ {pedido.calcular_total():.2f}")

#Caixa registra pagamento e finaliza
caixa = Caixa(nome="Maria")
caixa.registrar_pagamento(pedido)
caixa.fechar_conta(pedido)

print(f"\nEstado final do pedido: {pedido.estado}")
print(f"Mesa {mesa1.numero} está agora: {mesa1.situacao}")
