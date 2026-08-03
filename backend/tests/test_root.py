def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "VOLTA AI Chatbot" in data["message"]
    assert "application" in data["data"]
    assert "version" in data["data"]
    assert data["data"]["docs"] == "/docs"


def test_docs_availability(client):
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc_availability(client):
    response = client.get("/redoc")
    assert response.status_code == 200


def test_openapi_schema(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "VOLTA AI Chatbot"
