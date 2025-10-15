
![ArmoredDjango](https://portifolio.dinho.dev/media/projetos/Armored_Django_V3.png)

Uma base (template) de aplicação web construída com Django, focada em oferecer
um ponto de partida com autenticação, gerenciamento de perfis e integração
pronta para execução via Docker. Este repositório contém o código do service
(backend) em `service/src` e scripts para facilitar desenvolvimento, lint e
testes.

## Sumário

- Visão geral
- Requisitos
- Instalação (local)
- Execução com Docker
- Testes e lint
- Estrutura do projeto
- Como contribuir
- Licença

## Visão geral

O projeto inclui:

- App `authentication` com um modelo de usuário customizado `Profile`.
- Endpoints REST (DRF) para manipulação do perfil (`ProfileRestView`).
- Scripts para iniciar a aplicação, coletar estáticos e executar migrations.
- Configuração para executar via Docker (imagem baseada em Python + Poetry).

## Requisitos

- Python >= 3.10
- Docker & Docker Compose (opcional, recomendado para desenvolvimento e CI)
- PostgreSQL (quando não usar Docker)

As dependências Python estão gerenciadas via Poetry no arquivo
`service/pyproject.toml`.

## Instalação (modo local, sem Docker)

1. Crie e ative um ambiente virtual com Python >=3.10:

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Instale as dependências (preferido: usar Poetry):

```bash
cd service
poetry install
```

3. Copie e configure variáveis de ambiente (arquivo `.env`). Exemplos:

- POSTGRES_USER
- POSTGRES_PASSWORD
- DB_PORT
- ADMIN_PASSWORD
- PRODUCTION (setar True/False no container)

4. Execute migrations e crie um superusuário (o script `start.sh` já tenta
criar um usuário `admin` usando `ADMIN_PASSWORD`):

```bash
cd service
python src/manage.py migrate
python src/manage.py createsuperuser
```

5. Rode o servidor de desenvolvimento:

```bash
python src/manage.py runserver 0.0.0.0:8003
```

Abra http://localhost:8003/ no navegador.

## Execução com Docker (recomendado)

O projeto fornece um `Dockerfile` e `docker-compose.yaml` na raiz que
constroem um container do serviço e um container com PostgreSQL. O container do
service monta `./service` em `/app` e usa `/app/scripts/start.sh` como entrypoint.

Para rodar com Docker Compose:

```bash
# (na raiz do projeto)
docker compose up --build
```

Com isso o serviço Django ficará disponível em `http://localhost:8003/`.

Observações sobre o container:

- O `Dockerfile` instala o Poetry e as ferramentas de lint (black/isort/flake8).
- O `start.sh` coleta estáticos, gera migrations, aplica `migrate` e cria um
    superusuário `admin` (utiliza a variável `ADMIN_PASSWORD`).
- Para modo produção, defina `PRODUCTION=True` no `.env` e o container usará
    Gunicorn conforme `gunicorn_config.py`.

## Testes e Lint

O repositório já inclui scripts para facilitar testes e lint:

- Testes unitários (executar dentro do container ou localmente):

```bash
# dentro do container ou no diretório service com ambiente configurado
./scripts/run_unit_tests.sh
```

- Lint e formatação (local ou container):

```bash
# Executa black, isort e flake8 nos arquivos/pastas informados
./scripts/start-lint.sh <caminho-ou-pacote>
```

## Estrutura principal do projeto

 (visão resumida)

- service/: Dockerfile, scripts e código Python (src/)
    - src/armoreddjango/: configurações do Django
    - src/authentication/: app com models, serializers e views
    - scripts/: scripts para start, lint e testes
- docker-compose.yaml: define os serviços `django` e `db` (Postgres)

Exemplo de arquivos relevantes:

- `service/src/authentication/models/Profile.py` — modelo `Profile` que
    estende `AbstractUser` adicionando `email` único e `profileType`.
- `service/src/authentication/api/ProfileRestView.py` — `ModelViewSet` que
    expõe operações de list/update (create e delete são proibidos).

## Como contribuir

Pequenas contribuições são bem-vindas. Fluxo sugerido:

1. Fork do repositório
2. Crie uma branch com a feature/bugfix: `git checkout -b feat/minha-mudanca`
3. Abra um pull request descrevendo a alteração

Dicas:

- Rode os testes localmente antes de abrir PR
- Siga as regras do linter (black/isort/flake8)

## Comandos úteis rápidos

- Subir com Docker Compose: `docker-compose up --build`
- Rodar apenas o serviço (em dev): `python service/src/manage.py runserver`
- Executar testes: `service/scripts/run_unit_tests.sh`
- Executar lint: `service/scripts/start-lint.sh <alvo>`

## Licença

Este projeto está sob a licença MIT — veja `LICENSE` para detalhes.
