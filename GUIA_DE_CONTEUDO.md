# Guia de Conteúdo — Blog de Receitas

Este documento define as regras fixas para **toda** receita publicada neste site,
seja escrita manualmente ou gerada automaticamente pela rotina diária
(`.github/workflows/daily-recipe.yml` + `scripts/gerar_receita.py`).
Qualquer IA ou pessoa que for escrever uma nova receita deve seguir este guia.

## Nicho e tom

- Receitas **rápidas e práticas do dia a dia**: poucos ingredientes, fáceis de
  encontrar, preparo em geral entre 10 e 40 minutos.
- Português do Brasil, tom simples e direto, como alguém explicando a receita
  para um amigo. Frases curtas. Sem enrolação.
- Público amplo: pessoas que querem cozinhar algo gostoso sem complicação
  (não é conteúdo "gourmet" nem técnico de chef).

## Regras fixas (nunca quebrar)

1. **Não inventar informações.** Não afirmar propriedades nutricionais,
   medicinais ou "milagrosas" que não sejam de conhecimento culinário básico.
2. **Nunca prometer emagrecimento, "detox", "queima de gordura" ou eliminação
   de toxinas.** Isso viola políticas de anúncios (AdSense) e pode ser
   informação falsa.
3. Não usar clickbait exagerado no título. O título deve descrever a receita
   de forma clara e atrativa, sem promessas irreais.
4. Toda receita deve ser **original** (escrita com as próprias palavras),
   nunca copiada de outro site.
5. Sempre incluir a frase de aviso: "As informações desta receita têm caráter
   informativo e não substituem orientação nutricional profissional."
6. Não repetir um título/prato já publicado — antes de gerar, checar os
   arquivos existentes em `content/receitas/`.

## Categorias (rotacionar entre elas)

`Doces rápidos`, `Salgados rápidos`, `Lanches`, `Sobremesas`, `Pratos únicos`,
`Bebidas e sucos`, `Café da manhã`, `Massas`, `Receitas fit` (sem promessas de
emagrecimento — apenas "leve"/"com menos ingrediente X"), `Receitas com
poucos ingredientes`.

## Estrutura obrigatória de cada receita (front matter YAML + corpo)

Cada receita é um arquivo `.md` em `content/receitas/AAAA-MM-DD-slug.md` com
este formato:

```yaml
---
title: "Nome da receita"
slug: "nome-da-receita"
data_publicacao: "2026-09-16"
categoria: "Doces rápidos"
tempo_preparo: "20 minutos"
porcoes: "4 porções"
dificuldade: "Fácil"
resumo: "Uma frase curta e apetitosa resumindo a receita (até 160 caracteres, funciona como meta description)."
emoji: "🍰"
tags: ["sobremesa", "rápida", "sem forno"]
ingredientes:
  - "2 xícaras de farinha de trigo"
  - "1 xícara de açúcar"
modo_preparo:
  - "Misture os ingredientes secos em uma tigela."
  - "Adicione os líquidos e mexa até obter uma massa homogênea."
dicas:
  - "Pode substituir o leite por bebida vegetal."
---

Para receitas com partes bem distintas (ex: massa e cobertura de um bolo),
`ingredientes` também pode vir agrupado em vez de uma lista simples:

```yaml
ingredientes:
  - grupo: "Massa"
    itens:
      - "2 xícaras de farinha de trigo"
  - grupo: "Cobertura"
    itens:
      - "1 xícara de chocolate em pó"
```

Use o formato simples (lista direta) na maioria dos casos — só agrupe quando
fizer sentido para a receita.

Um parágrafo curto de introdução (2 a 4 frases) contando o contexto da
receita — quando fazer, por que é prática, alguma curiosidade real. Não
precisa repetir os ingredientes aqui, isso já aparece na página.
```

## SEO

- `resumo`: usado como meta description — até 160 caracteres, com a palavra-
  chave principal da receita.
- `title`: incluir a palavra-chave principal (ex: "Bolo de Caneca de
  Chocolate" em vez de só "Bolo Rápido").
- Cada receita gera automaticamente dados estruturados Schema.org `Recipe`
  (feito pelo `build.py`) — não é preciso escrever isso manualmente.
- Evitar títulos duplicados ou muito parecidos com receitas já existentes.

## Ritmo de publicação

- 1 receita nova por dia (rotina automática), sempre em uma categoria
  diferente da publicada no dia anterior, para variar o conteúdo do site.
