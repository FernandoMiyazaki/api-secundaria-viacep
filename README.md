# API Secundária ViaCEP - Sistema de Câmbio

Esta API secundária é responsável pelo gerenciamento de usuários e consultas de CEP no Sistema de Câmbio. Ela implementa todas as regras de negócio relacionadas a usuários e endereços, incluindo validação de dados e integração com o serviço ViaCEP.

## Responsabilidades

- Consultar e validar CEPs através do serviço externo ViaCEP
- Gerenciar o ciclo de vida completo dos usuários (CRUD)
- Validar dados como email, CPF e CEP
- Implementar regras de negócio relacionadas a usuários e endereços

## Instruções de Instalação

### Pré-requisitos
- Docker e Docker Compose
- Python 3.11 ou superior (para desenvolvimento local)
- Git

### Passos para instalação

1. Clone o repositório:
```bash
git clone https://github.com/FernandoMiyazaki/api-secundaria-viacep.git
```

2. Certifique-se de que o seguinte arquivo está presente:

- `api-secundaria-viacep/.env`

3. Usando Docker (recomendado):
```bash
# A API ViaCEP é iniciada como parte do docker-compose
# a partir da pasta da API Principal
cd ../api-principal-corretora
docker-compose up -d
```

4. Para desenvolvimento local (opcional):
```bash
# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
python run.py
```

## Endpoints

### CEP
- `GET /cep/{cep}` - Consulta um CEP e retorna os dados de endereço
- `POST /cep/{cep}` - Consulta um CEP e persiste os dados no banco
- `GET /cep` - Lista todas as consultas de CEP realizadas
- `DELETE /cep/{id}` - Remove uma consulta do banco de dados
- `PUT /cep/{id}/{complemento}` - Atualiza o complemento de uma consulta

### Usuários
- `GET /usuarios` - Lista todos os usuários
- `POST /usuarios` - Cria um novo usuário
- `GET /usuarios/{id}` - Obtém um usuário específico
- `PUT /usuarios/{id}` - Atualiza um usuário
- `DELETE /usuarios/{id}` - Remove um usuário

## Validações Implementadas
- Validação de formato de CEP (8 dígitos)
- Validação de existência de CEP via serviço externo
- Validação de CPF (algoritmo completo)
- Validação de email
- Unicidade de email e CPF no cadastro de usuários

## Tecnologias Utilizadas
- Flask
- SQLAlchemy
- PostgreSQL
- Flask-RESTx para documentação Swagger
- Requests para chamadas HTTP

## Acessando a Documentação da API
- Swagger UI: http://localhost:5001/swagger

## Modelo de Dados

### Tabela `cep_consultas`
- `id`: Chave primária
- `cep`: CEP formatado (8 dígitos)
- `logradouro`: Nome da rua/avenida
- `complemento`: Complemento (se houver)
- `bairro`: Bairro
- `localidade`: Cidade
- `uf`: Estado (sigla)
- `estado`: Nome do estado
- `regiao`: Região do Brasil
- `ibge`: Código IBGE
- `gia`: Código GIA
- `ddd`: DDD da região
- `siafi`: Código SIAFI
- `created_at`: Data/hora de criação

### Tabela `usuarios`
- `id`: Chave primária
- `nome_completo`: Nome completo do usuário
- `email`: Email (único)
- `senha`: Senha
- `cpf`: CPF (único)
- `cep`: CEP
- `logradouro`: Rua/Avenida
- `complemento`: Complemento do endereço
- `bairro`: Bairro
- `localidade`: Cidade
- `estado`: Estado
- `created_at`: Data/hora de criação
- `updated_at`: Data/hora de atualização