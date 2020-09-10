import sys
import socket
import threading


def server_loop():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] falha ao dar bind em %s:%d") % (local_host, local_port)
        print("[!!] procure por outros sockets ouvindo ou corriga as permissões.")
        sys.exit(0)
    print("[*] Escutando em %s:%d...")

    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        # exibe informações sobre a conexão local
        print("[==>] conexão recebida de %s:%d") % (addr[0], addr[1])
        # inicia uma thread para conversar com o host remoto
        proxy_thread = threading.Thread(target=proxy_handler,
                                        args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()


def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    # conecta-se ao host remoto
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # recebe dados do lado remoto se for necessario
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # envia os dados ao nosso handler de resposta
        remote_buffer = response_handler(remote_buffer)

        # se houver dados para serem enviados ao nosso cliente local, envia-os
        if len(remote_buffer):
            print("[<==] Enviando %d bytes para localhost") % (
                len(remote_buffer))
            client_socket.send(remote_buffer)
    # agora a gente lê o que tá rolando no localhost, enviar pro remotehost,enviar pro local e assim vai.
    while True:
        # lê do host local
        local_buffer = receive_from(client_socket)
        if(len(local_buffer)):
            print("[==>] %d bytes recebidos do localhost") % (
                len(remote_buffer))
            hexdump(local_buffer)

            # envia os dados para o handler de soliticação
            local_buffer = request_handler(local_buffer)
            # envia os dados para o host remoto
            remote_socket.send(local_buffer)
            print("[==>] Enviado para o remote")
        # recebe a resposta
        remote_buffer = receive_from(remote_socket)
        if(len(remote_buffer)):
            print("[<==] %d bytes recebidos do remotehost") % (
                len(remote_buffer))
            hexdump(remote_buffer)
            # envia os dados ao handler de resposta
            remote_buffer = response_handler(remote_buffer)
            # envia a resposta para o socket local
            client_socket.send(remote_buffer)
            print("[<==] enviado para o localhost")
        # se não tiver mais dados em nenhum dos lados, a gente fecha a conexão
        if not (len(local_buffer)) or not (len(remote_buffer)):
            client_socket.close()
            remote_socket.close()
            print("[*] Sem dados, encerrando conexão")
            break

# Nem pergunta por que eu também não sei, só sei que funciona


def hexdump():
    result = []
    digits = 4 if isinstance(src, unicode) else 2
    for i in range(0, len(src), lenght):
        s = src[i:i+lenght]
        hexa = b''.join(["%0*X" % (digits, ord(x)) for x in s])
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X    %-*s    %s" %
                      (i, lenght*(digits + 1), hexa, text))
    print(b'\n'.join(result))


def receive_from(connection):
    buffer = ""

    # definimos um timeout de 2 segundos, dependendo do alvo, pode aumentar
    connection.settimeout(2)
    try:
        # continua lendo em buffer até que não haja mais dados ou que a temporização expire
        while True:
            data = connection.recv(4096)
            if not data:
                break
            buffer += data
    except:
        pass
    return buffer


# modifica qualquer solicitação destiniada ao host remoto
def request_handler(buffer):
    # faz modificações no packet
    return buffer


# modifica qualquer resposta destinada ao host local
def response_handler(buffer):
    # faz modificações no packet
    return buffer


def main():
    if len(sys.argv[1:]) != 5:
        print(
            "Uso: ./proxyTCP.py [localhost] [localport] [remotehost] [remoteport] [receive_first] \n")
        print("Exemplo: ./proxyTCP.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)

    # define parâmetros pra ouvir localmente
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    # define o alvo remoto
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    # agora vem o proxy mesmo pra interceptar a conexão antes de enviar pro host
    receive_first = sys.argv[5]
    if("True" in receive_first):
        receive_first = True
    else:
        receive_first = False
    # Agora a gente põe o socket pra mamar
    server_loop(local_host, local_port, remote_host,
                remote_port, receive_first)


main()
