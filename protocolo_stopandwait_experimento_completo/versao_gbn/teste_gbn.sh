#!/bin/bash

# Teste automatizado do protocolo gbn com Mininet
# Requer: Mininet, xterm, Python3, matplotlib, bc, awk

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute como root (sudo)"
  exit
fi

# Diretórios
mkdir -p -v graficos
mkdir -p -v logs

# Configurações
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
metricas=(
  "Transmissao_(s)"
  "Arquivo_(bits)"
  "LOSS_(%)"
  "Eficiencia"
)

# Funções auxiliares
function init_topology {

  local vel=$1
  local atraso=$2
  local perda=$3

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
}

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

for teste in "${testes[@]}"; do
  parametros=($teste)
  caso=${parametros[0]}
  vel=${parametros[1]}
  atraso=${parametros[2]}
  perda=${parametros[3]}

  printf "[TESTE] Caso: %s | Velocidade: %s | Atraso: %s | Perda: %s\n\n" "$caso" "$vel" "$atraso" "$perda"

  mkdir -p -v graficos/${caso}/
  mkdir -p -v logs/${caso}/

  for metrica in "${metricas[@]}"; do
    : >"logs/${caso}/${metrica}.txt"
  done

  init_topology $vel $atraso $perda

  echo "[INFO] Iniciando Mininet..."
  mn --custom topo_stopandwait.py --topo stopandwait --link tc >/dev/null 2>&1 &
  sleep 3

  for janela in "${janelas[@]}"; do
    printf "[JANELA]: %s\n" "$janela"

    echo "[INFO] Executando servidor em h2..."
    h2=$(pgrep -f "mnexec.*h2")
    xterm -e "mnexec -a $h2 python3 servidor_gbn.py > servidor_log.txt" &
    sleep 5

    echo "[INFO] Iniciando medicao de tempo e cliente em h1..."
    START=$(date +%s.%N)

    h1=$(pgrep -f "mnexec.*h1")
    xterm -e "mnexec -a $h1 python3 cliente_gbn.py --window $janela --file input_02.txt > cliente_log.txt" &
    sleep 15

    END=$(date +%s.%N)
    RUNTIME=$(echo "$END - $START" | bc)

    for metrica in "${metricas[@]}"; do
      printf "[INFO] %s: " "$metrica"
      case "$metrica" in
      "Transmissao_(s)")
        echo "$janela $RUNTIME" >>"logs/${caso}/${metrica}.txt"
        printf "%s\n" "$RUNTIME segundos"
        ;;
      "Arquivo_(bits)")
        tam=$(($(stat -c %s input_02.txt) * 8))
        echo "$janela $tam" >>"logs/${caso}/${metrica}.txt"
        printf "%s\n" "$tam bits"
        ;;
      "LOSS_(%)")
        taxa_pacotes_perdidos=$(grep "PERCENTAGE_LOST_PACKETS" "cliente_log.txt" | awk '{print $2}')
        echo "$janela $taxa_pacotes_perdidos" >>"logs/${caso}/${metrica}.txt"
        printf "%s\n" "$taxa_pacotes_perdidos"
        ;;
      "Eficiencia")
        taxa_perda_decimal=$(echo "scale=4; $taxa_pacotes_perdidos / 100" | bc)
        tam_ajustado=$(echo "$tam * (1 + $taxa_perda_decimal)" | bc)
        eficiencia=$(echo "scale=8; $tam_ajustado / ($RUNTIME * ($vel * 1000000))" | bc)
        echo "$janela $eficiencia" >>"logs/${caso}/${metrica}.txt"
        printf "%s\n" "$eficiencia"
        ;;
      esac

      echo "[INFO] Gerando grafico comparativo para o cenario [$caso/$metrica]..."
      plot ${caso} "${metrica}"
    done

    echo "[INFO] Verificando integridade dos dados..."
    if diff output.txt input.txt >diff_result.txt; then
      echo "[SUCCESS] Arquivos coincidem."
    else
      echo "[FAIL] Arquivos nao coincidem. Veja diff_result.txt."
    fi
  done
done

echo "[INFO] Encerrando Mininet..."
mn -c
