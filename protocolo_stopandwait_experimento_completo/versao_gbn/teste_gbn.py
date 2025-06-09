#!/usr/bin/env python3

import os
import time
import subprocess
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.link import TCLink
import matplotlib.pyplot as plt

janelas = [4, 8, 16]
testes = [
    ("A", 1, 50, 0),
    ("B", 1, 200, 0),
    ("C", 1, 200, 5),
    ("D", 10, 100, 0),
    ("F", 100, 300, 0),
    ("G", 100, 300, 5),
    ("H", 100, 300, 10),
]
metricas = [
    "Transmissao_(s)",
    "Arquivo_(bits)",
    "LOSS_(%)",
    "Eficiencia"
]

class StopAndWaitTopo(Topo):
    def __init__(self, bw, delay, loss):
        super().__init__()
        client = self.addHost('h1')
        server = self.addHost('h2')
        switch = self.addSwitch('s1')
        self.addLink(client, switch, bw=bw, delay="{}ms".format(delay), loss=loss)
        self.addLink(server, switch, bw=bw, delay="{}ms".format(delay), loss=loss)

def plot(caso, metrica):
    filename = "logs/{}/{}.txt".format(caso, metrica)
    resultados = {}
    if not os.path.isfile(filename):
        return
    with open(filename) as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                janela, valor = parts
                resultados[int(janela)] = float(valor)
    xs = [4, 8, 16]
    ys = [resultados.get(x, 0) for x in xs]

    plt.figure(figsize=(6, 4))
    plt.plot(xs, ys, marker='o', color="steelblue")
    plt.title("{} - {}".format(caso, metrica))
    plt.xlabel("Janela")
    plt.ylabel(metrica)
    plt.tight_layout()
    os.makedirs("graficos/{}".format(caso), exist_ok=True)
    plt.savefig("graficos/{}/{}.png".format(caso, metrica))
    plt.close()
    print("[INFO] Gráfico salvo como 'graficos/{}/{}.png'".format(caso, metrica))

def run_command(cmd):
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = proc.communicate()
    return out, err

def main():
    if os.geteuid() != 0:
        print("Por favor, execute como root (sudo).")
        exit(1)

    os.makedirs("graficos", exist_ok=True)
    os.makedirs("logs", exist_ok=True)

    for caso, vel, atraso, perda in testes:
        print("[TESTE] Caso: {} | Velocidade: {} | Atraso: {} | Perda: {}".format(caso, vel, atraso, perda))
        os.makedirs("graficos/{}".format(caso), exist_ok=True)
        os.makedirs("logs/{}".format(caso), exist_ok=True)

        for metrica in metricas:
            open("logs/{}/{}.txt".format(caso, metrica), 'w').close()

        topo = StopAndWaitTopo(bw=vel, delay=atraso, loss=perda)
        net = Mininet(topo=topo, link=TCLink, controller=None)
        net.start()
        time.sleep(3)

        h1 = net.get('h1')
        h2 = net.get('h2')

        for janela in janelas:
            print("[JANELA]: {}".format(janela))

            servidor_log = "logs/{}/servidor_log_{}.txt".format(caso, janela)
            h2.cmd("python3 -u servidor_gbn.py > {} 2>&1 &".format(servidor_log))
            time.sleep(5)

            cliente_log = "logs/{}/cliente_log_{}.txt".format(caso, janela)
            start = time.time()
            h1.cmd("python3 -u cliente_gbn.py --window {} --file input_02.txt > {} 2>&1 &".format(janela, cliente_log))
            end = time.time()
            runtime = end - start

            print("[INFO] Tempo de transmissão: {:.3f}s".format(runtime))

            tam = os.path.getsize("input_02.txt") * 8 if os.path.isfile("input_02.txt") else 0

            perda_pct = 0.0
            with open(cliente_log) as f:
                for line in f:
                    if "PERCENTAGE_LOST_PACKETS" in line:
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            try:
                                perda_pct = float(parts[1])
                            except:
                                perda_pct = 0.0

            eficiencia = 0.0
            try:
                eficiencia = tam / (runtime * (vel * 1000000))
            except ZeroDivisionError:
                eficiencia = 0.0

            with open("logs/{}/Transmissao_(s).txt".format(caso), 'a') as f:
                f.write("{} {}\n".format(janela, runtime))
            with open("logs/{}/Arquivo_(bits).txt".format(caso), 'a') as f:
                f.write("{} {}\n".format(janela, tam))
            with open("logs/{}/LOSS_(%).txt".format(caso), 'a') as f:
                f.write("{} {}\n".format(janela, perda_pct))
            with open("logs/{}/Eficiencia.txt".format(caso), 'a') as f:
                f.write("{} {}\n".format(janela, eficiencia))

            for metrica in metricas:
                print("[INFO] Gerando gráfico para {}...".format(metrica))
                plot(caso, metrica)

            diff_out, _ = run_command("diff output.txt input_02.txt")
            if diff_out == '':
                print("[SUCCESS] Arquivos coincidem.")
            else:
                print("[FAIL] Arquivos não coincidem. Veja diff_result.txt.")
                with open("diff_result.txt", 'w') as f:
                    f.write(diff_out)

        net.stop()

    print("[INFO] Testes concluídos.")

if __name__ == "__main__":
    main()

