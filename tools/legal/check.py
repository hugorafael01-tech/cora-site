#!/usr/bin/env python3
"""Confere termos.html e privacidade.html contra os markdowns desta pasta.

Uso (na raiz do repo):  python3 tools/legal/check.py

Sai com código 1 se qualquer conferência falhar:
1. HTML commitável = saída do build.py (ninguém editou o HTML à mão, nem
   esqueceu de gerar depois de mudar o markdown);
2. texto do HTML idêntico ao markdown, palavra por palavra;
3. mesma quantidade de trechos em negrito;
4. nenhum id de cláusula ou seção que existia no último commit sumiu
   (ids são citados em e-mails; sumir um id quebra link já enviado).
"""
import difflib
import html
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True  # não deixar __pycache__ no repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build  # noqa: E402

CLAUSE_MD_RE = re.compile(r"^\*\*\d+\.\d+(?:-[A-Z])?\.\*\*", re.M)


def html_words(page_html):
    main = page_html[page_html.index("<main"):page_html.index("</main>")]
    main = re.sub(r'<nav class="toc".*?</nav>', "", main, flags=re.S)  # sumário repete títulos
    main = re.sub(r"</?(a|strong|span)\b[^>]*>", "", main)  # inline: sem espaço
    return html.unescape(re.sub(r"<[^>]+>", " ", main)).split()


def md_words(md):
    md = re.sub(r"^\|[-|]+\|$", "", md, flags=re.M)
    md = re.sub(r"^(#+ |- |> )", "", md, flags=re.M)
    return md.replace("**", "").replace("|", " ").split()


def ids(page_html):
    return set(re.findall(r'<(?:div|section) class="[^"]*" id="([^"]+)"', page_html))


def ids_no_ultimo_commit(name):
    try:
        old = subprocess.run(
            ["git", "show", f"HEAD:{name}"], cwd=build.REPO, capture_output=True, text=True, check=True
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None
    return ids(old)


def check(page):
    problems = []
    name = f"{page}.html"
    current = (build.REPO / name).read_text(encoding="utf-8")
    md = (build.HERE / build.PAGES[page]["md"]).read_text(encoding="utf-8")

    if current != build.render(page):
        problems.append(f"{name} difere da saída do build.py: rode python3 tools/legal/build.py (e não edite o HTML à mão)")

    mw, hw = md_words(md), html_words(current)
    if mw != hw:
        diff = list(difflib.unified_diff(mw, hw, "markdown", name, lineterm="", n=3))
        problems.append("texto diferente do markdown:\n    " + "\n    ".join(diff[:40]))

    md_bold = len(re.findall(r"\*\*(.+?)\*\*", md)) - len(CLAUSE_MD_RE.findall(md)) - md.count("\n# ") - 1
    main = current[current.index("<main"):current.index("</main>")]
    if md_bold != main.count("<strong>"):
        problems.append(f"negritos: markdown {md_bold}, HTML {main.count('<strong>')}")

    old_ids = ids_no_ultimo_commit(name)
    if old_ids:
        gone = sorted(old_ids - ids(current))
        if gone:
            problems.append("ids que existiam no último commit e sumiram: " + ", ".join(gone))

    print(f"{name}: {len(hw)} palavras, {len(ids(current))} âncoras -> " + ("OK" if not problems else "FALHOU"))
    for p in problems:
        print("  - " + p)
    return not problems


if __name__ == "__main__":
    ok = all([check(page) for page in build.PAGES])
    sys.exit(0 if ok else 1)
