from fastapi import APIRouter, HTTPException
from schemas.sala import SalaCreate, SalaOut
from services.reserva_service import criar_sala, listar_salas

router = APIRouter(prefix="/salas", tags=["Salas"])


@router.post("", response_model=SalaOut)
def criar_sala_route(data: SalaCreate):
    try:
        sala = criar_sala(data.nome, data.capacidade, data.bloco)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return SalaOut(id=sala.id, nome=sala.nome, capacidade=sala.capacidade, bloco=sala.bloco)


@router.get("", response_model=list[SalaOut])
def listar_salas_route():
    salas = listar_salas()
    return [SalaOut(id=s.id, nome=s.nome, capacidade=s.capacidade, bloco=s.bloco) for s in salas]
