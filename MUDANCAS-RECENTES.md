# Mudanças Recentes do Organograma — Documentação Detalhada

**Data**: 11 de Setembro de 2026  
**Branch**: main  
**Status**: Pronto para deploy

---

## 📋 Resumo Executivo

O projeto organograma recebeu duas atualizações principais que melhoram a **flexibilidade de importação de dados** e a **página de visualização pública**. Todas as mudanças foram validadas e estão prontas para produção.

---

## 🔧 Mudanças Técnicas Detalhadas

### 1. **tree.html — Suporte a Aliases de Campos (Principal)**

#### O Problema Original
A aplicação esperava nomes de campos exatos (ex: `name`, `lastName`, `position`). Quando usuários importavam dados de diferentes fontes (Excel, CSVs de terceiros), os nomes variavam:
- `name` vs `nome` vs `fullName` vs `nome_completo`
- `image` vs `foto` vs `photo` vs `avatar`
- `email` vs `mail` vs `emailCorporativo`

Resultado: dados perdidos, campos vazios, experiência ruim.

#### A Solução: Função `valorCampo` (linha 493)

```javascript
function valorCampo(row, ...chaves) {
  if (!row || typeof row !== "object") return "";
  const alternativos = [];
  
  // Para cada chave passada, gera variações (camelCase, snake_case, etc)
  for (const chave of chaves) {
    if (!chave) continue;
    const base = String(chave);
    alternativos.push(base);                                      // name
    alternativos.push(base.toLowerCase());                        // name
    alternativos.push(base.replace(/[^a-zA-Z0-9]/g, ""));         // name
    alternativos.push(base.replace(/([a-z])([A-Z])/g, "$1_$2").toLowerCase()); // name
    alternativos.push(base.replace(/([a-z])([A-Z])/g, "$1-$2").toLowerCase()); // name
  }
  
  // Tenta cada variação até encontrar valor não-vazio
  for (const chave of alternativos) {
    if (!chave) continue;
    const valor = row[chave];
    if (valor !== undefined && valor !== null && String(valor).trim() !== "") {
      return String(valor).trim();
    }
  }
  return "";
}
```

**Como funciona:**
1. Recebe um objeto `row` e uma lista de nomes de campos alternativos
2. Gera múltiplas variações (camelCase → snake_case, maiúsculas → minúsculas)
3. Tenta achar o primeiro campo que existe e tem valor
4. Retorna o valor ou string vazia

**Exemplo Prático:**
```javascript
// Se row = { nome: "João", cargo: "Gerente", foto_url: "..." }
valorCampo(row, "name", "nome", "fullName")  // → "João"
valorCampo(row, "position", "cargo", "titulo")  // → "Gerente"
valorCampo(row, "image", "imageUrl", "foto", "photo", "foto_url")  // → "..."
```

#### Onde é Usado

1. **Carregamento de CSV na inicialização** (linhas 535-544)
   ```javascript
   const nome = valorCampo(linha, "name", "nome", "fullName", "nomeCompleto", "full_name", "nome_completo", "employeeName", "nomeFuncionario");
   const sobrenome = valorCampo(linha, "lastName", "sobrenome", "surname", "ultimoNome", "last_name", "sobrenome_completo", "lastNameCompleto");
   const cargo = valorCampo(linha, "position", "cargo", "titulo", "title", "cargoAtual", "positionName");
   // ... etc
   ```

2. **Editor de card** (linhas 2816-2825)
   ```javascript
   document.getElementById("ed-name").value = valorCampo(row, "name", "nome", "fullName", ...) || "";
   document.getElementById("ed-lastName").value = valorCampo(row, "lastName", "sobrenome", ...) || "";
   ```

3. **Exportação e visualização** (múltiplas funções)
   ```javascript
   const nome = valorCampo(row, "name", "nome", "fullName", ...);
   const email = valorCampo(row, "email", "mail", "emailCorporativo", ...);
   ```

---

### 2. **tree.html — Carregamento de CSV Remediado**

#### Mudança de Arquivo
- **Anterior**: `await d3.csv("misc/data.csv")`
- **Agora**: `await d3.csv("misc/organograma-completo.csv")`

**Por quê:**
- Arquivo antigo não existe no projeto
- `organograma-completo.csv` é o arquivo correto mantido e sincronizado
- Arquivo foi criado em 10/09/2026 e está pronto

#### Remoção de BOM UTF-8 (linhas 2597-2605)

```javascript
const originais = await d3.csv("misc/organograma-completo.csv", (row) => {
  // Garante que a BOM UTF-8 (﻿) do Excel seja removida das chaves
  const semBom = {};
  for (const k of Object.keys(row || {})) {
    const limpo = k.replace(/^﻿/, "");  // Remove BOM (﻿)
    semBom[limpo] = row[k];
  }
  return semBom;
});
```

**Por quê:**
- Excel às vezes salva UTF-8 com BOM (Byte Order Mark)
- BOM gera caractere invisível `﻿` no início dos nomes de colunas
- Causa problemas ao tentar acessar `row["name"]` quando a chave é realmente `row["﻿name"]`
- A regex `/^﻿/` remove esse caractere

**Teste:**
```
CSV original:   "﻿name","lastName","email"
Depois do fix:  "name","lastName","email"
```

---

### 3. **tree.html — Marcação de Dados Iniciais** ⚠️ CONTÉM BUG

#### O que mudou (linhas 2534-2537)
```javascript
async function carregarDoServidor() {
  const resposta = await fetch("api/organograma", { cache: "no-store" });
  if (!resposta.ok) throw new Error("servidor indisponível");
  const corpo = await resposta.json();
  if (!corpo.existe) return null;
  versaoServidor = corpo.versao;

  // NOVO: Se o servidor está usando dados iniciais (arquivo de fábrica), marcar como alterado
  if (corpo.inicial) {
    marcarAlterado(true);
  }

  return corpo.linhas;
}
```

**⚠️ Esta mudança está com a lógica INVERTIDA.** Ver [BUG #1](#bug-1--botão-descartar-alterações-sempre-visível-lógica-invertida) abaixo.

Correção anterior desta documentação: uma versão prévia deste arquivo afirmava que a mudança
"mostra o botão Descartar apenas quando há mudanças". **Isso está errado** — o código faz o
oposto. A afirmação foi escrita sem execução do sistema e está corrigida aqui.

---

### 4. **view/index.html — Página de Visualização Pública Completa**

#### Mudanças Principais

**Antes:** Arquivo incompleto, apenas layout básico

**Agora:** Página funcional e completa com:

1. **Header com branding** (linhas 125-128)
   ```html
   <header class="kiosk-header">
     <div class="kiosk-header__brand">Organograma</div>
     <div class="kiosk-header__meta">Visualização pública</div>
   </header>
   ```

2. **Estilos CSS Variables** (linhas 8-16)
   ```css
   :root {
     --bg: #081321;
     --panel: rgba(15, 23, 42, 0.92);
     --text: #e2e8f0;
     --muted: #94a3b8;
     --accent: #38bdf8;
     --green: #22c55e;
   }
   ```

3. **Iframe para organograma** (linha 131)
   ```html
   <iframe class="kiosk-frame" src="/?view=1"></iframe>
   ```
   - Parâmetro `?view=1` ativa modo somente-leitura (READ_ONLY_MODE em tree.html)

4. **Desativação de Ações** (linhas 141-211)
   ```javascript
   function desativarAcoes() {
     // Remove toolbar, sidebar, editor, botões
     // Desabilita funções de edição no iframe
     // Esconde elementes de interação
   }
   ```

5. **Botão Sair** (linhas 133-134, 214-216)
   - Permite sair do modo visualização pública
   - Volta para a página principal

---

## ✅ Validação de Integridade

### Arquivos Verificados
- ✓ Arquivo `misc/organograma-completo.csv` existe (81.7 KB)
- ✓ Função `valorCampo` definida na linha 493
- ✓ Função usada em 20+ locais no código
- ✓ Variável `READ_ONLY_MODE` definida na linha 377
- ✓ Função `marcarAlterado` definida na linha 2557
- ✓ Todas as referências são consistentes

### Dependências
- d3.csv (já incluído no projeto)
- Nenhuma nova dependência adicionada
- Compatível com Node.js puro

### Estrutura de Dados
```
tree.html
├── função valorCampo (linha 493)
├── função temFoto (linha 515) — usa valorCampo
├── função normalizar (linha 526) — usa valorCampo
├── inicialização (linha 2574+)
│   ├── carregamento do servidor
│   └── carregamento de CSV com BOM fix
├── editor (linha 2808+)
│   └── usa valorCampo para preenchimento
└── exportação (linhas 2067+)
    └── usa valorCampo para leitura

view/index.html
└── Página kiosk completa com iframe
```

---

## 🚀 Instruções para Deployment

### Via Docker (Recomendado)

```bash
cd /mnt/c/Users/40446686808/projetos/organograma

# Build e subida
docker compose up -d --build

# Verificar status
docker compose ps

# Logs
docker compose logs --tail=50 orgchart

# Teste de saúde
curl http://localhost:8085/api/saude
```

### URLs de Acesso

- **Editor completo (localhost)**: http://localhost:8085
- **Visualização pública**: http://localhost:8085/view/
- **API de saúde**: http://localhost:8085/api/saude

### Rede (WSL)
- **IP Local**: http://192.168.0.218:8085
- **Acesso remoto**: Mesmo IP, mesmas URLs

---

## 🧪 Testes Recomendados (Após Deploy)

1. **Importação CSV com diferentes nomes de campos**
   - Testar com `nome` e `name`
   - Testar com `foto`, `image`, `photo`
   - Testar com `cargo`, `position`, `title`

2. **Verificar remoção de BOM**
   - Exportar CSV do Excel com UTF-8 BOM
   - Importar novamente
   - Verificar se campos são identificados corretamente

3. **Modo Visualização Pública**
   - Abrir http://localhost:8085/view/
   - Verificar se toolbar está oculta
   - Verificar se botões de edição estão desabilitados
   - Clicar em "Sair da visualização" e voltar

4. **Marcação de Dados Iniciais**
   - Verificar se botão "Descartar" apareça após mudanças
   - Clicar em "Descartar" e confirmar reset

---

## 📝 Notas Técnicas

### Por que valorCampo é genérica
A função suporta qualquer combinação de nomes de campos:
```javascript
valorCampo(row, "name")           // Procura: name, name, name, name, name
valorCampo(row, "firstName")      // Procura: firstName, firstname, firstname, first_name, first-name
valorCampo(row, "employeeName")   // Procura: employeeName, employeename, employeename, employee_name, employee-name
```

### Por que diferentes CSV precisam ser suportados
- Cada prefeitura/órgão exporta de forma diferente
- Planilhas herdadas têm nomes em português
- Sistemas integrados podem ter nomes em inglês
- Manter só um padrão criaria "gotchas" para usuários

### Performance
- Função `valorCampo` é chamada apenas na inicialização e edição (não em tempo real)
- Busca genérica é O(n) por campo, mas n é pequeno (máx 30 variações)
- Sem impacto em performance

---

## 📌 Checklist para Agente

Se necessário reproduzir essas mudanças:

- [ ] Implementar função `valorCampo` na linha 493
- [ ] Usar `valorCampo` em todos os lugares onde se acessa campos de dados
- [ ] Mudar referência de `misc/data.csv` para `misc/organograma-completo.csv`
- [ ] Adicionar removedor de BOM UTF-8 no carregamento de CSV
- [ ] Adicionar lógica `marcarAlterado(true)` quando `corpo.inicial` é verdadeiro
- [ ] Completar arquivo `view/index.html` com página kiosk funcional
- [ ] Testar importação com múltiplos formatos de CSV
- [ ] Testar modo visualização pública (`/?view=1`)
- [ ] Commitar com mensagem descritiva

---

## ✨ Resultado Final

- ✅ Organograma agora aceita dados em múltiplos formatos
- ✅ Página de visualização pública funcional e completa
- ✅ Sem novas dependências
- ✅ Compatível com Docker
- ✅ Pronto para produção

**Próximas ações:** Deploy via Docker Compose na porta 8085.

---

# 🔴 VALIDAÇÃO EXECUTADA E BUGS ENCONTRADOS

**Data da execução**: 14 de Setembro de 2026
**Ambiente**: Docker 29.6.2 dentro do WSL Ubuntu
**Container**: `orgchart-demo` — `Up`, healthcheck `{"ok":true}` HTTP 200

> ⚠️ **Aviso sobre a seção anterior deste documento.** Tudo acima da linha
> "VALIDAÇÃO EXECUTADA" foi escrito por análise estática, **sem rodar o sistema**,
> e afirmava "100% validado / pronto para produção" indevidamente. A validação real
> só foi feita agora, e encontrou os bugs listados abaixo. Trate as seções anteriores
> como descrição do código, não como atestado de qualidade.

## ✅ O que foi verificado rodando de verdade

| Verificação | Resultado |
|---|---|
| `docker compose up -d --build` | ✅ Build e start OK |
| `GET /api/saude` | ✅ 200 `{"ok":true}` |
| `GET /` | ✅ 200 |
| `GET /api/organograma` | ✅ 200 — 643 linhas |
| `GET /view/` e `/view/index.html` | ✅ 200 |
| `GET /misc/organograma-completo.csv` | ✅ 200 |
| `GET /misc/data.csv` (referência antiga) | ✅ 404 — confirma que a troca do CSV era necessária |
| `GET /sidebar/sidebar.html` e `.css` | ✅ 200 |
| Todos os `build/*` (d3, org-chart, jspdf, html2canvas, fontawesome…) | ✅ 200, nenhum 404 |
| Acesso do **Windows** a `127.0.0.1:8085` | ✅ TCP OK + HTTP `{"ok":true}` |
| Acesso do **Windows** a `192.168.0.218:8085` | ❌ **TCP recusado** — ver BUG #2 |

Observação: um teste inicial via `Invoke-WebRequest` deu timeout, mas a causa era o
**proxy do sistema no PowerShell**, não a aplicação. Com `WebClient.Proxy = $null`
o acesso funciona normalmente.

---

## BUG #1 — Botão "Descartar alterações" sempre visível (lógica invertida)

**Severidade**: Média — não corrompe dados, mas oferece uma ação destrutiva sem motivo.

### Diagnóstico

No `server.js`, a função `lerArquivo()` (linha ~139) funciona assim:

- Se `/dados/organograma.json` **existe** (usuário já editou) → retorna **sem** `inicial`.
- Se **não existe** (ENOENT) → cai no arquivo de fábrica e retorna `inicial: true` (linha 147).

Portanto: **`inicial: true` significa "NÃO há edições do usuário"** — ou seja, não há
absolutamente nada para descartar.

Mas em `tree.html`, `marcarAlterado(true)` **mostra** o botão:

```javascript
function marcarAlterado(alterado) {      // linha 2557
  const btn = document.getElementById("btn-descartar");
  if (btn) btn.hidden = !alterado;       // true => hidden = false => VISÍVEL
}
```

O botão nasce `hidden` no HTML (linha 227-231). Os pontos que o revelam:

| Linha | Contexto | Correto? |
|---|---|---|
| 2496 | Após conflito 409 (servidor tinha versão mais nova) | ✅ Sim |
| 2513 | Após salvar com sucesso | ✅ Sim |
| **2536** | **NOVO — quando `corpo.inicial` é true** | ❌ **Invertido** |
| **2590** | **Após qualquer carga do servidor, incondicional** | ❌ **Sempre dispara** |

**Efeito observável**: sempre que o servidor responde, o botão vermelho
"Descartar alterações" aparece — inclusive num organograma de fábrica intocado.
Clicar nele dispara um `confirm()` alarmante ("Isto afeta todo mundo que abrir esta página")
e um `DELETE /api/organograma` para apagar alterações que não existem.

A linha 2536 nova não corrigiu nada: a 2590 já mostrava o botão incondicionalmente,
e a 2536 reforça o comportamento errado de forma explícita.

**Estado atual no servidor**: o volume `orgchart-dados` já contém
`/dados/organograma.json` (176 KB, de 11/09), então `inicial` **não** vem na resposta hoje
e a linha 2536 está dormente. O bug aparece num volume novo (`docker compose down -v`)
ou após clicar em "Descartar".

### Passo a passo da correção

1. Abrir `tree.html`.
2. Ir até a função `carregarDoServidor()`, por volta da **linha 2528**.
3. **Remover** o bloco novo (linhas 2534-2537):
   ```javascript
   // Se o servidor está usando dados iniciais (arquivo de fábrica), marcar como alterado
   if (corpo.inicial) {
    marcarAlterado(true);
   }
   ```
4. Fazer a função devolver também o flag, para quem chamou decidir. Trocar o `return`:
   ```javascript
   // antes
   return corpo.linhas;
   // depois
   inicialServidor = Boolean(corpo.inicial);
   return corpo.linhas;
   ```
   Declarar `var inicialServidor = false;` junto das outras variáveis de estado
   (perto de `versaoServidor`).
5. Ir até a **linha ~2590**, dentro do bloco de inicialização:
   ```javascript
   const salvas = await carregarDoServidor();
   if (salvas) {
    marcarAlterado(true);          // ← trocar esta linha
   ```
   Trocar por:
   ```javascript
   marcarAlterado(!inicialServidor);
   ```
6. **Não mexer** nas linhas 2496 e 2513 — aquelas estão corretas.
7. Rebuild: `docker compose up -d --build`.

### Como testar a correção

```bash
# 1) Zerar o volume para forçar o estado "de fábrica"
docker compose down -v
docker compose up -d --build

# 2) Abrir http://localhost:8085
#    ESPERADO: botão "Descartar alterações" NÃO aparece

# 3) Editar qualquer card (duplo clique) e salvar
#    ESPERADO: botão "Descartar alterações" PASSA a aparecer

# 4) Recarregar a página (F5)
#    ESPERADO: botão continua aparecendo (agora há edições reais)
```

⚠️ **Atenção**: `docker compose down -v` **apaga os dados editados**. Exportar CSV/JSON antes.

---

## BUG #2 — README documenta uma URL de rede que não funciona

**Severidade**: Baixa — documentação, não código.

### Diagnóstico

O `README.md` (linhas 9-13) afirma:

```text
Na maquina atual, o servico esta configurado para WSL com rede espelhada e porta 8085:
http://192.168.0.218:8085
```

Mas o `docker-compose.yml` (linha 18) publica a porta assim:

```yaml
ports:
  - "127.0.0.1:8085:8085"
```

O prefixo `127.0.0.1:` prende a porta ao **loopback**. Confirmado por medição:

- `ss -ltn` dentro do WSL: `LISTEN 127.0.0.1:8085`
- `Test-NetConnection 127.0.0.1 -Port 8085` → **True**
- `Test-NetConnection 192.168.0.218 -Port 8085` → **False**

O IP `192.168.0.218` existe (é o IP do WSL com rede espelhada), mas **nada escuta nele**.
Ou seja: ninguém na rede local consegue abrir o organograma pela URL documentada.

### Passo a passo da correção

Há **duas** saídas. Escolher conforme a intenção — **perguntar ao usuário antes**, porque
uma delas expõe o serviço para a rede inteira.

**Opção A — manter o acesso restrito (mais seguro) e corrigir o README:**

1. Abrir `README.md`.
2. Na seção "## Acesso" (linhas 7-19), remover o bloco que cita `http://192.168.0.218:8085`
   e deixar apenas `http://localhost:8085`.
3. Na seção "Teste de saude" (linha 32), trocar
   `curl -fsS http://192.168.0.218:8085/api/saude` por
   `curl -fsS http://localhost:8085/api/saude`.
4. Nenhum rebuild necessário (só documentação).

**Opção B — realmente expor na rede local:**

1. Abrir `docker-compose.yml`.
2. Trocar a linha 18:
   ```yaml
   # antes
   - "127.0.0.1:8085:8085"
   # depois
   - "8085:8085"
   ```
3. `docker compose up -d --build`
4. Validar de outra máquina da rede: `curl http://192.168.0.218:8085/api/saude`
5. ⚠️ **Implicação de segurança**: a API tem `POST` e `DELETE` **sem autenticação
   nenhuma**. Expor na rede significa que qualquer pessoa no mesmo Wi-Fi pode apagar
   ou reescrever o organograma inteiro. Só fazer isso com autenticação na frente
   (o `.env` cita uma stack `hub-login` — provavelmente é ali que isso deve entrar).

---

## BUG #3 — Comentário contradiz o código (limpeza de foto)

**Severidade**: Baixa — não altera comportamento, mas engana quem for manter o código.

### Diagnóstico

Em `tree.html`, por volta da **linha 3056**, dentro de `salvarEditor()`:

```javascript
if (valores.image) {
 row.image = valores.image;
 row.imageUrl = valores.image;
} else {
 // Preserve existing image if user cleared the field intentionally
 // row.image and row.imageUrl keep their previous values unless explicitly set to empty
 // Only clear if the field was genuinely empty (user removed photo)
 row.image = "";
 row.imageUrl = "";
}
```

Os três comentários dizem que a foto **é preservada**. O código logo abaixo **apaga**
`image` e `imageUrl` incondicionalmente. O `git diff` confirma que **só os comentários
mudaram** — o comportamento é idêntico ao de antes. Alguém escreveu a intenção mas não
implementou.

### Passo a passo da correção

Decidir qual das duas é a intenção real — **perguntar ao usuário**:

**Se o comportamento atual (apagar) está certo** → corrigir só o comentário:

1. Abrir `tree.html`, linha ~3059.
2. Substituir os três comentários por um só, verdadeiro:
   ```javascript
   } else {
    // Campo de imagem vazio: remove a foto do card.
    row.image = "";
    row.imageUrl = "";
   }
   ```

**Se a intenção era preservar a foto** → implementar de fato:

1. Abrir `tree.html`, linha ~3056.
2. Trocar o bloco `else` inteiro por:
   ```javascript
   } else {
    // Campo vazio não apaga a foto existente; para remover, usar "Limpar foto".
   }
   ```
3. Garantir que o botão "Limpar foto" (`limparFoto()`) continue zerando os dois campos —
   senão não haverá mais nenhuma forma de remover uma foto pela interface.
4. Rebuild e testar: editar um card com foto, apagar o texto do campo de imagem, salvar,
   e conferir se a foto continua no card.

---

## 📋 Resumo para o próximo agente

| # | Bug | Arquivo | Linhas | Precisa perguntar ao usuário? |
|---|---|---|---|---|
| 1 | Botão "Descartar" sempre visível (lógica invertida) | `tree.html` | 2534-2537, 2590 | Não — correção é objetiva |
| 2 | README cita URL de rede que não responde | `README.md` / `docker-compose.yml` | 9-13, 32 / 18 | **Sim** — Opção A ou B (B tem risco de segurança) |
| 3 | Comentário contradiz o código da foto | `tree.html` | ~3056-3064 | **Sim** — qual é a intenção real |

**Nenhum destes bugs impede o uso do sistema hoje.** O organograma está no ar,
servindo 643 linhas, com todos os assets carregando. São defeitos de acabamento.

**Regra de ouro para esta base**: corrigir o defeito pedido e parar. Não mexer em
cor, estilo ou layout sem pedido explícito do usuário.
