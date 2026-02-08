import socket
import json
import time

HOST = "localhost"
PORT = 8000

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))


# ---------- UNARY RPC ----------
def unary_rpc():
    name = input("Enter your name: ")

    request = {
        "rpc_type": "unary",
        "data": {
            "name": name
        }
    }

    client.send(json.dumps(request).encode())

    response = json.loads(client.recv(2048).decode())
    print("\nUnary Response:", response)


# ---------- SERVER STREAMING RPC ----------
def server_stream_rpc():
    patient = input("Enter patient name for monitoring: ")

    request = {
        "rpc_type": "server_stream",
        "data": {
            "patient_name": patient
        }
    }

    client.send(json.dumps(request).encode())

    print("\nReceiving detailed vitals...\n")

    for i in range(5):
        data = client.recv(2048).decode()
        vitals = json.loads(data)

        print(f"Reading {vitals['reading_number']}")
        print("Patient:", vitals["patient"])
        print("Heart Rate:", vitals["heart_rate"])
        print("Blood Pressure:", vitals["blood_pressure"])
        print("Oxygen Level:", vitals["oxygen_level"])
        print("Temperature:", vitals["temperature"])
        print("Status:", vitals["status"])
        print("Time:", vitals["timestamp"])
        print("-----------------------------\n")


# ---------- CLIENT STREAMING RPC ----------
def client_stream_rpc():
    request = {
        "rpc_type": "client_stream"
    }

    client.send(json.dumps(request).encode())

    print("\n--- Upload Medical Reports ---")
    print("Type report names one by one. Type 'done' when finished.\n")

    while True:
        report_name = input("Enter report name: ")

        if report_name.lower() == "done":
            break

        report = {
            "report_name": report_name,
            "date": time.strftime("%Y-%m-%d")
        }

        client.send(json.dumps(report).encode())

    client.send("END".encode())

    response = json.loads(client.recv(2048).decode())

    print("\n--- SERVER SUMMARY ---")
    print("Status:", response["status"])
    print("Total Reports:", response["total_reports"])
    print("Reports:", response["report_list"])
    print("Doctor Comment:", response["doctor_comment"])
    print("Time:", response["timestamp"])


# ---------- BIDIRECTIONAL STREAMING RPC ----------
def bidi_stream_rpc():
    request = {
        "rpc_type": "bidi_stream"
    }

    client.send(json.dumps(request).encode())

    print("\nStarting Live Consultation with Latency Measurement...\n")

    latencies = []

    while True:
        msg = input("Patient: ")

        send_time = time.time()

        packet = {
            "text": msg,
            "timestamp": send_time
        }

        client.send(json.dumps(packet).encode())

        if msg == "bye":
            break

        data = client.recv(2048).decode()
        response = json.loads(data)

        receive_time = time.time()

        latency = receive_time - send_time
        latencies.append(latency)

        print("Doctor:", response["text"])
        print(f"Latency: {latency * 1000:.2f} ms\n")

    if latencies:
        avg = sum(latencies) / len(latencies)
        print(f"\nAverage Latency: {avg * 1000:.2f} ms")


# ---------- MENU ----------
print("\nSelect RPC Type:")
print("1. Unary RPC")
print("2. Server Streaming RPC")
print("3. Client Streaming RPC")
print("4. Bidirectional Streaming RPC")

choice = input("Enter choice: ")

if choice == "1":
    unary_rpc()

elif choice == "2":
    server_stream_rpc()

elif choice == "3":
    client_stream_rpc()

elif choice == "4":
    bidi_stream_rpc()

client.close()
