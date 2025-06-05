# Projeto de Redes - Avaliação de Protocolos Confiáveis com Mininet

## 🎯 Objetivo

Avaliar a eficiência dos protocolos **Selective Repeat** (comparado com Stop-and-Wait), com execução de testes controlados no Mininet em cenários de rede com diferentes **larguras de banda (Mbps)**, **atrasos (ms)** e **taxas de perda (%)**.

Cada grupo deve implementar **um protocolo (GBN ou SR)** e utilizar **Stop-and-Wait como base comparativa**, já fornecido.

---

## 📦 Estrutura

Este projeto contém:

- Implementações base para Stop-and-Wait
- Scripts de topologia para o Mininet
- Estrutura para implementar Go-Back-N ou Selective Repeat
- Scripts de teste automatizado e coleta de métricas
- Arquivos de exemplo para transmissão (`input.txt`, `output.txt`)

---

## 🧪 Tabela de Cenários de Teste

| Cenário | Velocidade (Mbps) | Atraso (ms) | Perda (%) |
|---------|-------------------|-------------|-----------|
| A       | 1                 | 50          | 0         |
| B       | 1                 | 200         | 0         |
| C       | 1                 | 200         | 5         |
| D       | 10                | 100         | 0         |
| E       | 10                | 100         | 10        |
| F       | 100               | 300         | 0         |
| G       | 100               | 300         | 5         |
| H       | 100               | 300         | 10        |

---

## 🔧 Variação de Janela nos Protocolos

Para os protocolos **Go-Back-N (GBN)** e **Selective Repeat (SR)**, execute os testes com os seguintes tamanhos de janela:

- `N = 4, 8, 16`

Avalie o impacto da janela nos seguintes aspectos:

- Eficiência
- Número de retransmissões
- Robustez a perdas
- Tempo total de transmissão

---

## 📊 Coleta de Métricas

Durante cada experimento, registre:

- Tamanho do arquivo transmitido (em bits)
- Tempo total de transmissão (em segundos)
- Número de quadros enviados e retransmitidos
- Eficiência calculada por:

\[
\text{Eficiência} = \frac{\text{bits úteis recebidos}}{\text{tempo total (s)} \times \text{largura de banda (bps)}}
\]

---

## 📈 Ferramentas Sugeridas

- `time.time()` para medição do tempo (Python)
- `matplotlib` para gráficos de desempenho
- `Wireshark` (opcional) para análise de pacotes
- `bash` + `Mininet` + `xterm` + `scripts de automação` (ex: `teste_sw.sh`)

---

## 🧪 Execução no Mininet

1. Inicie a topologia:
```bash
sudo mn --custom topo_stopandwait.py --topo stopandwait --link tc --controller=remote
```

2. Em terminais separados:
```bash
mininet> xterm h1
mininet> xterm h2
```

3. Execute os scripts:
- Em `h2` (servidor):
```bash
python3 servidor_sr.py
```

- Em `h1` (cliente):
```bash
python3 cliente_sr.py
```

---

## 📁 Entregáveis

- Implementação completa do protocolo Selective Repeat (SR)
- Código fornecido de Stop-and-Wait (base comparativa)
- Scripts e logs de teste
- Gráficos de desempenho
- Relatório final (PDF), contendo:
  - Descrição da implementação
  - Tabelas e gráficos por cenário
  - Análise comparativa entre o protocolo implementado e Stop-and-Wait

---

## 🧠 Discussão Esperada no Relatório

- Impacto da latência, perda e banda na eficiência
- Comparação entre o protocolo implementado e Stop-and-Wait
- Análise dos efeitos do tamanho da janela
- Observações sobre escalabilidade e uso de recursos

---

## 📊 Avaliação

| Critério                      | Peso |
|------------------------------|------|
| Implementação funcional       | 30%  |
| Análise e métricas experimentais | 30%  |
| Gráficos e interpretação dos dados | 20%  |
| Clareza e organização do relatório | 20%  |
