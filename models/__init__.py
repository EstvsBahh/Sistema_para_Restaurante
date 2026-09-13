# Cozinha não vira tabela: ela não guarda dados próprios, apenas consulta
# pedidos com estado="em_preparo"/"pronto" (ver routes/rotas_pedido.py).
from models.mesa import Mesa
from models.categoria import Categoria
from models.produto import Produto
from models.garcom import Garcom
from models.pedido import Pedido
from models.item_pedido import ItemPedido
from models.pagamento import Pagamento
from models.caixa import Caixa
