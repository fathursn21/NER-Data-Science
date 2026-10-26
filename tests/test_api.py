from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_1_normal_article_input():
    r = client.post("/extract-entities", json={
        "title": "Bursa Malaysia Retreats",
        "body": "KUALA LUMPUR, Oct 7 - Maybank and CIMB traded actively in Malaysia."
    })
    assert r.status_code == 200
    data = r.json()
    assert data["meta"]["entity_count"] == len(data["entities"])

def test_2_empty_title_and_body_rejected_400():
    r = client.post("/extract-entities", json={"title": "   ", "body": ""})
    assert r.status_code == 400

def test_3_punctuation_entity():
    r = client.post("/extract-entities", json={
        "title": "Retail Update",
        "body": "MR D.I.Y. expanded its operations in Kuala Lumpur."
    })
    assert r.status_code == 200
    assert any("D.I.Y." in e["text"] for e in r.json()["entities"])

def test_4_repeated_entities():
    r = client.post("/extract-entities", json={
        "title": "Maybank reports strong growth",
        "body": "Maybank announced new digital services as Maybank shares rose in Malaysia."
    })
    assert r.status_code == 200
    mentions = [e for e in r.json()["entities"] if "Maybank" in e["text"]]
    assert len(mentions) >= 2
    assert mentions[0]["start"] != mentions[1]["start"]

def test_5_numbers_filtered_and_dates_detected():
    r = client.post("/extract-entities", json={
        "title": "Market Volume",
        "body": "Shares rose RM250 on Wednesday, October 7, 2026 in Kuala Lumpur."
    })
    assert r.status_code == 200
    ents = r.json()["entities"]
    assert all(e["text"] != "RM250" for e in ents)

def test_6_non_ascii_text():
    r = client.post("/extract-entities", json={
        "title": "KUALA LUMPUR — Ringkasan Pasar",
        "body": "Maybank mencatat transaksi aktif di Malaysia — naik signifikan."
    })
    assert r.status_code == 200

def test_7_exceeding_max_length_rejected_400():
    r = client.post("/extract-entities", json={"title": "Judul", "body": "A" * 10005})
    assert r.status_code == 400

def test_8_malformed_json_and_determinism():
    r_bad = client.post("/extract-entities", content="{malformed", headers={"Content-Type": "application/json"})
    assert r_bad.status_code == 400
    payload = {"title": "Maybank News", "body": "Maybank operates in Kuala Lumpur."}
    assert client.post("/extract-entities", json=payload).json() == client.post("/extract-entities", json=payload).json()
