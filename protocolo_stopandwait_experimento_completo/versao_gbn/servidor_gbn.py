# Servidor GBN - a ser implementado
import socket

IP = '10.0.0.2'
PORT = 5000
BUFFER_SIZE = 1024
WINDOW_SIZE = 4

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    expected_seq = 0
    sliding_window = {}

    with open('output.txt', 'wb') as file:
        print('Servidor aguardando dados...')
        while True:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                seq = data[0]
                payload = data[1:]

                if seq == expected_seq:
                    file.write(payload)
                    print(f'Recebido seq={seq}, dados gravados.')
                    expected_seq += 1

                elif seq > expected_seq:
                    sliding_window[seq] = payload
                    print(f'Pacote seq={seq} armazenado na janela.')

                ack = bytes([expected_seq - 1])
                sock.sendto(ack, addr)
                print(f'ACK {expected_seq - 1} enviado.')

            except Exception as e:
                print(f'Erro: {e}')
                break

    sock.close()

if __name__ == '__main__':
    main()
