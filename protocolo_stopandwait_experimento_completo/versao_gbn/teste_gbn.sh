#!/bin/bash

# Teste automatizado do protocolo gbn com Mininet
# Requer: Mininet, xterm, Python3, matplotlib, bc

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute como root (sudo)"
  exit
fi

# Diretórios
mkdir -p graficos
mkdir -p logs

# Parâmetros
janelas=(4 8 16)
testes=(
  "A 1 50 0"
  "B 1 200 0"
  "C 1 200 5"
  "D 10 100 0"
  "F 100 300 0"
  "G 100 300 5"
  "H 100 300 10"
)

for teste in "${testes[@]}"; do
  parametros=($teste)
  caso=${parametros[0]}
  vel=${parametros[1]}
  atraso=${parametros[2]}
  perda=${parametros[3]}
  printf "Caso: %s | Velocidade: %s | Atraso: %s | Perda: %s\n\n" "$caso" "$vel" "$atraso" "$perda"

  >"logs/tempos_caso_${caso}.txt"

  cat >topo_stopandwait.py <<EOF
from mininet.topo import Topo
class StopAndWaitTopo(Topo):
    def build(self):
        client = self.addHost('h1')
        server = self.addHost('h2')
        switch = self.addSwitch('s1')
        self.addLink(client, switch, bw=$vel, delay='${atraso}ms', loss=$perda)
        self.addLink(server, switch, bw=$vel, delay='${atraso}ms', loss=$perda)
topos = {'stopandwait': (lambda: StopAndWaitTopo())}
EOF
  echo "[INFO] Iniciando Mininet..."
  mn --custom topo_stopandwait.py --topo stopandwait --link tc >/dev/null 2>&1 &
  sleep 3

  for janela in "${janelas[@]}"; do
    printf "	Janela: %s\n\n" "$janela"

    echo "[INFO] Executando servidor em h2..."
    xterm -e "mnexec -a $(pgrep -f 'bash.*h2') python3 servidor_gbn.py > logs/servidor_log.txt" &
    sleep 2

    echo "[INFO] Iniciando medição de tempo e cliente em h1..."
    START=$(date +%s.%N)

    xterm -e "mnexec -a $(pgrep -f 'bash.*h1') python3 cliente_gbn.py --window $janela > cliente_log.txt" &
    sleep 15

    END=$(date +%s.%N)
    RUNTIME=$(echo "$END - $START" | bc)
    echo "[INFO] Tempo de transmissão: $RUNTIME segundos"

    echo "$janela $RUNTIME" >>"logs/tempos_caso_${caso}.txt"

    echo "[INFO] Verificando integridade dos dados..."
    if diff output.txt input.txt >diff_result.txt; then
      echo "[SUCCESS] Arquivos coincidem."
    else
      echo "[FAIL] Arquivos não coincidem. Veja diff_result.txt."
    fi
  done

  echo "[INFO] Gerando gráfico comparativo para o caso $caso..."
  python3 <<EOF
import matplotlib.pyplot as plt

resultados = {}
with open("logs/tempos_caso_{}.txt".format("${caso}")) as f:
    for line in f:
        janela, tempo = line.strip().split()
        resultados[int(janela)] = float(tempo)

plt.figure(figsize=(6,4))
plt.plot([4, 8, 16], [resultados[k] for k in [4, 8, 16]], marker='o', color="steelblue")
plt.title("VELOCIDADE: ${vel} | ATRASO: ${atraso} | PERDA: ${perda}")
plt.xlabel("Janela (N)")
plt.ylabel("Tempo (s)")
plt.tight_layout()
plt.savefig("graficos/caso_{}.png".format("${caso}"))
print("[INFO] Gráfico salvo como graficos/caso_{}.png".format("${caso}"))
EOF

done

echo "[INFO] Encerrando Mininet..."
mn -c
