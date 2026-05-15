from fastapi import APIRouter, HTTPException
from schemas.usuario import UsuarioCreate, UsuarioOut
from services.reserva_service import criar_usuario, listar_usuarios

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.post("", response_model=UsuarioOut)
def criar_usuario_route(data: UsuarioCreate):
    try:
        usuario = criar_usuario(data.nome, data.email)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    return UsuarioOut(id=usuario.id, nome=usuario.nome, email=usuario.email)


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios_route():
    usuarios = listar_usuarios()
    return [UsuarioOut(id=u.id, nome=u.nome, email=u.email) for u in usuarios]
