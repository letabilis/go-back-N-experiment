import socket

IP = '10.0.0.2'
PORT = 5000
BUFFER_SIZE = 512 + 1 

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    expected_seq = 0

    with open('output.txt', 'wb') as file:
        print('Servidor aguardando dados...')
        encerramento = False
        while not encerramento:
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                seq = data[0]
                payload = data[1:]

                if seq == expected_seq:
                    file.write(payload)
                    print('Recebido seq={}, dados gravados.'.format(seq))
                    expected_seq += 1

                elif seq > expected_seq:
                    print('Descartado seq={}, espera-se seq={}.'.format(seq, expected_seq))

                ack = bytes([expected_seq - 1])
                sock.sendto(ack, addr)
                print('ACK {} enviado.'.format(expected_seq - 1))

            except IndexError as e:
                print('Recebido sinal de encerramento, payload é nulo')
                encerramento = True

    sock.close()

if __name__ == '__main__':
    main()
