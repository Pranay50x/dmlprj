def test_stream_etl(client):
    payload_one = {
        "symbol": "BTCUSDT",
        "price": 100.0,
        "source": "manual",
        "observed_at": "2026-05-12T10:00:00Z",
    }
    payload_two = {
        "symbol": "BTCUSDT",
        "price": 110.0,
        "source": "manual",
        "observed_at": "2026-05-12T10:01:00Z",
    }

    response_one = client.post("/stream/ticks", json=payload_one)
    assert response_one.status_code == 200
    response_two = client.post("/stream/ticks", json=payload_two)
    assert response_two.status_code == 200

    list_response = client.get("/stream/ticks?limit=1")
    assert list_response.status_code == 200
    items = list_response.json()
    assert items[0]["symbol"] == payload_two["symbol"]

    status_before = client.get("/etl/stream/status")
    assert status_before.status_code == 200
    before_data = status_before.json()
    assert before_data["total_ticks"] >= 2
    assert before_data["pending_ticks"] >= 2

    etl_response = client.post("/etl/stream/run?max_rows=10")
    assert etl_response.status_code == 200
    assert etl_response.json()["processed"] >= 2

    status_after = client.get("/etl/stream/status")
    assert status_after.status_code == 200
    after_data = status_after.json()
    assert after_data["pending_ticks"] == 0

    features_response = client.get("/stream/features?limit=2")
    assert features_response.status_code == 200
    feat_items = features_response.json()
    assert feat_items[0]["price_delta"] == 10.0
    assert feat_items[0]["percent_change"] == 10.0
    assert feat_items[0]["is_up"] is True
