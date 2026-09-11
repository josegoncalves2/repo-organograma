# Operacao com Docker e WSL

## Porta

O servico roda na porta:

```text
8085
```

URL da maquina atual:

```text
http://192.168.0.218:8085
```

## Compose

O `docker-compose.yml` usa `network_mode: host` para o container escutar diretamente no host WSL:

```yaml
network_mode: host
environment:
  PORT: 8085
```

Isso evita depender de publicacao bridge do Docker para a porta `8085`.

## Subir

Execute dentro do WSL:

```bash
cd /mnt/c/Users/40446686808/projetos/organograma
docker compose up -d --build
```

## Validar

```bash
docker compose ps
ss -ltnp | grep ':8085'
curl -fsS http://192.168.0.218:8085/api/saude
```

Saida esperada:

```json
{"ok":true}
```

## Configuracao WSL usada

Arquivo:

```text
C:\Users\40446686808\.wslconfig
```

Configuracao aplicada:

```ini
[wsl2]
networkingMode=Mirrored
firewall=false
processors=2
defaultVhdSize=42949672960
memory=4GB

[experimental]
sparseVhd=true
hostAddressLoopback=true
```

Apos alterar `.wslconfig`, reinicie:

```powershell
wsl --shutdown
```

Depois suba o Compose novamente pelo WSL.

## Observacao sobre Windows

O acesso `localhost:8085` pode funcionar mesmo quando `192.168.0.218:8085` falha, porque sao caminhos de rede diferentes no WSL mirrored.

Para acesso pela rede, validar sempre:

```bash
curl -fsS http://192.168.0.218:8085/api/saude
```

Se funcionar no WSL mas nao em outro computador, verificar firewall corporativo, VLAN, isolamento de cliente ou politica da rede.

