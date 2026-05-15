from datetime import datetime, date
from domain.usuario import Usuario
from domain.sala import Sala
from domain.reserva import Reserva
from repositories.memory import db


DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
MAX_RESERVA_HORAS = 2
MAX_RESERVAS_POR_DIA = 2


def _parse_data(data: str) -> date:
    return datetime.strptime(data, DATE_FORMAT).date()


def _parse_hora(hora: str) -> datetime.time:
    return datetime.strptime(hora, TIME_FORMAT).time()


def _validar_data_e_horario(data: str, hora_inicio: str, hora_fim: str):
    data_dt = _parse_data(data)
    hoje = date.today()
    if data_dt < hoje:
        raise ValueError("Não é possível reservar para data passada")

    inicio = _parse_hora(hora_inicio)
    fim = _parse_hora(hora_fim)
    if fim <= inicio:
        raise ValueError("Hora final deve ser maior que hora inicial")

    duracao = (datetime.combine(data_dt, fim) - datetime.combine(data_dt, inicio)).total_seconds() / 3600
    if duracao > MAX_RESERVA_HORAS:
        raise ValueError("Duração máxima de reserva é de 2 horas")

    return data_dt


def criar_usuario(nome: str, email: str):
    if not nome.strip():
        raise ValueError("Nome é obrigatório")

    if not email.strip():
        raise ValueError("Email é obrigatório")

    if any(usuario.email.lower() == email.lower() for usuario in db.usuarios.values()):
        raise ValueError("Email já cadastrado")

    usuario = Usuario(id=db.next_usuario_id, nome=nome, email=email)
    db.usuarios[db.next_usuario_id] = usuario
    db.next_usuario_id += 1
    return usuario


def listar_usuarios():
    return list(db.usuarios.values())


def criar_sala(nome: str, capacidade: int, bloco: str):
    if not nome.strip():
        raise ValueError("Nome da sala é obrigatório")

    if capacidade <= 0:
        raise ValueError("Capacidade deve ser maior que zero")

    if not bloco.strip():
        raise ValueError("Bloco é obrigatório")

    sala = Sala(id=db.next_sala_id, nome=nome, capacidade=capacidade, bloco=bloco)
    db.salas[db.next_sala_id] = sala
    db.next_sala_id += 1
    return sala


def listar_salas():
    return list(db.salas.values())


def criar_reserva(usuario_id: int, sala_id: int, data: str, hora_inicio: str, hora_fim: str):
    if usuario_id not in db.usuarios:
        raise ValueError("Usuário não encontrado")
    if sala_id not in db.salas:
        raise ValueError("Sala não encontrada")

    data_dt = _validar_data_e_horario(data, hora_inicio, hora_fim)

    usuario_reservas_mesma_data = [
        reserva
        for reserva in db.reservas.values()
        if reserva.usuario_id == usuario_id and reserva.data == data and reserva.status == "active"
    ]
    if len(usuario_reservas_mesma_data) >= MAX_RESERVAS_POR_DIA:
        raise ValueError("Usuário já possui 2 reservas ativas para este dia")

    nova_reserva = Reserva(
        id=db.next_reserva_id,
        usuario_id=usuario_id,
        sala_id=sala_id,
        data=data,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
    )

    for reserva in db.reservas.values():
        if reserva.data != data:
            continue
        if reserva.sala_id == sala_id and reserva.conflita_com(nova_reserva):
            raise ValueError("Sala já possui reserva em horário conflituoso")
        if reserva.usuario_id == usuario_id and reserva.conflita_com(nova_reserva):
            raise ValueError("Usuário já possui reserva em horário conflituoso")

    db.reservas[db.next_reserva_id] = nova_reserva
    db.next_reserva_id += 1
    return nova_reserva


def listar_reservas():
    return list(db.reservas.values())


def listar_reservas_usuario(usuario_id: int):
    if usuario_id not in db.usuarios:
        raise ValueError("Usuário não encontrado")
    return [reserva for reserva in db.reservas.values() if reserva.usuario_id == usuario_id]


def buscar_reserva(reserva_id: int):
    reserva = db.reservas.get(reserva_id)
    if not reserva:
        raise ValueError("Reserva não encontrada")
    return reserva


def cancelar_reserva(reserva_id: int):
    reserva = buscar_reserva(reserva_id)
    if not reserva.cancelar():
        raise ValueError("Reserva não pode ser cancelada")
    return reserva


def finalizar_reserva(reserva_id: int, hora_atual: str):
    reserva = buscar_reserva(reserva_id)
    if not reserva.finalizar(hora_atual):
        raise ValueError("Reserva não pode ser finalizada")
    return reserva
