import socket

IP = '10.0.0.2'
PORT = 5000
BUFFER_SIZE = 513

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((IP, PORT))

    expected_seq = 0

    with open('output.txt', 'wb') as file:
        print('Servidor aguardando dados...')
        while True:
            expected_seq = expected_seq % 256
            try:
                data, addr = sock.recvfrom(BUFFER_SIZE)
                seq = data[0]
                payload = data[1:]

                if len(payload) > 1:
                    if seq == expected_seq:
                        file.write(payload)
                        print('Recebido seq={}, dados gravados.'.format(seq))
                        expected_seq += 1

                    else:
                        print('Descartado seq={}, espera-se seq={}.'.format(seq, expected_seq))

                    ack = bytes([expected_seq - 1])
                    print('ACK {} enviado.'.format(expected_seq - 1))
                    
                else:
                    print('Recebido sinal de encerramento, payload é nulo')
                    ack = bytes([seq])
                    print('ACK {} enviado.'.format(seq))
                    break
                    
                sock.sendto(ack, addr)

            except Exception as e:
                print('Erro: {}'.format(e))
                break


    sock.close()

if __name__ == '__main__':
    main()
