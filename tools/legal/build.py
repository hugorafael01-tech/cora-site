#!/usr/bin/env python3
"""Gera termos.html e privacidade.html a partir dos markdowns desta pasta.

Uso (na raiz do repo):  python3 tools/legal/build.py

Só Python 3 padrão, sem dependência. Suporta apenas o subconjunto de markdown
usado nos documentos legais: # e ## títulos, **negrito**, listas "- ",
tabelas, citação "> ", separador "---", parágrafos e parágrafos de cláusula
que começam com **N.N.** (viram <div id="N.N">).

O texto sai idêntico ao markdown. O HTML só acrescenta navegação: sumário,
âncoras e links sobre palavras que já existem no texto (make_linker).
Conferir sempre com tools/legal/check.py depois de gerar.
"""
import html
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent

PAGES = {
    "termos": {
        "md": "conteudo-termos.md",
        "title": "Termos de Uso — Cora",
        "description": "Termos de Uso da assinatura de pães de fermentação natural da Cora, com o Anexo I: preços, cobrança, entrega, pausa e cancelamento. {versao}, após revisão jurídica.",
        "other": ("/privacidade", "Política de Privacidade"),
    },
    "privacidade": {
        "md": "conteudo-privacidade.md",
        "title": "Política de Privacidade — Cora",
        "description": "Como a Cora coleta, usa, compartilha e protege os dados pessoais de quem assina, com base na LGPD. {versao}, em revisão jurídica.",
        "other": ("/termos", "Termos de Uso"),
    },
}

CLAUSE_RE = re.compile(r"^\*\*(\d+\.\d+(?:-[A-Z])?)\.\*\*\s*")
SECTION_RE = re.compile(r"^(\d+)\.\s+(.*)$")
ANNEX_SECTION_RE = re.compile(r"^([A-Z])\.\s+(.*)$")


def slug_annex(title):
    # "Anexo I — Regras da Assinatura" -> "anexo-i"
    m = re.match(r"Anexo\s+([IVX]+)", title)
    return "anexo-" + m.group(1).lower()


def make_linker(page):
    """Links sobre referências no texto, sem alterar nenhuma palavra."""
    parts = [
        r"(?P<email>[\w.]+@acora\.com\.br)",
        r"(?P<portal>app\.acora\.com\.br)",
        r"(?P<termosurl>acora\.com\.br/termos)",
        r"(?P<privurl>acora\.com\.br/privacidade)",
        r"(?P<site>(?<![\w@.])acora\.com\.br)",
        r"(?P<clausula>cláusula (?P<cnum>\d+(?:\.\d+)?(?:-[A-Z])?))",
        r"(?P<politica>Política de Privacidade)",
        r"(?P<anexo>Anexo I\b)",
    ]
    if page == "privacidade":
        parts += [r"(?P<termos>Termos de Uso)", r"(?P<secao>seção (?P<snum>\d+))"]
    rx = re.compile("|".join(parts))

    termos_prefix = "" if page == "termos" else "/termos"

    def sub(m):
        t = m.group(0)
        if m.group("email"):
            href = "mailto:" + t
        elif m.group("portal"):
            href = "https://app.acora.com.br"
        elif m.group("termosurl"):
            href = "/termos"
        elif m.group("privurl"):
            href = "/privacidade"
        elif m.group("site"):
            href = "/"
        elif m.group("clausula"):
            href = f"{termos_prefix}#{m.group('cnum')}"
        elif m.group("politica"):
            if page == "privacidade":
                return t
            href = "/privacidade"
        elif m.group("anexo"):
            href = f"{termos_prefix}#anexo-i"
        elif page == "privacidade" and m.group("termos"):
            href = "/termos"
        elif page == "privacidade" and m.group("secao"):
            href = f"#{m.group('snum')}"
        else:
            return t
        return f'<a href="{href}">{t}</a>'

    return lambda s: rx.sub(sub, s)


def inline(text, linker, link=True):
    s = html.escape(text, quote=False)
    # links antes do negrito: o regex não pode casar dentro de tags geradas
    if link:
        s = linker(s)
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)


def strip_md(text):
    return re.sub(r"\*\*(.+?)\*\*", r"\1", text)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md, page):
    linker = make_linker(page)
    lines = md.splitlines()
    out = []
    toc = []  # (id, num, título, filhos)
    title = meta = annex_meta = annex_id = None
    in_annex = False
    state = {"clause": False, "section": False, "subsection": False}

    def close(*levels):
        for level in ("clause", "subsection", "section"):
            if state[level]:
                out.append("</div>" if level == "clause" else "</section>")
                state[level] = False
            if level == levels[0]:
                break

    def next_nonblank(i):
        j = i + 1
        while not lines[j].strip():
            j += 1
        return j

    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            i += 1
            continue

        if line.startswith("# "):
            h = line[2:].strip()
            j = next_nonblank(i)
            if title is None:
                title, meta = h, strip_md(lines[j].strip())
            else:
                # Anexo
                close("section")
                in_annex = True
                annex_id = slug_annex(h)
                annex_meta = strip_md(lines[j].strip())
                out.append(f'<section class="annex" id="{annex_id}">')
                out.append(f'<h2 class="heading annex-title">{html.escape(h)}</h2>')
                out.append(f'<p class="doc-meta">{html.escape(annex_meta)}</p>')
                toc.append((annex_id, "", h, []))
                state["section"] = True
            i = j + 1
            continue

        if line.startswith("## "):
            h = line[3:].strip()
            if in_annex:
                close("subsection")
                m = ANNEX_SECTION_RE.match(h)
                sid = f"{annex_id}-{m.group(1).lower()}"
                out.append(f'<section class="annex-section" id="{sid}">')
                out.append(
                    f'<h3 class="heading"><a class="sec-num" href="#{sid}">{m.group(1)}.</a> '
                    f"{inline(m.group(2), linker, link=False)}</h3>"
                )
                toc[-1][3].append((sid, m.group(1), m.group(2)))
                state["subsection"] = True
            else:
                close("section")
                m = SECTION_RE.match(h)
                sid = m.group(1)
                out.append(f'<section class="doc-section" id="{sid}">')
                out.append(
                    f'<h2 class="heading"><a class="sec-num" href="#{sid}">{sid}.</a> '
                    f"{inline(m.group(2), linker, link=False)}</h2>"
                )
                toc.append((sid, sid, m.group(2), []))
                state["section"] = True
            i += 1
            continue

        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            header, body = rows[0], rows[2:]
            out.append('<div class="table-wrap"><table>')
            out.append("<thead><tr>" + "".join(f'<th scope="col">{inline(c, linker)}</th>' for c in header) + "</tr></thead>")
            out.append("<tbody>")
            for r in body:
                cells = "".join(
                    f'<td data-label="{html.escape(strip_md(header[k]))}">{inline(c, linker)}</td>'
                    for k, c in enumerate(r)
                )
                out.append(f"<tr>{cells}</tr>")
            out.append("</tbody></table></div>")
            continue

        if line.startswith("- "):
            out.append("<ul>")
            while i < len(lines) and lines[i].startswith("- "):
                out.append(f"<li>{inline(lines[i][2:].strip(), linker)}</li>")
                i += 1
            out.append("</ul>")
            continue

        if line.strip() == "---":
            # Separador: fecha a cláusula aberta para o que vem depois não ser
            # lido como parte dela (o fecho de contato, no fim dos Termos).
            close("clause")
            out.append("<hr>")
            i += 1
            continue

        if line.startswith("> "):
            out.append(f'<blockquote class="note"><p>{inline(line[2:].strip(), linker)}</p></blockquote>')
            i += 1
            continue

        m = CLAUSE_RE.match(line)
        if m:
            close("clause")
            cid = m.group(1)
            out.append(f'<div class="clause" id="{cid}">')
            out.append(f'<p><a class="clause-num" href="#{cid}">{cid}.</a> {inline(line[m.end():], linker)}</p>')
            state["clause"] = True
        else:
            out.append(f"<p>{inline(line.strip(), linker)}</p>")
        i += 1

    close("section")
    return title, meta, annex_meta, toc, "\n".join(out)


def render_toc(toc):
    items = []
    for sid, num, t, children in toc:
        if children:
            sub = "".join(
                f'<li><a href="#{cid}"><span class="toc-num">{cnum}.</span> {html.escape(ct)}</a></li>'
                for cid, cnum, ct in children
            )
            items.append(
                f'<li class="toc-annex"><a href="#{sid}">{html.escape(t)}</a><ol class="toc-sub">{sub}</ol></li>'
            )
        else:
            items.append(f'<li><a href="#{sid}"><span class="toc-num">{num}.</span> {html.escape(t)}</a></li>')
    return "\n".join(items)


def render(page):
    """Devolve o HTML final de uma página, sem gravar."""
    cfg = PAGES[page]
    md = (HERE / cfg["md"]).read_text(encoding="utf-8")
    template = (HERE / "template.html").read_text(encoding="utf-8")
    title, meta, annex_meta, toc, body = convert(md, page)

    # meta: "Cora · Versão 1.3 · 15/09/2026 · após revisão jurídica"
    # O status é o último campo e sai do próprio markdown: cada documento tem o
    # seu, porque a Política pode seguir em revisão enquanto os Termos já
    # voltaram do advogado.
    status = meta.rsplit(" · ", 1)[1]
    versao = re.search(r"Versão [\d.]+", meta).group(0)
    meta_html = html.escape(meta[: -len(status)]) + f'<span class="doc-status">{status}</span>'
    footer_meta = html.escape(title + " · " + meta.split(" · ", 1)[1])
    footer_meta = footer_meta.replace(status, f'<span class="doc-status">{status}</span>')
    if annex_meta:
        footer_meta += "<br>Anexo I · " + html.escape(annex_meta)

    return (
        template.replace("{{PAGE}}", page)
        .replace("{{TITLE}}", html.escape(cfg["title"]))
        .replace("{{DESCRIPTION}}", html.escape(cfg["description"].format(versao=versao)))
        .replace("{{H1}}", html.escape(title))
        .replace("{{META}}", meta_html)
        .replace("{{TOC}}", render_toc(toc))
        .replace("{{BODY}}", body)
        .replace("{{FOOTER_META}}", footer_meta)
        .replace("{{OTHER_HREF}}", cfg["other"][0])
        .replace("{{OTHER_LABEL}}", cfg["other"][1])
    )


def main():
    for page in PAGES:
        out = REPO / f"{page}.html"
        out.write_text(render(page), encoding="utf-8")
        ids = re.findall(r'<div class="clause" id="([^"]+)"', out.read_text(encoding="utf-8"))
        print(f"{out.name}: gerado ({len(ids)} cláusulas com âncora)")


if __name__ == "__main__":
    main()
