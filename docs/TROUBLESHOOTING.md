# Troubleshooting

## Container nao sobe

Verifique:

```bash
cd /mnt/c/Users/40446686808/projetos/organograma
docker compose ps
docker compose logs --tail=100 orgchart
```

## Porta 8085 nao responde

No WSL:

```bash
ss -ltnp | grep ':8085'
curl -fsS http://localhost:8085/api/saude
curl -fsS http://192.168.0.218:8085/api/saude
```

No Windows:

```powershell
curl.exe http://localhost:8085/api/saude
curl.exe http://192.168.0.218:8085/api/saude
```

Se funciona no WSL e no Windows local, mas nao em outro computador:

- confirmar que o outro computador esta na mesma rede;
- verificar bloqueio de VLAN;
- verificar firewall corporativo;
- confirmar IP atual com `ipconfig`.

## WSL nao aplica rede espelhada

Arquivo esperado:

```text
C:\Users\40446686808\.wslconfig
```

Deve conter:

```ini
[wsl2]
networkingMode=Mirrored
firewall=false

[experimental]
hostAddressLoopback=true
```

Depois de alterar:

```powershell
wsl --shutdown
```

Suba novamente:

```bash
cd /mnt/c/Users/40446686808/projetos/organograma
docker compose up -d
```

## Seletor mostra itens repetidos

O seletor deve desambiguar nomes repetidos com o ancestral institucional.

Exemplo esperado:

```text
Divisao Administrativa - GABINETE DO PREFEITO
Divisao Administrativa - SECRETARIA MUNICIPAL DE SAUDE
```

Se aparecerem varias opcoes identicas, recarregue com `Ctrl+F5` e confirme que o container foi rebuildado.

## Dados nao salvam

Verifique logs:

```bash
docker compose logs --tail=100 orgchart
```

O arquivo persistente fica no volume Docker:

```text
/dados/organograma.json
```

O servidor recusa salvar dados invalidos para evitar organograma em branco.

