# Bank API

Projeto para a avaliação final da disciplina "Criptografia e Trusted Computing" do Projeto Connor.

**Aluna:** Giovanna Souza Teodoro

**Aplicação:** Sistema bancário feito com FastAPI + Prisma (MySQL) para mostrar a implementação de proteção contra **Replay Attack**.


## Estrutura

```
bank-api/
├── app/
│   ├── main.py
│   ├── db.py
│   ├── core/
│   │   └── security.py     # JWT, bcrypt, nonce
│   └── routers/
│       ├── auth.py          # /auth/register + /auth/login
│       ├── users.py         # /users/me + /users/
│       └── transactions.py  # /transactions/transfer + /history + /nonce
├── prisma/
│   └── schema.prisma
├── .env.example
└── requirements.txt
```

## Setup

```bash
openssl rand -base64 32 # para criar um SECRET_KEY forte
cp .env.example .env # preencher com o SECRET_KEY criado
virtualenv venv # para isolar o ambiente
source venv/bin/activate
pip install -r requirements.txt # este passo demora um pouco
prisma generate # cria o
prisma db push # cria as tabelas
uvicorn app.main:app --reload
```

Acesse o Swagger UI em: http://localhost:8000/docs

## Segurança implementada: Proteção contra Replay Attack

### O ataque
Um atacante intercepta uma requisição legítima de transferência e a reenvia para duplicar a operação.

### A defesa
Toda transferência exige um campo `nonce` (valor único gerado via `secrets.token_hex(16)`).
O servidor rejeita com **409** qualquer `nonce` já utilizado (campo `UNIQUE` no banco).

### Simulando o ataque

**1. Obtenha um nonce:**
```
GET /transactions/nonce
Resposta: {"nonce": "abc123..."}
```

**2. Faça a transferência legítima:**
```json
POST /transactions/transfer
Resposta: 201 Created
{"receiver_id": 2, "amount": 100, "nonce": "abc123..."}
```

**3. Replay — reenvie exatamente a mesma requisição:**
```json
POST /transactions/transfer
Resposta: 409 Conflict: "Duplicate transaction (replay detected)"
{"receiver_id": 2, "amount": 100, "nonce": "abc123..."}
```

O segundo envio é bloqueado porque o nonce já existe no banco.

## Rotas

| Método | Rota | Auth | Descrição |
|--------|------|------|-----------|
| POST | /auth/register | ✗ | Criar conta |
| POST | /auth/login | ✗ | Obter JWT |
| GET | /users/me | ✓ | Meu perfil + saldo |
| GET | /users/ | ✓ | Listar usuários |
| GET | /transactions/nonce | ✓ | Gerar nonce |
| POST | /transactions/transfer | ✓ | Transferir |
| GET | /transactions/history | ✓ | Histórico |
