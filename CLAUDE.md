# cora-site

Site institucional da Cora, `acora.com.br`, e as páginas legais (Termos de
Uso e Política de Privacidade). HTML estático, sem bundler e sem
`package.json`. O `tools/legal/build.py` gera `termos.html` e
`privacidade.html` a partir do markdown. A fonte editorial dos Termos e da
Política é o Notion (página Jurídico): o markdown daqui é cópia da versão
marcada lá.

## Ao abrir a sessão, antes de qualquer coisa

1. Sincronizar a skill `cora-dev`. A fonte é a `main` remota do
   `cora-business`, nunca o working tree dele. A comparação é por conteúdo,
   não por data:

   ```bash
   git -C ../cora-business fetch -q origin main &&
   git -C ../cora-business show origin/main:skills/cora-dev/SKILL.md > /tmp/cora-dev-SKILL.md &&
   mkdir -p ~/.claude/skills/cora-dev &&
   { cmp -s /tmp/cora-dev-SKILL.md ~/.claude/skills/cora-dev/SKILL.md ||
     { cp /tmp/cora-dev-SKILL.md ~/.claude/skills/cora-dev/SKILL.md && echo "skill cora-dev atualizada"; }; }
   ```

   Se aparecer "skill cora-dev atualizada", avise o Hugo numa linha. Se
   qualquer comando falhar, pare e avise: não trabalhe sem a skill.

2. Carregar a skill `cora-dev` e seguir o que ela diz.

## Regras duras

- **Schema não se altera aqui.** Migration só no `cora-backoffice`. Se a
  tarefa pedir mudança de schema, pare e avise.
- Conferir a branch **antes de escrever qualquer arquivo** (`git status -sb`),
  não só antes de commitar. Nunca commitar na `main`.
- Uma frente, uma branch, uma sessão.
- Commits em ASCII, sem acento.
- Nenhum CPF, e-mail ou telefone em código, teste, commit ou PR. Dado de
  teste é sintético.
- Nunca mergear. O Hugo faz squash pela interface quando decidir.
- Depois do merge, apagar a branch local (`git branch -D`).

- **Âncora de cláusula não se reaproveita.** Ao renumerar, número antigo não
  recebe conteúdo novo: link antigo abriria a cláusula errada.

## Antes de abrir o PR

Regerar as páginas e conferir, na raiz do repo:

```bash
python3 tools/legal/build.py && python3 tools/legal/check.py
```

Depois, conferir que a versão de teste da Vercel terminou como READY e pôr o
link dela na descrição do PR.

## Deploy no ar

Este site não tem arquivo `.js` com nome variável. O sinal de que a versão
nova entrou no ar é um trecho do conteúdo novo aparecer na página publicada:

```bash
curl -s https://www.acora.com.br/ | grep -c 'trecho-do-conteudo-novo'
```

Se não aparecer depois do merge, avise a conversa do claude.ai, que confere e
coloca a versão no ar pela conexão com a Vercel.
