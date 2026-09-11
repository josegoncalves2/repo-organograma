param(
  [int]$Porta = 8085,
  [string]$ListenAddress = ""
)

$principal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  Write-Error "Execute este script em um PowerShell aberto como Administrador."
  exit 1
}

if (-not $ListenAddress) {
  $candidatos = Get-NetIPConfiguration |
    Where-Object { $_.IPv4Address -and $_.IPv4DefaultGateway } |
    ForEach-Object { $_.IPv4Address.IPAddress } |
    Where-Object { $_ -notlike "127.*" -and $_ -notlike "169.254.*" }
  $ListenAddress = @($candidatos)[0]
}

if (-not $ListenAddress) {
  Write-Error "Nao encontrei um IPv4 de rede. Informe -ListenAddress manualmente."
  exit 1
}

$nomeRegra = "Organograma $Porta"

Get-NetFirewallRule -DisplayName $nomeRegra -ErrorAction SilentlyContinue |
  Remove-NetFirewallRule

New-NetFirewallRule `
  -DisplayName $nomeRegra `
  -Direction Inbound `
  -Action Allow `
  -Protocol TCP `
  -LocalPort $Porta `
  -Profile Any | Out-Null

netsh interface portproxy delete v4tov4 listenaddress=$ListenAddress listenport=$Porta | Out-Null
netsh interface portproxy add v4tov4 listenaddress=$ListenAddress listenport=$Porta connectaddress=127.0.0.1 connectport=$Porta | Out-Null

Write-Host "Organograma exposto em: http://$ListenAddress`:$Porta"
