#!/usr/bin/env python3
"""
Gera UMA nova receita por dia usando a API da Anthropic (Claude) e salva o
arquivo Markdown em content/receitas/, seguindo exatamente o formato
descrito em GUIA_DE_CONTEUDO.md.

Requer a variável de ambiente ANTHROPIC_API_KEY (configurada como "secret"
no GitHub Actions).

Uso:
    python3 scripts/gerar_receita.py
"""
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

import requests
import yaml

ROOT = Path(__file__).parent.parent
CONTENT_RECEITAS = ROOT / "content" / "receitas"
GUIA = ROOT / "GUIA_DE_CONTEUDO.md"

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-4-5-20250929")

CATEGORIAS = [
    "Doces rápidos", "Salgados rápidos", "Lanches", "Sobremesas",
    "Pratos únicos", "Bebidas e sucos", "Café da manhã", "Massas",
    "Receitas fit", "Receitas com poucos ingredientes",
]


def receitas_existentes():
    titulos, slugs, categorias_recentes = [], set(), []
    arquivos = sorted(CONTENT_RECEITAS.glob("*.md"))
    for arquivo in arquivos:
        texto = arquivo.read_text(encoding="utf-8")
        fm = yaml.safe_load(texto.split("---")[1])
        titulos.append(fm["title"])
        slugs.add(fm["slug"])
        categorias_recentes.append(fm.get("categoria", ""))
    return titulos, slugs, categorias_recentes[-5:]


def escolher_categoria(categorias_recentes):
    for cat in CATEGORIAS:
        if cat not in categorias_recentes:
            return cat
    return CATEGORIAS[0]


def montar_prompt(guia_texto, titulos_existentes, categoria_sugerida):
    lista_titulos = "\n".join(f"- {t}" for t in titulos_existentes) or "(nenhuma ainda)"
    return f"""Você vai gerar UMA nova receita para um blog de receitas em português do Brasil.

Siga RIGOROSAMENTE o guia de conteúdo abaixo:

{guia_texto}

Categoria sugerida para hoje: {categoria_sugerida}
(pode escolher outra categoria da lista do guia se fizer mais sentido, mas prefira esta)

Receitas que JÁ EXISTEM no site (não repita o prato nem o título):
{lista_titulos}

Responda APENAS com um bloco de front matter YAML entre "---" seguido do
parágrafo de introdução, exatamente no formato de exemplo do guia
(campos: title, slug, data_publicacao, categoria, tempo_preparo, porcoes,
dificuldade, resumo, emoji, tags, ingredientes, modo_preparo, dicas).
Use a data de hoje: {date.today().isoformat()}.
Não inclua nenhum texto antes ou depois do bloco (sem comentários, sem
markdown de código, sem explicações)."""


def chamar_claude(prompt):
    if not API_KEY:
        print("ERRO: variável ANTHROPIC_API_KEY não definida.", file=sys.stderr)
        sys.exit(1)
    resposta = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": MODEL,
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    return dados["content"][0]["text"].strip()


def extrair_front_matter(texto):
    texto = texto.strip()
    # remove blocos de código markdown, se a IA tiver adicionado por engano
    texto = re.sub(r"^```[a-zA-Z]*\n?", "", texto)
    texto = re.sub(r"\n?```$", "", texto)
    if not texto.startswith("---"):
        raise ValueError("Resposta da IA não começa com front matter YAML '---'")
    partes = texto.split("---", 2)
    if len(partes) < 3:
        raise ValueError("Front matter YAML incompleto na resposta da IA")
    fm = yaml.safe_load(partes[1])
    corpo = partes[2].strip()
    return fm, corpo, texto


def validar(fm, slugs_existentes):
    obrigatorios = [
        "title", "slug", "data_publicacao", "categoria", "tempo_preparo",
        "porcoes", "dificuldade", "resumo", "ingredientes", "modo_preparo",
    ]
    faltando = [c for c in obrigatorios if c not in fm or fm[c] in (None, "")]
    if faltando:
        raise ValueError(f"Campos obrigatórios faltando na receita gerada: {faltando}")
    if fm["slug"] in slugs_existentes:
        fm["slug"] = f"{fm['slug']}-{date.today().isoformat()}"


def main():
    guia_texto = GUIA.read_text(encoding="utf-8")
    titulos, slugs, categorias_recentes = receitas_existentes()
    categoria_sugerida = escolher_categoria(categorias_recentes)
    prompt = montar_prompt(guia_texto, titulos, categoria_sugerida)

    texto_gerado = chamar_claude(prompt)
    fm, corpo, texto_completo = extrair_front_matter(texto_gerado)
    validar(fm, slugs)

    nome_arquivo = f"{date.today().isoformat()}-{fm['slug']}.md"
    destino = CONTENT_RECEITAS / nome_arquivo

    # reconstrói o arquivo com front matter validado (para garantir YAML limpo)
    front_matter_yaml = yaml.dump(fm, allow_unicode=True, sort_keys=False)
    conteudo_final = f"---\n{front_matter_yaml}---\n\n{corpo}\n"
    destino.write_text(conteudo_final, encoding="utf-8")
    print(f"Nova receita criada: {destino}")


if __name__ == "__main__":
    main()
