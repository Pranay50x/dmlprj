def test_predict_and_log(client):
    payload = {"text": "I love this product!!!"}
    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["label"] in {"positive", "negative", "neutral"}
    assert isinstance(data["score"], float)

    list_response = client.get("/predictions?limit=1")
    assert list_response.status_code == 200
    items = list_response.json()
    assert items[0]["text"] == payload["text"]

    status_before = client.get("/etl/features/status")
    assert status_before.status_code == 200
    before_data = status_before.json()
    assert before_data["total_predictions"] >= 1
    assert before_data["pending_predictions"] >= 1

    etl_response = client.post("/etl/features/run?max_rows=10")
    assert etl_response.status_code == 200
    assert etl_response.json()["processed"] >= 1

    status_after = client.get("/etl/features/status")
    assert status_after.status_code == 200
    after_data = status_after.json()
    assert after_data["pending_predictions"] == 0

    features_response = client.get("/features?limit=1")
    assert features_response.status_code == 200
    feat_items = features_response.json()
    assert feat_items[0]["text_length"] == len(payload["text"])
    assert feat_items[0]["exclamation_count"] == payload["text"].count("!")
