# Receita Rápida — Blog de Receitas

Blog estático de receitas rápidas e práticas, com publicação automática de
uma receita nova por dia via IA, pronto para monetização com Google AdSense.

- **Como publicar o site:** veja [DEPLOY.md](DEPLOY.md).
- **Regras de conteúdo das receitas:** veja [GUIA_DE_CONTEUDO.md](GUIA_DE_CONTEUDO.md).

## Estrutura do projeto

```
content/receitas/    → receitas em Markdown (1 arquivo por receita)
content/paginas/     → páginas institucionais (Sobre, Contato, Privacidade, Cookies)
templates/           → templates HTML (Jinja2)
static/              → CSS e imagens
scripts/gerar_receita.py → gera 1 receita nova via IA (Claude)
.github/workflows/   → automação diária (GitHub Actions)
build.py             → gera o site estático final na pasta docs/
site_config.py       → nome do site, URL e e-mail de contato
docs/                → site pronto (gerado automaticamente, não edite direto)
```

## Rodando localmente

```bash
pip install -r requirements.txt
python3 build.py
```

O site pronto fica em `docs/`. Para visualizar localmente:

```bash
cd docs && python3 -m http.server 8000
```

Depois acesse http://localhost:8000 no navegador.
