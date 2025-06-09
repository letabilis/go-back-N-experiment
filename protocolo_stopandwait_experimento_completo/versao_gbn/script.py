import os, matplotlib.pyplot as plt

# Configs
cenarios = [
    {"Caso": "A", "Bandwidth": 1, "Delay": 50, "Loss": 0},
    {"Caso": "B", "Bandwidth": 1, "Delay": 200, "Loss": 0},
    {"Caso": "C", "Bandwidth": 1, "Delay": 200, "Loss": 5},
    {"Caso": "D", "Bandwidth": 10, "Delay": 100, "Loss": 0},
    {"Caso": "F", "Bandwidth": 100, "Delay": 300, "Loss": 0},
    {"Caso": "G", "Bandwidth": 100, "Delay": 300, "Loss": 5},
    {"Caso": "H", "Bandwidth": 100, "Delay": 300, "Loss": 10},
]

janelas = [4, 8, 16]


def new_topology(bandwidth, delay, loss):
    with open('topo_stopandwait.py', 'w') as f:
        f.write((
            "from mininet.topo import Topo\n\n"
            "class StopAndWaitTopo(Topo):\n"
            "    def build(self):\n"
            "        client = self.addHost('h1')\n"
            "        server = self.addHost('h2')\n"
            "        switch = self.addSwitch('s1')\n"
            "        self.addLink(client, switch, bw={}, delay='{}ms', loss={})\n"
            "        self.addLink(server, switch, bw={}, delay='{}ms', loss={})\n\n"
            "topos = {{'stopandwait': (lambda: StopAndWaitTopo())}}\n"
        ).format(bandwidth, delay, loss, bandwidth, delay, loss))

def plot():
    pass

for cenario in cenarios:
    caso, bw, delay, loss = cenario.values()
    os.makedirs("resultados/logs/{}".format(caso))
    os.makedirs("resultados/graficos/{}".format(caso))
    new_topology(bw, delay, loss)
    for janela in janelas:
        os.replace("./tempo_execucao.txt", "./resultados/logs/{}/tempo_execucao.txt".format(caso))
        
    plot(#todo)


'''    
function plot {
  local caso=$1
  local metrica=$2
  python3 <<EOF
import matplotlib.pyplot as plt

filename = "logs/${caso}/${metrica}.txt"

resultados = {}
with open(filename) as f:
    for line in f:
        janela, valor = line.strip().split()
        resultados[int(janela)] = float(valor)

plt.figure(figsize=(6, 4))
plt.plot([4, 8, 16], [resultados.get(k, 0) for k in [4, 8, 16]], marker='o', color="steelblue")
plt.title("${caso} - ${metrica}")
plt.xlabel("Janela")
plt.ylabel("${metrica}")
plt.tight_layout()
plt.savefig("graficos/${caso}/${metrica}.png")
print("[INFO] Grafico salvo como 'graficos/${caso}/${metrica}.png'")
EOF
}
''''

 

