from fastapi.testclient import TestClient


def criar_usuario(client: TestClient, nome: str, email: str):
    return client.post("/usuarios", json={"nome": nome, "email": email})


def criar_sala(client: TestClient, nome: str, capacidade: int, bloco: str):
    return client.post("/salas", json={"nome": nome, "capacidade": capacidade, "bloco": bloco})


def criar_reserva(client: TestClient, usuario_id: int, sala_id: int, data: str, hora_inicio: str, hora_fim: str):
    return client.post(
        "/reservas",
        json={
            "usuario_id": usuario_id,
            "sala_id": sala_id,
            "data": data,
            "hora_inicio": hora_inicio,
            "hora_fim": hora_fim,
        },
    )


def test_criar_usuario_com_email_valido(client: TestClient):
    response = criar_usuario(client, "Ana Souza", "ana@example.com")
    assert response.status_code == 200
    assert response.json()["id"] == 1


def test_impedir_usuario_com_email_duplicado(client: TestClient):
    criar_usuario(client, "Ana Souza", "ana@example.com")
    response = criar_usuario(client, "Ana Maria", "ana@example.com")
    assert response.status_code == 400
    assert "Email já cadastrado" in response.json()["detail"]


def test_criar_sala_com_capacidade_valida(client: TestClient):
    response = criar_sala(client, "Sala 101", 6, "A")
    assert response.status_code == 200
    assert response.json()["capacidade"] == 6


def test_impedir_sala_com_capacidade_zero(client: TestClient):
    response = criar_sala(client, "Sala 102", 0, "A")
    assert response.status_code == 400
    assert "Capacidade deve ser maior que zero" in response.json()["detail"]


def test_criar_reserva_valida(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    response = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "14:00", "15:30")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"


def test_impedir_reserva_em_horario_passado(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    response = criar_reserva(client, usuario["id"], sala["id"], "2000-01-01", "09:00", "10:00")
    assert response.status_code == 400
    assert "Não é possível reservar para data passada" in response.json()["detail"]


def test_impedir_conflito_de_horario_mesma_sala(client: TestClient):
    usuario1 = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    usuario2 = criar_usuario(client, "Bruno Silva", "bruno@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    criar_reserva(client, usuario1["id"], sala["id"], "2099-01-01", "14:00", "15:00")
    response = criar_reserva(client, usuario2["id"], sala["id"], "2099-01-01", "14:30", "15:30")
    assert response.status_code == 400
    assert "Sala já possui reserva em horário conflituoso" in response.json()["detail"]


def test_impedir_conflito_de_horario_mesmo_usuario(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala1 = criar_sala(client, "Sala 101", 6, "A").json()
    sala2 = criar_sala(client, "Sala 102", 6, "A").json()
    criar_reserva(client, usuario["id"], sala1["id"], "2099-01-01", "14:00", "15:00")
    response = criar_reserva(client, usuario["id"], sala2["id"], "2099-01-01", "14:30", "15:30")
    assert response.status_code == 400
    assert "Usuário já possui reserva em horário conflituoso" in response.json()["detail"]


def test_impedir_terceira_reserva_ativa_no_mesmo_dia(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala1 = criar_sala(client, "Sala 101", 6, "A").json()
    sala2 = criar_sala(client, "Sala 102", 6, "A").json()
    sala3 = criar_sala(client, "Sala 103", 6, "A").json()
    criar_reserva(client, usuario["id"], sala1["id"], "2099-01-01", "08:00", "09:00")
    criar_reserva(client, usuario["id"], sala2["id"], "2099-01-01", "10:00", "11:00")
    response = criar_reserva(client, usuario["id"], sala3["id"], "2099-01-01", "12:00", "13:00")
    assert response.status_code == 400
    assert "Usuário já possui 2 reservas ativas para este dia" in response.json()["detail"]


def test_impedir_reserva_com_mais_de_duas_horas(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    response = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "08:00", "11:00")
    assert response.status_code == 400
    assert "Duração máxima de reserva é de 2 horas" in response.json()["detail"]


def test_cancelar_reserva_ativa(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    reserva = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "08:00", "09:00").json()
    response = client.put(f"/reservas/{reserva['id']}/cancelar")
    assert response.status_code == 200
    assert response.json()["status"] == "canceled"


def test_impedir_cancelar_reserva_ja_cancelada(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    reserva = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "08:00", "09:00").json()
    client.put(f"/reservas/{reserva['id']}/cancelar")
    response = client.put(f"/reservas/{reserva['id']}/cancelar")
    assert response.status_code == 400
    assert "Reserva não pode ser cancelada" in response.json()["detail"]


def test_finalizar_reserva_apos_horario_de_termino(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    reserva = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "08:00", "09:00").json()
    response = client.put(f"/reservas/{reserva['id']}/finalizar?hora_atual=09:00")
    assert response.status_code == 200
    assert response.json()["status"] == "finished"


def test_impedir_finalizar_antes_do_fim(client: TestClient):
    usuario = criar_usuario(client, "Ana Souza", "ana@example.com").json()
    sala = criar_sala(client, "Sala 101", 6, "A").json()
    reserva = criar_reserva(client, usuario["id"], sala["id"], "2099-01-01", "08:00", "09:00").json()
    response = client.put(f"/reservas/{reserva['id']}/finalizar?hora_atual=08:30")
    assert response.status_code == 400
    assert "Reserva não pode ser finalizada" in response.json()["detail"]
