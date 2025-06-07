import socket
import time

SERVER_IP = '10.0.0.2'
PORT = 5000
TIMEOUT = 2
BLOCK_SIZE = 512

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    with open('input.txt', 'rb') as file:
        seq = 0
        while True:
            data = file.read(BLOCK_SIZE)
            if not data:
                break

            acked = False
            while not acked:
                packet = seq.to_bytes(1, 'big') + data
                sock.sendto(packet, (SERVER_IP, PORT))
                print('Enviado quadro com seq={}'.format(seq))
                try:
                    ack, _ = sock.recvfrom(1)
                    if int.from_bytes(ack, 'big') == seq:
                        acked = True
                        print('ACK {} recebido'.format(seq))
                except socket.timeout:
                    print('Timeout, reenviando seq={}'.format(seq))
            seq = 1 - seq

    print('Transmissão finalizada.')
    print('Encerrando conexão.')
    acked = False
    TO = False
    while not acked and not TO:
        packet = seq.to_bytes(1, 'big')
        sock.sendto(packet, (SERVER_IP, PORT))
        print('Enviado quadro com seq={}'.format(seq))
        try:
            ack, _ = sock.recvfrom(1)
            if int.from_bytes(ack, 'big') == seq:
                acked = True
                print('ACK {} recebido'.format(seq))
        except socket.timeout:
            print('Timeout, encerrando')
            TO = True

    sock.close()

if __name__ == '__main__':
    main()
