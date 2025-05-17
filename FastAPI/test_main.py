import requests
import asyncio
import websockets

BASE_URL = "http://127.0.0.1:8000"

# Define synchronous endpoint tests
tests = [
    {"name": "Root", "method": "get", "url": "/", "expected": 200},
    {"name": "Greet User", "method": "get", "url": "/hello/TestUser", "expected": 200},
    {"name": "Add Query", "method": "get", "url": "/add", "params": {"a": 5, "b": 7}, "expected": 200},
    {"name": "Sum Path", "method": "get", "url": "/sum/3/4", "expected": 200},
    {"name": "Create Item", "method": "post", "url": "/items/", "json": {"name": "Item1", "description": "A test item", "price": 12.5}, "expected": 200},
    {"name": "Get User", "method": "get", "url": "/user", "expected": 200},
    {"name": "Secure Data Valid", "method": "get", "url": "/secure-data", "headers": {"Authorization": "TokenSecret"}, "expected": 200},
    {"name": "Secure Data Invalid", "method": "get", "url": "/secure-data", "expected": 401},
    {"name": "Register User", "method": "post", "url": "/register", "json": {"name": "Bob", "email": "bob@example.com", "password": "pass"}, "expected": 200},
    {"name": "Category Book", "method": "get", "url": "/category/book", "expected": 200},
    {"name": "Category Invalid", "method": "get", "url": "/category/unknown", "expected": 422},
    {"name": "List Users", "method": "get", "url": "/users", "expected": 200},
    {"name": "Upload File", "method": "post", "url": "/uploadfile", "files": {"file": ("test.txt", b"Hello world")}, "expected": 200},
    {"name": "Download Missing", "method": "get", "url": "/download/nope.txt", "expected": 404},
    {"name": "Form Login", "method": "post", "url": "/login", "data": {"username": "user1", "password": "pwd"}, "expected": 200},
    {"name": "Read Unicorn OK", "method": "get", "url": "/unicorns/ok", "expected": 200},
    {"name": "Read Unicorn Error", "method": "get", "url": "/unicorns/yolo", "expected": 418},
    {"name": "Stream Response", "method": "get", "url": "/stream", "stream": True, "expected": 200},
    {"name": "DB Dependency", "method": "get", "url": "/items-db", "expected": 200},
    {"name": "Create User Examples", "method": "post", "url": "/users-examples", "json": {"id": 2, "name": "Alice", "email": "alice@example.com"}, "expected": 201},
]

passed = 0
for test in tests:
    method = getattr(requests, test["method"])
    kwargs = {k: test[k] for k in ("params", "json", "headers", "files", "data") if k in test}
    if test.get("stream"):
        kwargs["stream"] = True
    r = method(BASE_URL + test["url"], **kwargs)
    result = "PASS" if r.status_code == test["expected"] else "FAIL"
    print(f"{test['name']}: {r.status_code} expected {test['expected']} -> {result}")
    if result == "PASS":
        passed += 1

# WebSocket test
async def test_ws():
    uri = BASE_URL.replace('http', 'ws') + "/ws"
    try:
        async with websockets.connect(uri) as ws:
            await ws.send("ping")
            resp = await ws.recv()
            return resp == "Echo: ping"
    except Exception:
        return False

ws_result = asyncio.run(test_ws())
print(f"WebSocket: {'PASS' if ws_result else 'FAIL'}")
if ws_result:
    passed += 1

total = len(tests) + 1  # +1 for websocket
print(f"\nSummary: {passed} passed, {total - passed} failed, out of {total} tests.")