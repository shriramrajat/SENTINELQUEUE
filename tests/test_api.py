from datetime import datetime, timezone, timedelta

def test_create_job_immediate(client, mock_redis):
    response = client.post("/jobs/", json={
        "task_name": "generate_pdf",
        "payload": {"user_id": 1},
        "priority": "medium"
    })
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "queued"
    assert data["task_name"] == "generate_pdf"
    
    # Verify it was pushed to redis
    mock_redis.lpush.assert_called_once()
    args, kwargs = mock_redis.lpush.call_args
    assert args[0] == "queue:medium"
    assert args[1] == data["id"]

def test_create_job_scheduled(client, mock_redis):
    # Create a time 1 hour in the future
    future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat()
    
    response = client.post("/jobs/", json={
        "task_name": "generate_pdf",
        "execute_at": future_time
    })
    
    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "scheduled"
    
    # Verify it was NOT pushed to redis
    mock_redis.lpush.assert_not_called()

def test_monitor_endpoint(client, mock_redis):
    # Mock redis queue lengths
    mock_redis.llen.side_effect = lambda q: 5 if q == "queue:high" else 0
    
    response = client.get("/monitor/")
    assert response.status_code == 200
    data = response.json()
    
    # Check redis metrics
    assert data["redis_queues"]["high_priority"] == 5
    assert data["redis_queues"]["total_waiting"] == 5
