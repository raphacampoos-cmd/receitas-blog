#!/usr/bin/env python3
"""
Gerador estático do blog de receitas.

Lê os arquivos Markdown em content/receitas/ e content/paginas/, renderiza os
templates Jinja2 e escreve o site pronto em docs/ (pasta usada pelo GitHub
Pages ao servir "main /docs").

Uso:
    python3 build.py
"""
import json
import re
import shutil
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader

sys.path.insert(0, str(Path(__file__).parent))
from site_config import SITE

ROOT = Path(__file__).parent
CONTENT_RECEITAS = ROOT / "content" / "receitas"
CONTENT_PAGINAS = ROOT / "content" / "paginas"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUT = ROOT / "docs"

env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=False)

# "base" é o caminho da URL sem domínio (ex: "/receitas-blog" para páginas de
# projeto do GitHub Pages, ou "" para um domínio próprio na raiz). Calculado
# automaticamente para nunca ficar dessincronizado de SITE["url"].
SITE["url"] = SITE["url"].rstrip("/")
SITE["base"] = urlparse(SITE["url"]).path.rstrip("/")


def slugificar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    texto = texto.lower().strip()
    texto = re.sub(r"[^a-z0-9]+", "-", texto).strip("-")
    return texto


def ler_frontmatter(caminho: Path):
    texto = caminho.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        raise ValueError(f"{caminho} não tem front matter YAML")
    _, fm, corpo = texto.split("---", 2)
    dados = yaml.safe_load(fm)
    dados["corpo_md"] = corpo.strip()
    return dados


def normalizar_ingredientes(ingredientes):
    """Aceita tanto uma lista simples de strings quanto uma lista agrupada
    ([{"grupo": "Massa", "itens": [...]}, ...]) e sempre devolve o formato
    agrupado, para o template poder tratar os dois casos da mesma forma."""
    if not ingredientes:
        return []
    if isinstance(ingredientes[0], dict):
        return ingredientes
    return [{"grupo": None, "itens": ingredientes}]


def ingredientes_flat(ingredientes_agrupados):
    """Lista simples de ingredientes (para o Schema.org, que não usa grupos)."""
    itens = []
    for grupo in ingredientes_agrupados:
        itens.extend(grupo.get("itens", []))
    return itens


def carregar_receitas():
    receitas = []
    for arquivo in sorted(CONTENT_RECEITAS.glob("*.md")):
        dados = ler_frontmatter(arquivo)
        obrigatorios = [
            "title", "slug", "data_publicacao", "categoria", "tempo_preparo",
            "porcoes", "dificuldade", "resumo", "ingredientes", "modo_preparo",
        ]
        faltando = [c for c in obrigatorios if c not in dados or dados[c] in (None, "")]
        if faltando:
            raise ValueError(f"{arquivo.name}: faltam campos {faltando}")
        dados["ingredientes"] = normalizar_ingredientes(dados["ingredientes"])
        dados["categoria_slug"] = slugificar(dados["categoria"])
        receitas.append(dados)
    # mais recente primeiro
    receitas.sort(key=lambda r: r["data_publicacao"], reverse=True)
    return receitas


def montar_categorias(receitas):
    """Agrupa receitas por categoria, preservando a ordem de primeira aparição
    (mais recente primeiro, já que `receitas` já vem ordenada assim)."""
    categorias = {}
    for r in receitas:
        cat = r["categoria"]
        categorias.setdefault(cat, {"nome": cat, "slug": r["categoria_slug"], "receitas": []})
        categorias[cat]["receitas"].append(r)
    return list(categorias.values())


def relacionadas(receita, todas, maximo=3):
    mesma_categoria = [r for r in todas if r is not receita and r["categoria"] == receita["categoria"]]
    outras = [r for r in todas if r is not receita and r["categoria"] != receita["categoria"]]
    return (mesma_categoria + outras)[:maximo]


def schema_recipe(r):
    schema = {
        "@context": "https://schema.org/",
        "@type": "Recipe",
        "name": r["title"],
        "description": r["resumo"],
        "datePublished": str(r["data_publicacao"]),
        "recipeCategory": r.get("categoria"),
        "recipeYield": r.get("porcoes"),
        "totalTime": _iso_duration(r.get("tempo_preparo", "")),
        "recipeIngredient": ingredientes_flat(r.get("ingredientes", [])),
        "recipeInstructions": [
            {"@type": "HowToStep", "text": passo} for passo in r.get("modo_preparo", [])
        ],
    }
    return json.dumps(schema, ensure_ascii=False, indent=2)


def _iso_duration(texto_tempo: str) -> str:
    """Converte algo como '20 minutos' ou '1 hora' em PT20M / PT1H (best effort)."""
    numeros = "".join(c for c in texto_tempo if c.isdigit())
    if not numeros:
        return "PT20M"
    minutos = int(numeros)
    if "hora" in texto_tempo.lower():
        minutos *= 60
    return f"PT{minutos}M"


def carregar_paginas():
    paginas = []
    for arquivo in sorted(CONTENT_PAGINAS.glob("*.md")):
        dados = ler_frontmatter(arquivo)
        dados["conteudo_html"] = markdown.markdown(dados["corpo_md"])
        dados["arquivo_saida"] = arquivo.stem + ".html"
        paginas.append(dados)
    return paginas


def contexto_base(caminho: str, titulo: str, descricao: str, categorias=None):
    return {
        "site": SITE,
        "caminho": caminho,
        "titulo_pagina": titulo,
        "descricao_pagina": descricao,
        "ano_atual": datetime.now().year,
        "categorias_nav": categorias or [],
    }


def build():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    # assets estáticos
    shutil.copytree(STATIC, OUT / "static")

    receitas = carregar_receitas()
    paginas = carregar_paginas()
    categorias = montar_categorias(receitas)
    # ordena o menu de categorias por número de receitas (mais populosas primeiro)
    categorias_nav = sorted(categorias, key=lambda c: len(c["receitas"]), reverse=True)

    # index
    tpl = env.get_template("index.html")
    ctx = contexto_base("/", SITE["nome"], SITE["descricao"], categorias_nav)
    ctx["receitas"] = receitas
    ctx["destaque"] = receitas[0] if receitas else None
    (OUT / "index.html").write_text(tpl.render(**ctx), encoding="utf-8")

    # receitas
    (OUT / "receitas").mkdir(exist_ok=True)
    tpl_receita = env.get_template("receita.html")
    for r in receitas:
        r["conteudo_html"] = markdown.markdown(r["corpo_md"]) if r.get("corpo_md") else ""
        ctx = contexto_base(
            f"/receitas/{r['slug']}.html",
            r["title"],
            r["resumo"],
            categorias_nav,
        )
        ctx["r"] = r
        ctx["schema_json"] = schema_recipe(r)
        ctx["relacionadas"] = relacionadas(r, receitas)
        html = tpl_receita.render(**ctx)
        (OUT / "receitas" / f"{r['slug']}.html").write_text(html, encoding="utf-8")

    # páginas de categoria
    (OUT / "categorias").mkdir(exist_ok=True)
    tpl_categoria = env.get_template("categoria.html")
    for cat in categorias:
        ctx = contexto_base(
            f"/categorias/{cat['slug']}.html",
            cat["nome"],
            f"Receitas de {cat['nome'].lower()} — {SITE['nome']}.",
            categorias_nav,
        )
        ctx["categoria"] = cat
        ctx["receitas"] = cat["receitas"]
        html = tpl_categoria.render(**ctx)
        (OUT / "categorias" / f"{cat['slug']}.html").write_text(html, encoding="utf-8")

    # páginas institucionais
    tpl_pagina = env.get_template("pagina.html")
    for p in paginas:
        ctx = contexto_base(
            f"/{p['arquivo_saida']}", p["title"], p.get("resumo", SITE["descricao"]), categorias_nav
        )
        ctx["conteudo_html"] = p["conteudo_html"]
        html = tpl_pagina.render(**ctx)
        (OUT / p["arquivo_saida"]).write_text(html, encoding="utf-8")

    # índice de busca (usado pelo campo de busca client-side na home)
    indice_busca = [
        {
            "title": r["title"],
            "slug": r["slug"],
            "resumo": r["resumo"],
            "categoria": r["categoria"],
            "emoji": r.get("emoji", "🍽️"),
        }
        for r in receitas
    ]
    (OUT / "static" / "busca.json").write_text(
        json.dumps(indice_busca, ensure_ascii=False), encoding="utf-8"
    )

    # sitemap.xml
    urls = [SITE["url"] + "/"]
    urls += [f"{SITE['url']}/receitas/{r['slug']}.html" for r in receitas]
    urls += [f"{SITE['url']}/categorias/{c['slug']}.html" for c in categorias]
    urls += [f"{SITE['url']}/{p['arquivo_saida']}" for p in paginas]
    sitemap = ['<?xml version="1.0" encoding="UTF-8"?>',
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        sitemap.append(f"  <url><loc>{u}</loc></url>")
    sitemap.append("</urlset>")
    (OUT / "sitemap.xml").write_text("\n".join(sitemap), encoding="utf-8")

    # robots.txt
    (OUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE['url']}/sitemap.xml\n",
        encoding="utf-8",
    )

    # rss.xml (simples)
    rss_items = []
    for r in receitas[:20]:
        link = f"{SITE['url']}/receitas/{r['slug']}.html"
        rss_items.append(
            f"<item><title>{r['title']}</title><link>{link}</link>"
            f"<guid>{link}</guid><description>{r['resumo']}</description></item>"
        )
    rss = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<rss version="2.0"><channel>'
        f"<title>{SITE['nome']}</title><link>{SITE['url']}</link>"
        f"<description>{SITE['descricao']}</description>"
        + "".join(rss_items)
        + "</channel></rss>"
    )
    (OUT / "rss.xml").write_text(rss, encoding="utf-8")

    # .nojekyll evita que o GitHub Pages tente processar como Jekyll
    (OUT / ".nojekyll").write_text("", encoding="utf-8")

    print(
        f"Build concluído: {len(receitas)} receitas, {len(categorias)} categorias, "
        f"{len(paginas)} páginas -> {OUT}"
    )


if __name__ == "__main__":
    build()
