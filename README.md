
# Aiqfome — Serviço backend

Backend Django para o desafio Aiqfome. Implementa autenticação, gerenciamento de clientes e favoritos de produtos integrados a uma API externa (FakeStore).

Este README descreve como rodar, variáveis de ambiente importantes e os endpoints principais.

Sumário
- Sobre
- Requisitos
- Variáveis de ambiente importantes
- Como rodar (Docker)
- Endpoints principais
- Cache de favoritos
- Migrations e testes
- Explicação sobre escolhas

Sobre
-------
O serviço fornece:

- Autenticação JWT (login/refresh/verify).
- Registro e gerenciamento de customers (perfil de usuário customizado).
- Endpoints para gerenciar produtos favoritos por usuário.
- Integração com uma FakeStore API (proxy interno e validação de produtos).

Requisitos
----------
- Docker & Docker Compose (recomendado)
- Python 3.10+ (para execução local sem Docker)

Variáveis de ambiente importantes
---------------------------------
Defina um arquivo `.env` na raiz. Existe um exemplo no repositório o `.env.example`, você pode copiar e renomear para `.env`. 

As variáveis mais importantes:

- SECRET_KEY — segredo do Django (se conter `$`, deve ser colocado entre aspas simples).
- POSTGRES_USER / POSTGRES_PASSWORD / DB_PORT — credenciais do Postgres.
- ADMIN_PASSWORD — senha usada pelo script para criar usuário `admin`.
- PRODUCTION — True/False. Quando True, o container inicia em modo produção usando o `gunicorn` e quando False ele utiliza o `runserver`.
- FAKESTORE_BASE_URL — URLs usadas para consultar os produtos externos (Hardcoded dentro do settings do Django).
    
Como rodar (com Docker)
-----------------------
Na raiz do projeto:

```bash
docker compose up --build
```

O serviço Django ficará disponível em http://localhost:8003/.
O Swagger ficará disponível em http://localhost:8003/swagger/.
O ReDoc ficará disponível em http://localhost:8003/redoc/.

Endpoints principais
--------------------
- POST /api/login/ — obter pair JWT
- POST /api/login/refresh/ — refresh token
- POST /api/login/verify/ — verificar token
- POST /api/register/ — (endpoint de registro, ver `CreateCustomerRestView`)
- GET /api/customers — obter perfil do usuário autenticado
- GET /api/customers/{id} — obter perfil por id

- Favorites endpoints (registrados em `/api/favorites` via router):
    - GET /api/favorites — listar favoritos ativos do usuário autenticado
    - POST /api/favorites — criar um favorito (body: {"product_id": 3})
    - GET /api/favorites/{id} — obter favorito por id
    - PATCH /api/favorites/{id} — atualizar favorito
    - DELETE /api/favorites/{id} — desativar favorito (soft delete)

Observação: endpoints de `Customers` e `Favorites` exigem autenticação JWT (Authorization: Bearer `<token>`).

Cache de favoritos
-------------------
O serviço usa cache para armazenar a lista de favoritos por usuário com a
chave `fakestore:all_products:{user_id}`:

- A função util `utils.cache_utils.update_favorites_cache_for_user(user_id)`
    centraliza a atualização do cache.
- Ao criar ou desativar favoritos, o cache é atualizado automaticamente.
- Ao consultar a API externa também existe cache na listagem e na consulta em um produto específico.

Migrações e testes
------------------
### Gerar e aplicar migrações (quando rodando local ou no container):

```bash
cd service
python src/manage.py makemigrations
python src/manage.py migrate
```
    P.S: As migrações são automaticamente geradas e aplicadas ao subir o docker. 


### Executar testes unitários (rodar dentro do container ou localmente com o ambiente configurado):

```bash
./service/scripts/run_unit_tests.sh
```

Comandos úteis
-------------
- Subir com Docker Compose: `docker compose up --build`
- Rodar localmente (dev): `python service/src/manage.py runserver 0.0.0.0:8003`
- Executar testes: `./service/scripts/run_unit_tests.sh`
- Executar lint: `./service/scripts/start-lint.sh <alvo>`


Exemplos de payloads e respostas
--------------------------------
O projeto expõe documentação interativa com Swagger/ReDoc quando `PRODUCTION` é False. 

Acesse:

- `http://localhost:8003/swagger/` (Swagger UI)
- `http://localhost:8003/redoc/` (ReDoc)

#### Exemplos rápidos (JSON):

### 1) Autenticação — obter JWT

Request:

POST /api/login/

```json
{
    "username": "admin",
    "password": "admin"
}
```

Response (200):

```json
{
    "access": "<jwt-access-token>",
    "refresh": "<jwt-refresh-token>"
}
```

### 2) Registrar usuário

Request:

POST /api/register/

```json
{
    "first_name": "John",
    "last_name": "Doe",
    "username": "jdoe",
    "password": "strongpass",
    "email": "jdoe@example.com"
}
```

Response (201):

```json
{
    "id": 5,
    "first_name": "John",
    "last_name": "Doe",
    "username": "jdoe",
    "email": "jdoe@example.com",
    "last_login": null,
    "date_joined": "2025-10-16T12:00:00Z"
}
```

### 3) Criar favorito

O serializer espera `product_id` no payload; o serviço busca os dados do produto na FakeStore (proxy interno) e grava `product_data` automaticamente.

Request:

POST /api/favorites
Authorization: Bearer `<access>`

```json
{
    "product_id": 3
}
```

Response (201):

```json
{
    "id": "<uuid>",
    "customer": "<customer_id>",
    "product_id": 3,
    "product_data": {
        "title": "Mens Cotton Jacket",
        "price": 55.99,
        "description": "great outerwear jackets for Spring/Autumn/Winter, suitable for many occasions, such as working, hiking, camping, mountain/rock climbing, cycling, traveling or other outdoors. Good gift choice for you or your family member. A warm hearted love to Father, husband or son in this thanksgiving or Christmas Day.",
        "category": "men's clothing",
        "image": "https://fakestoreapi.com/img/71li-ujtlUL._AC_UX679_t.png",
        "rating": { "rate": 4.7, "count": 500 }
    },
    "active": true,
    "created_at": "2025-10-16T12:05:00Z",
    "updated_at": "2025-10-16T12:05:00Z"
}
```
##### Após a criação, o cache de favorito é atualizado.

### 4) Listar favoritos

Request:

GET /api/favorites
Authorization: Bearer `<access>`

Response (200):

```json
[
    {
        "id": "<uuid>",
        "customer": "<customer_id>",
        "product_id": 3,
        "product_data": { ... },
        "active": true,
        "created_at": "2025-10-16T12:05:00Z",
        "updated_at": "2025-10-16T12:05:00Z"
    }
]
```

##### Após a primeira listagem, o cache de favorito é criado.

### 5) Recuperar favorito
GET /api/favorites/`{id}`
Authorization: Bearer `<access>`

Response (200):

```json
{
    "id": "<uuid>",
    "customer": "<customer_id>",
    "product_id": 3,
    "product_data": { ... },
    "active": true,
    "created_at": "2025-10-16T12:05:00Z",
    "updated_at": "2025-10-16T12:05:00Z"
}
```
##### Após a primeira listagem, o cache de favorito é criado.

### 6) Apagar favorito (Soft delete)
DELETE /api/favorites/`{id}`
Authorization: Bearer `<access>`

Response (204) - `No Content`

##### Após o soft delete, o cache de favorito é atualizado.

### 7) Apagar Cliente (Hard delete)
DELETE /api/customers/`{id}`
Authorization: Bearer `<access>`

Response (204) - `No Content`

##### Após o hard delete, o cache de favorito deste cliente/usuário, é excluído.

##### Observação: para ver todas as operações e schemas detalhados, prefira a UI disponível em `/swagger/` (muito útil para testar rapidamente payloads e ver os campos esperados).


##

## 🔥 Escolhas técnicas 🍲 
### Arquitetura e Modelagem
##

#### O “Customer” é um Custom User (AbstractUser/AbstractBaseUser) ou um perfil ligado a User? Por quê?
###### Sim, é um Custom User criado para poder ter mais controle sobre a tabela de usuários e adicionar mais campos sem ser necessário criar uma outra instância associadas ao usuário. Por exemplo caso seja necessário adicionar foto de perfil, endereço, site pessoal, linkedin e etc.

#### O e-mail é único de forma case-insensitive? Considerou UniqueConstraint com Lower(email) ou CITEXT no Postgres?
###### O e-mail é registrado em lower-case. O UniqueConstraint funciona apenas para unicidade, consultas iriam precisar de `__iexact`. O CITEXT não é compatível com a funcionalidade para histórico de alterações.

#### O fluxo de remoção de clientes existe? Será hard delete, soft delete ou restrito ao admin?
###### O django por padrão faz um soft delete, modificando o valor da coluna is_active para false. Porém nesta aplicação é realizado um hard delete que pode ser solicitado pelo próprio usuário e por um algum admin.

#### Em Favoritos, há soft delete? Se sim, a unicidade (customer_id, product_id) foi pensada para reativar sem violar a constraint?
###### Sim, nos favoritos é realizado um soft delete. a unicidade entre o id do cliente e produto foi pensada para não ter duplicação e produtos como favoritos e também serve para a reativação do produto favorito.

#### Por que optou por endpoint de registro separado (/api/register) em vez de POST /api/customers? Vantagens/limitações?
###### Por vantagens. Caso seja necessário criar mais instancias durante o cadastro do usuário, podemos criar nessa view que é separada.

##
### API e Rotas
##

#### Os endpoints seguem padrões REST (plural, sem verbos na URL, status codes consistentes)?
###### Sim, os endpoints seguem padrões REST: os recursos estão no plural, não usamos verbos nas URLs e os status codes HTTP retornados são consistentes com cada operação (200, 201, 204, 400, 404, etc.).

#### Há paginação nas listagens (favorites, products)? Qual PageSize default?
###### Não há paginação nas listagens (favorites, products), pois a quantidade de itens é pequena e não justifica a complexidade adicional. Portanto, todos os itens são retornados em uma única resposta e não há um PageSize definido.

#### As respostas de erro seguem um formato padrão (ex.: {"detail": "...", "code": "..."})?
###### Sim, as respostas de erro seguem um formato padrão. Em geral, retornam um JSON com os campos detail e o status code, fornecendo uma mensagem clara do erro e um código identificador, garantindo consistência entre diferentes endpoints.

#### Há versionamento de API (ex.: /api/v1/…) para futuras mudanças?
###### Não há versionamento de API, mas ele pode ser facilmente implementado no futuro, garantindo compatibilidade com mudanças sem impactar clientes existentes.

##
### Segurança e Autorização
##

#### As permissões restringem Customer e Favorites ao usuário autenticado (object-level)? Como trata o caso de admin?
###### Sim. As views exigem autenticação (JWT) e implementam verificações de nível de objeto para garantir que o usuário só acesse/edite seus próprios recursos. Para administradores (`is_superuser=True`), o acesso é liberado conforme necessário (ex.: leitura/remoção de qualquer registro).

#### Há throttle/rate limiting (login, chamadas externas) para mitigar abuso?
###### Ainda não foi habilitado throttling no DRF. É recomendável configurar `DEFAULT_THROTTLE_CLASSES`/`RATES` para login e eventualmente para o proxy da FakeStore.

#### Políticas de CORS/CSRF em produção estão mínimas necessárias?
###### Sim. `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` e `CORS_ALLOWED_ORIGINS` usam o domínio do `.env` e localhost para desenvolvimento. Em produção, manter apenas os domínios oficiais.

#### Política de senha e enumeração de usuários
###### A política de senha usa os validadores padrão do Django. Para evitar enumeração, mensagens de erro são genéricas nos fluxos de autenticação.

##
### Integração com a API externa (FakeStore)
##

#### Como é feita a validação de produtos?
###### O serviço consulta a FakeStore via proxy interno (`/api/products`) para validar `product_id` e obter `product_data`. Em caso de 404, retorna erro ao cliente.

#### Campo "review" nos favoritos (rating vs review)
###### A FakeStore expõe `rating` (rate/count). O projeto retorna esse conteúdo em `product_data`. Quando necessário exibir "review", usamos o campo `rating` como fonte; se ausente, o valor fica nulo.

#### Timeouts, retries e erros
###### As chamadas externas utilizam `requests`. Hoje não há `retry` automático; erros retornam 502 (gateway) ou 404 conforme o caso. Pode ser adicionado e é recomendável,wse3 timeout explícito e política de retries com backoff.

##
### Cache e Performance
##

#### Que itens são cacheados?
###### A lista de favoritos do usuário é cacheada por chave `fakestore:all_products:{user_id}`. Além disso, o proxy da FakeStore cacheia a listagem completa e a consulta por produto.

#### TTL e onde fica configurado
###### O TTL é controlado por `CACHE_TIMEOUT` nos settings. Pode ser ajustado por ambiente.

#### Atualização do cache
###### Foi centralizada na função `utils.cache_utils.update_favorites_cache_for_user(user_id)`, chamada após criar/desativar favoritos. Agora usamos `transaction.on_commit` para disparar a atualização somente depois do commit da transação,evitando que o cache fique inconsistente se ocorrer rollback.

#### Evita N+1 chamadas externas?
###### Sim. Ao criar o favorito, salvamos `product_data`. Na listagem, retornamos esse snapshot e apenas atualizamos via proxy quando necessário, evitando chamadas por item.

##
### Dados e Banco de Dados
##

#### Unicidade e índices
###### Favoritos têm `unique_together (customer, product_id)` para impedir duplicatas. Além disso, foi criado um índice composto `idx_customer_active` em `(customer, active)` para acelerar a listagem de favoritos ativos por usuário.


#### Tipagem de preço
###### O preço vem do JSON externo (float). Como não persistimos preço separado (fica em `product_data`), não há risco de cálculo contábil interno. Se futuramente for necessário snapshot contábil, usar `Decimal`/`Inteiro`.

#### Normalização de e‑mail
###### O e‑mail é armazenado em minúsculas para garantir unicidade case‑insensitive. Validações no serializer impedem duplicidade.

#### Migrações
###### As migrações são geradas e aplicadas automaticamente na subida do Docker. Em desenvolvimento local, comandos de `makemigrations`/`migrate` estão documentados.

##
### Configuração e Deploy
##

#### Variáveis de ambiente e defaults
###### `SECRET_KEY`, credenciais do Postgres e flags `PRODUCTION/DEBUG` vêm do `.env`. O `SECRET_KEY` deve estar entre aspas simples se contiver `$`. O endpoint da FakeStore é configurado via settings.

#### Gunicorn e execução em produção
###### Em `PRODUCTION=True`, o serviço usa Gunicorn (config padrão do projeto). É possível ajustar número de workers, timeout e logs no arquivo de configuração.

##
### Testes e Qualidade
##

#### Cobertura de testes
###### Foram implementados testes para: criação e unicidade de clientes; autenticação e permissões; favoritos (validação externa, duplicidade, soft delete); e cache (hit/miss, atualização).

#### Linters e formato
###### Scripts de lint (black/isort/flake8) já estão disponíveis via `./service/scripts/start-lint.sh`.

##
### Documentação
##

#### OpenAPI (Swagger/ReDoc)
###### A documentação está disponível em `/swagger/` e `/redoc/` (em não‑produção). Os exemplos de payloads no README complementam a navegação pela UI.