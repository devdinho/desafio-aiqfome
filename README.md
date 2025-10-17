
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
- GET /api/customer — obter perfil do usuário autenticado
- GET /api/customer/{id} — obter perfil por id

- Favorites endpoints (registrados em `/api/favorites` via router):
    - GET /api/favorites — listar favoritos ativos do usuário autenticado
    - POST /api/favorites — criar um favorito (body: {"product_data": {...}})
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
DELETE /api/customer/`{id}`
Authorization: Bearer `<access>`

Response (204) - `No Content`

##### Após o hard delete, o cache de favorito deste cliente/usuário, é excluído.

##### Observação: para ver todas as operações e schemas detalhados, prefira a UI disponível em `/swagger/` (muito útil para testar rapidamente payloads e ver os campos esperados).
