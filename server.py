import socket
import json
import time

HOST = "localhost"
PORT = 8000

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)

print("Telemedicine RPC Server Started...")

conn, addr = server.accept()
print("Connected to:", addr)


# ---------- UNARY RPC ----------
def handle_unary(data):
    name = data["name"]
    return {
        "message": f"Welcome {name} to Telemedicine System",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }


# ---------- SERVER STREAMING RPC ----------
def handle_server_stream(request_data):
    patient = request_data["patient_name"]

    print(f"Starting live monitoring for patient: {patient}")

    for i in range(5):
        vitals = {
            "patient": patient,
            "reading_number": i + 1,
            "heart_rate": 70 + i,
            "blood_pressure": f"{120+i}/{80+i}",
            "oxygen_level": 98 - i,
            "temperature": 98.5 + (i * 0.1),
            "status": "Stable" if i < 3 else "Observation Needed",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        conn.send(json.dumps(vitals).encode())
        time.sleep(2)

    print("Completed monitoring stream.")


# ---------- CLIENT STREAMING RPC ----------
def handle_client_stream():
    print("Receiving reports from patient...")

    reports = []
    count = 0

    while True:
        data = conn.recv(2048).decode()

        if data == "END":
            break

        report = json.loads(data)
        reports.append(report)
        count += 1

        print(f"Received Report {count}: {report['report_name']}")

    summary = {
        "status": "Reports Successfully Received",
        "total_reports": count,
        "report_list": [r["report_name"] for r in reports],
        "doctor_comment": "Reports will be analyzed shortly",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    conn.send(json.dumps(summary).encode())


# ---------- BIDIRECTIONAL STREAMING RPC ----------
def handle_bidi_stream():
    print("Live Consultation Started with Latency Monitoring...")

    while True:
        data = conn.recv(2048).decode()

        if not data:
            break

        message = json.loads(data)

        if message["text"] == "bye":
            print("Consultation Ended")
            break

        print("Patient:", message["text"])

        reply = input("Doctor: ")

        response = {
            "text": reply,
            "timestamp": time.time()
        }

        conn.send(json.dumps(response).encode())


# ---------- MAIN DISPATCHER ----------
while True:
    request = conn.recv(2048).decode()

    if not request:
        break

    request = json.loads(request)

    rpc_type = request["rpc_type"]

    if rpc_type == "unary":
        response = handle_unary(request["data"])
        conn.send(json.dumps(response).encode())

    elif rpc_type == "server_stream":
        handle_server_stream(request["data"])

    elif rpc_type == "client_stream":
        handle_client_stream()

    elif rpc_type == "bidi_stream":
        handle_bidi_stream()

conn.close()
