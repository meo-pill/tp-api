def test_prediction_unauthorized():
    r = client.post("/predictions", json={
        "age": 30,
        "income": 3000,
        "credit_amount": 10000,
        "duration": 24
    })
    assert r.status_code == 401

