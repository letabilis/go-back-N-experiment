import socket

N = 4
TIMEOUT = 2
BLOCK_SIZE = 512
SERVER_IP = '10.0.0.2'
PORT = 5000

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    sliding_window = []
    next_seq = current_seq = 0

    with open('input.txt', 'rb') as file:
        next_data = file.read(BLOCK_SIZE)

        while True:
            while len(sliding_window) < N and next_data:
                seq_byte = next_seq.to_bytes(1, 'big')
                packet = seq_byte + next_data
                sock.sendto(packet, (SERVER_IP, PORT))
                sliding_window.append((next_seq, packet))
                print('Enviado quadro com seq={}'.format(next_seq))
                next_seq += 1

                next_data = file.read(BLOCK_SIZE)

            if current_seq == next_seq and not next_data:
                break

            try:
                ack, _ = sock.recvfrom(1)
                ack_num = int.from_bytes(ack, 'big')
                print('ACK {} recebido'.format(ack_num))

                if ack_num >= current_seq:
                    sliding_window = [
                        (seq, p) for seq, p in sliding_window if seq > ack_num
                    ]
                    current_seq = ack_num + 1

            except socket.timeout:
                print('Timeout, reenviando a partir de seq={}'.format(current_seq))
                for seq, packet_data in sliding_window:
                    sock.sendto(packet_data, (SERVER_IP, PORT))
                    print('Reenviado quadro com seq={}'.format(seq))

    print('Transmissão finalizada.')
    print('Enviando sinal de encerramento.')

    acked = False
    while not acked:
        packet = next_seq.to_bytes(1, 'big')
        sock.sendto(packet, (SERVER_IP, PORT))
        print('Enviado quadro de encerramento com seq={}'.format(next_seq))
        try:
            ack, _ = sock.recvfrom(1)
            if int.from_bytes(ack, 'big') == next_seq:
                acked = True
                print('ACK {} recebido para encerramento'.format(next_seq))
        except socket.timeout:
            print('Timeout, reenviando encerramento')

    sock.close()


if __name__ == '__main__':
    main()
