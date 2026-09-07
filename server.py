import socket
import threading


SERVER_HOST = "127.0.0.1"
SERVER_PORT = 7000


clients = []


def broadcast(message, sender_socket):

    for client in clients:

        if client != sender_socket:

            try:

                client.send(message)

            except:

                client.close()

                if client in clients:
                    clients.remove(client)


def handle_client(client_socket, client_address):

    print("Client connected:", client_address)

    clients.append(client_socket)

    while True:

        try:

            message = client_socket.recv(1024)

            if not message:

                break

            print(
                f"Message from {client_address}: "
                f"{message.decode()}"
            )

            # Send message to other clients
            broadcast(
                message,
                client_socket
            )

        except:

            break


    if client_socket in clients:

        clients.remove(client_socket)


    client_socket.close()

    print(
        "Client disconnected:",
        client_address
    )


# Create server
server_socket = socket.socket(
    socket.AF_INET,
    socket.SOCK_STREAM
)


server_socket.bind(
    (SERVER_HOST, SERVER_PORT)
)


server_socket.listen()


print("Server started on port 5000")
print("Waiting for clients...")


while True:

    client_socket, client_address = server_socket.accept()


    client_thread = threading.Thread(
        target=handle_client,
        args=(
            client_socket,
            client_address
        )
    )


    client_thread.start()