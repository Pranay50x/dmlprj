def test_predict_and_log(client):
    payload = {"text": "I love this product"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["label"] in {"positive", "negative", "neutral"}
    assert isinstance(data["score"], float)

    list_response = client.get("/predictions?limit=1")
    assert list_response.status_code == 200
    items = list_response.json()
    assert items[0]["text"] == payload["text"]
