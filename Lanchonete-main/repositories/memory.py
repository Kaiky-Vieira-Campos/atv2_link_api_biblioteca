from typing import Dict


class MemoryDB:
    """Repositório em memória para armazenamento dos dados da aplicação.

    Substitui um banco de dados durante o desenvolvimento/testes.
    Os dados são perdidos ao reiniciar a aplicação.
    """

    def __init__(self):
        self.clientes_por_cpf: Dict[str, object] = {}
        self.produtos_por_id: Dict[int, object] = {}
        self.pedidos_por_codigo: Dict[int, object] = {}
        self.usuarios: Dict[int, object] = {}
        self.salas: Dict[int, object] = {}
        self.reservas: Dict[int, object] = {}
        self.next_usuario_id: int = 1
        self.next_sala_id: int = 1
        self.next_reserva_id: int = 1


db = MemoryDB()
