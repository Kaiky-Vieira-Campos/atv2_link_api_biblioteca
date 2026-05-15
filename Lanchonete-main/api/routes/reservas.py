from fastapi import APIRouter, HTTPException
from schemas.reserva import ReservaCreate, ReservaOut
from services.reserva_service import (
    criar_reserva,
    listar_reservas,
    listar_reservas_usuario,
    buscar_reserva,
    cancelar_reserva,
    finalizar_reserva,
)

router = APIRouter(prefix="/reservas", tags=["Reservas"])


@router.post("", response_model=ReservaOut)
def criar_reserva_route(data: ReservaCreate):
    try:
        reserva = criar_reserva(data.usuario_id, data.sala_id, data.data, data.hora_inicio, data.hora_fim)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReservaOut(
        id=reserva.id,
        usuario_id=reserva.usuario_id,
        sala_id=reserva.sala_id,
        data=reserva.data,
        hora_inicio=reserva.hora_inicio,
        hora_fim=reserva.hora_fim,
        status=reserva.status,
    )


@router.get("", response_model=list[ReservaOut])
def listar_reservas_route():
    return [ReservaOut(**vars(r)) for r in listar_reservas()]


@router.get("/usuario/{usuario_id}", response_model=list[ReservaOut])
def listar_reservas_usuario_route(usuario_id: int):
    try:
        reservas = listar_reservas_usuario(usuario_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return [ReservaOut(**vars(r)) for r in reservas]


@router.get("/{reserva_id}", response_model=ReservaOut)
def buscar_reserva_route(reserva_id: int):
    try:
        reserva = buscar_reserva(reserva_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    return ReservaOut(**vars(reserva))


@router.put("/{reserva_id}/cancelar", response_model=ReservaOut)
def cancelar_reserva_route(reserva_id: int):
    try:
        reserva = cancelar_reserva(reserva_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReservaOut(**vars(reserva))


@router.put("/{reserva_id}/finalizar", response_model=ReservaOut)
def finalizar_reserva_route(reserva_id: int, hora_atual: str):
    try:
        reserva = finalizar_reserva(reserva_id, hora_atual)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return ReservaOut(**vars(reserva))
