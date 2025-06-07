#!/bin/bash

# Teste automatizado do protocolo gbn com Mininet
# Requer: Mininet, xterm, Python3, matplotlib, bc

# Verifica se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo "Por favor, execute como root (sudo)"
  exit
fi

echo "[INFO] Limpando Mininet..."
mn -c

echo "[INFO] Iniciando Mininet..."
mn --custom topo_stopandwait.py --topo stopandwait --link tc >/dev/null 2>&1 &
sleep 3

echo "[INFO] Executando servidor em h2..."
xterm -e "mnexec -a $(pgrep -f 'bash.*h2') python3 servidor_gbn.py > servidor_log.txt" &
sleep 2

echo "[INFO] Iniciando medição de tempo e cliente em h1..."
START=$(date +%s.%N)

xterm -e "mnexec -a $(pgrep -f 'bash.*h1') python3 cliente_gbn.py > cliente_log.txt" &

sleep 15

END=$(date +%s.%N)
RUNTIME=$(echo "$END - $START" | bc)
echo "[INFO] Tempo de transmissão: $RUNTIME segundos"
echo "$RUNTIME" >tempo_execucao.txt

# Comparação dos arquivos
echo "[INFO] Verificando integridade dos dados..."
if diff output.txt input.txt >diff_result.txt; then
  echo "[SUCCESS] Arquivos coincidem."
else
  echo "[FAIL] Arquivos não coincidem. Veja diff_result.txt."
fi

# Geração de gráfico com matplotlib
echo "[INFO] Gerando gráfico de tempo..."

python3 <<EOF
import matplotlib.pyplot as plt

with open("tempo_execucao.txt") as f:
      tempo = float(f.read().strip())

plt.figure(figsize=(6,4))
plt.bar([0], [tempo], color="steelblue")
plt.xticks([0], ["gbn"])
plt.title("Tempo de Transmissão - gbn")
plt.ylabel("Tempo (s)")
plt.tight_layout()
plt.savefig("grafico_tempo_gbn.png")
print("[INFO] Gráfico salvo como grafico_tempo_gbn.png")
EOF

echo "[INFO] Encerrando Mininet..."
mn -c
