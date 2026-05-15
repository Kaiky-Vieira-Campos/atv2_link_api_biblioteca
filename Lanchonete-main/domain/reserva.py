from datetime import datetime


class Reserva:
    def __init__(
        self,
        id: int,
        usuario_id: int,
        sala_id: int,
        data: str,
        hora_inicio: str,
        hora_fim: str,
        status: str = "active"
    ):
        self.id = id
        self.usuario_id = usuario_id
        self.sala_id = sala_id
        self.data = data
        self.hora_inicio = hora_inicio
        self.hora_fim = hora_fim
        self.status = status

    def cancelar(self) -> bool:
        if self.status != "active":
            return False
        self.status = "canceled"
        return True

    def finalizar(self, hora_atual: str) -> bool:
        if self.status != "active":
            return False

        hora_atual_dt = datetime.strptime(hora_atual, "%H:%M").time()
        hora_fim_dt = datetime.strptime(self.hora_fim, "%H:%M").time()
        if hora_atual_dt < hora_fim_dt:
            return False

        self.status = "finished"
        return True

    def duracao_em_horas(self) -> float:
        inicio = datetime.strptime(self.hora_inicio, "%H:%M")
        fim = datetime.strptime(self.hora_fim, "%H:%M")
        delta = fim - inicio
        return delta.total_seconds() / 3600

    def conflita_com(self, outra_reserva) -> bool:
        if self.data != outra_reserva.data:
            return False

        inicio_self = datetime.strptime(self.hora_inicio, "%H:%M")
        fim_self = datetime.strptime(self.hora_fim, "%H:%M")
        inicio_outra = datetime.strptime(outra_reserva.hora_inicio, "%H:%M")
        fim_outra = datetime.strptime(outra_reserva.hora_fim, "%H:%M")

        return inicio_self < fim_outra and inicio_outra < fim_self
