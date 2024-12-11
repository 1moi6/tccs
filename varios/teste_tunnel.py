import paramiko
from paramiko import SSHClient
from paramiko import AutoAddPolicy
import socket

def create_ssh_tunnel(ssh_host, ssh_port, ssh_username, ssh_password, remote_host, remote_port, local_port):
    # Estabelece a conexão SSH
    ssh_client = SSHClient()
    ssh_client.set_missing_host_key_policy(AutoAddPolicy())
    print(f"Conectando-se ao servidor SSH {ssh_host}:{ssh_port}...")
    ssh_client.connect(ssh_host, port=ssh_port, username=ssh_username, password=ssh_password)

    # Cria o túnel
    print(f"Redirecionando o tráfego de {local_port} para {remote_host}:{remote_port}...")
    transport = ssh_client.get_transport()
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_sock.bind(('0.0.0.0', local_port))
    local_sock.listen(1)

    while True:
        client_sock, _ = local_sock.accept()
        print(f"Conexão recebida de {client_sock.getpeername()}")
        remote_sock = transport.open_channel('direct-tcpip', (remote_host, remote_port), ('localhost', 0))

        while True:
            data = client_sock.recv(1024)
            if not data:
                break
            remote_sock.send(data)

            data = remote_sock.recv(1024)
            if not data:
                break
            client_sock.send(data)

        client_sock.close()
        remote_sock.close()

if __name__ == "__main__":
    ssh_host = '200.17.60.251'
    ssh_port = 12299
    ssh_username = 'liama'
    ssh_password = 'npk052515'  # Substitua pela senha correta ou use chave SSH
    remote_host = '10.10.10.2'
    remote_port = 11434
    local_port = 11434  # Porta local onde você escutará o tráfego

    create_ssh_tunnel(ssh_host, ssh_port, ssh_username, ssh_password, remote_host, remote_port, local_port)
