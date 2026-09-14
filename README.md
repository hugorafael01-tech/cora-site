# cora-site

Site institucional da Cora em [www.acora.com.br](https://www.acora.com.br). HTML estático, sem build, publicado pela Vercel a partir da `main`.

| Caminho | Arquivo |
|---|---|
| `/` | `index.html` |
| `/termos` | `termos.html` (Termos de Uso + Anexo I) |
| `/privacidade` | `privacidade.html` (Política de Privacidade) |

As URLs sem `.html` vêm do `cleanUrls` no `vercel.json`.

## Texto legal: duas cópias, uma regra

O texto de `termos.html` e `privacidade.html` também existe no Notion, em *Cora / Jurídico — Termos e Política*, que é a fonte de verdade editorial.

**Mudança no texto legal toca os dois no mesmo dia.** Atualize a versão e a data no topo e no rodapé da página. Se a data do site divergir da do Notion, o site está errado sobre o contrato vigente.

**O markdown é a fonte; o HTML só acrescenta navegação.** O texto publicado é idêntico, palavra por palavra, ao markdown revisado. O HTML acrescenta apenas sumário, âncoras e links sobre palavras que já existem no texto ("cláusula 6.9" → `#6.9`, "Anexo I", "Política de Privacidade", e-mails, `app.acora.com.br`). Nenhuma palavra muda. Uma versão revisada (por exemplo, a devolvida pelo advogado) entra pelo markdown e o HTML é gerado de novo a partir dele. Não se edita o texto legal direto no HTML.

Os `id` de cláusula (`/termos#6.7`, `/termos#6.9-A`, `/termos#anexo-i-f`) e de seção (`/privacidade#4`) são citados em e-mails e conversas. Não renomear nem renumerar sem avisar quem já citou.
