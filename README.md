# Meu Acervo Digital de Romances

## Descrição

Meu Acervo Digital de Romances é uma aplicação para gerenciar e catalogar livros. Desenvolvida como projeto final do curso [FastAPI do Zero](https://fastapidozero.dunossauro.com/14/).

## Instalação e uso local

Projeto desenvolido em`Python 3.12` com `poetry 1.8.2`.

Para reproduzir o projeto, deve-se:

1. Clonar o repositório.

```sh
git clone https://github.com/danielbrito91/madr.git
cd madr
```

2. Criar arquivo `.env` com as seguintes variáveis:

- `DATABASE_URL`: URL de conexão com o banco de dados
- `SECRET_KEY`: chave secreta para proteger token de autenticação
- `ALGORITHM`: algorítimo para encriptografar o token.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: tempo de expiração do token JWT em minutos.

3. É possível executar o projeto em:

- Diretamente em seu computador, executando:

```sh
poetry install
poetry run task run
```

- Ou via Docker:

```sh
docker-compose up
```

4. Acesse a aplicação no navegador:

```sh
http://localhost:8000
