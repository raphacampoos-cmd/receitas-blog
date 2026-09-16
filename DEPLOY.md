# Como publicar o site (passo a passo)

Este projeto já está pronto: 10 receitas, todas as páginas, CSS e a
automação diária. Falta só publicar. Recomendo o **GitHub Pages**, porque é
gratuito, confiável e funciona muito bem com AdSense.

## 1. Criar conta no GitHub (se ainda não tiver)

Acesse https://github.com/signup e crie uma conta gratuita.

## 2. Criar o repositório

1. No GitHub, clique em **New repository**.
2. Nome sugerido: `receitas-blog` (pode ser outro nome).
3. Deixe como **Public** (necessário para GitHub Pages gratuito).
4. Não marque nenhuma opção de inicializar com README — vamos enviar os
   arquivos que já estão prontos.

## 3. Enviar os arquivos deste projeto para o repositório

No seu computador, com a pasta deste projeto (`receitas-blog/`) baixada:

```bash
cd receitas-blog
git init
git add .
git commit -m "Site inicial do blog de receitas"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/receitas-blog.git
git push -u origin main
```

Troque `SEU-USUARIO` pelo seu nome de usuário do GitHub.

## 4. Ajustar a configuração do site

Abra `site_config.py` e troque a `url` pelo endereço real que o site vai
ter, por exemplo:

```python
"url": "https://SEU-USUARIO.github.io/receitas-blog",
```

Depois rode `python3 build.py` de novo e suba a alteração (`git add`,
`git commit`, `git push`) — ou deixe que a automação diária já cuide disso
na próxima execução.

Também edite:
- `content/paginas/contato.md` — coloque seu e-mail de verdade.
- `site_config.py` — campo `email_contato`.

## 5. Ativar o GitHub Pages

1. No repositório, vá em **Settings → Pages**.
2. Em "Build and deployment", escolha **Deploy from a branch**.
3. Em "Branch", escolha `main` e a pasta **`/docs`**.
4. Clique em **Save**.
5. Em alguns minutos, o site estará disponível em
   `https://SEU-USUARIO.github.io/receitas-blog/`.

## 6. Ativar a receita automática diária

A automação já está pronta em `.github/workflows/daily-recipe.yml` — ela
gera 1 receita nova por dia usando IA (API da Anthropic/Claude) e publica
sozinha.

1. Crie uma chave de API em https://console.anthropic.com/ (seção "API
   Keys"). Isso tem custo bem baixo por chamada (poucos centavos por
   receita gerada).
2. No repositório do GitHub, vá em **Settings → Secrets and variables →
   Actions → New repository secret**.
3. Nome do secret: `ANTHROPIC_API_KEY`. Valor: cole a chave gerada.
4. Pronto. Todo dia às 9h (horário UTC, ajustável no arquivo do workflow)
   uma nova receita é gerada, o site é reconstruído e publicado
   automaticamente.
5. Para testar sem esperar o horário, vá na aba **Actions** do repositório,
   escolha o workflow "Publicar receita diária" e clique em **Run
   workflow**.

Se preferir não usar geração por IA por enquanto, pode simplesmente não
configurar o secret — o site continua funcionando normalmente com as
receitas já existentes, e você pode adicionar receitas manualmente
seguindo o formato em `GUIA_DE_CONTEUDO.md`.

## 7. Domínio próprio (opcional, mas recomendado para AdSense)

Um domínio próprio (ex: `receitarapida.com.br`) passa mais credibilidade e
facilita a aprovação no AdSense.

1. Compre um domínio (Registro.br, Hostinger, GoDaddy, etc. — geralmente
   R$ 40–70/ano para `.com.br`).
2. No GitHub, em **Settings → Pages → Custom domain**, digite seu domínio.
3. No painel do seu domínio, configure os registros DNS conforme a
   documentação do GitHub Pages:
   https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site
4. Atualize `site_config.py` com a nova `url` (ex:
   `https://www.receitarapida.com.br`) e rode `python3 build.py` de novo.

## 8. Sobre o Google AdSense

Para ser aprovado no AdSense, o Google geralmente espera:

- Conteúdo original e de qualidade (você já tem isso).
- Páginas de Sobre, Contato e Política de Privacidade (já incluídas).
- Algum tempo online e tráfego orgânico real — sites muito novos ou vazios
  costumam ser recusados na primeira tentativa.
- Domínio próprio é recomendado (subdomínios gratuitos do tipo
  `github.io` às vezes são aceitos, mas um domínio próprio aumenta as
  chances).

Recomendo publicar o site, deixar a automação rodando por algumas semanas
para acumular receitas e algum tráfego (compartilhando nas redes sociais,
por exemplo), e só então enviar para revisão do AdSense em
https://www.google.com/adsense/.

## Comandos úteis

```bash
python3 build.py          # gera o site em docs/ a partir do conteúdo
python3 scripts/gerar_receita.py   # gera manualmente 1 receita nova via IA
                                     # (requer ANTHROPIC_API_KEY no ambiente)
```
