# GateMesh

GateMesh é um gateway customizado em Python para roteamento, autenticação, monitoramento e controle de serviços HTTP. O projeto combina uma API de encaminhamento com uma interface web de monitoramento, permitindo centralizar a comunicação entre clientes e serviços internos, registrar logs e configurar rotas dinamicamente por meio de um arquivo YAML.

Ele foi pensado para ambientes em que é necessário reduzir a complexidade de integrações diretas entre aplicações, mantendo uma camada de controle de acesso, observabilidade e gestão de configuração.

## Visão geral

O GateMesh disponibiliza:

- Roteamento de requisições entre cliente e serviços de destino
- Monitoramento de status das rotas configuradas
- Registro de logs e conexões
- Gestão de parâmetros e configuração via interface web
- Autenticação simples por usuário/senha no painel administrativo
- Suporte a arquivos `.gmc` para regras e comportamento do gateway

O projeto é composto por:

- uma API Flask para servir como gateway central
- um painel administrativo para monitoramento de rotas e parâmetros
- um banco SQLite para armazenar usuários, logs, conexões e parâmetros
- uma camada de compilação de regras customizadas (`GmcCopiler`) para controlar acessos e fluxos

## Funcionalidades principais

### 1. Gateway HTTP
O gateway recebe requisições em um endpoint de serviço e redireciona para a rota configurada em `config/gateway.yml`.

Exemplo de fluxo:

- o cliente chama `http://localhost:<porta>/_gateway/service/<nome_do_servico>`
- o sistema localiza a rota correspondente em `gateway.yml`
- valida autenticação e regras do `.gmc`
- encaminha a requisição para o serviço alvo
- registra logs e status da resposta

### 2. Monitoramento web
A aplicação possui um painel com páginas para:

- login
- visualização do status dos serviços
- logs de respostas HTTP
- administração de parâmetros do sistema
- edição e acompanhamento da configuração do gateway

### 3. Sistema de autenticação
O banco inicial cria um usuário administrador padrão:

- usuário: `admin`
- senha: `admin`

Esse usuário é criado automaticamente na primeira execução do sistema, pela função `init_db()`.

### 4. Arquivos de configuração
A configuração do gateway é definida em YAML em `config/gateway.yml`, permitindo mapear:

- host e porta do gateway
- nome da rota
- caminho da rota
- destino do serviço

### 5. Regras `.gmc`
O sistema aceita arquivos `.gmc` para definir regras de execução da rota, como:

- `check_service`
- `service_use`
- `limit_request`
- `check_fail`
- `absolute_request`
- `allow_resource_for`

Essas instruções são processadas pela classe `GmcCopiler`, que valida disponibilidade do serviço, limites e acesso a recursos.

## Estrutura do projeto

```text
GateMesh/
├── GateMonitor/                 # Blueprint e endpoints do monitor/admin
│   ├── api.py                  # API do gateway
│   └── monitor.py              # Dashboard, login, logs, parâmetros
├── GateMonitor_package/         # Camada para chamadas HTTP e compilação GMC
│   ├── GateMonitorHttp.py      # Execução de chamadas e roteamento
│   └── gmcCopiler.py           # Processamento da linguagem GMC
├── data/                       # Modelos e repositórios do banco de dados
│   ├── models/                 # SQLAlchemy models
│   └── repo/                   # Acesso a dados e persistência
├── config/                     # Arquivos de configuração do projeto
│   └── gateway.yml             # Rotas do gateway
├── templates/                  # Templates HTML do painel web
├── static/                     # Assets estáticos do frontend
├── app.py                      # Classe principal de bootstrap
├── GateMonitorApp.py           # Aplicação Flask principal
├── gatemesh.db                 # Banco SQLite local
├── README.md                   # Documentação do projeto
├── LICENSE                     # Licença
└── ...
```

## Pré-requisitos

- Python 3.10+
- Flask
- SQLAlchemy
- PyYAML
- requests

Instale as dependências manualmente:

```bash
pip install flask sqlalchemy pyyaml requests
```

## Instalação e execução

1. Acesse a pasta do projeto

```bash
cd GateMesh
```

2. Inicie a aplicação:

```bash
python GateMonitorApp.py
```

3. Acesse no navegador:

```text
http://localhost:8000/login
```

> O valor da porta é lido de `config/gateway.yml`.

## Configuração do gateway

O arquivo principal de configuração está em:

```yaml
config/gateway.yml
```

Exemplo:

```yaml
gateway:
  host: 0.0.0.0
  port: 8000
routes:
  - name: users
    path: /
    target: http://localhost:5001

  - name: DataBase
    path: /_gateway/config
    target: http://localhost:8000
```

### Campos da rota

Cada item da lista `routes` aceita:

- `name`: nome lógico da rota
- `path`: caminho que será usado pelo gateway
- `target`: endereço do serviço backend para o qual a requisição será enviada

## Como usar o projeto

### Acesso ao painel

Abra a URL:

```text
http://localhost:8000/login
```

Faça login com:

```text
admin / admin
```

### Painel disponível

Após autenticar, você terá acesso às seguintes áreas:

- `/monitoring` — status dos serviços e rotas
- `/logs` — histórico de logs
- `/parameters` — parâmetros e configuração do sistema
- `/docs` — documentação interna do projeto
- `/logout` — encerramento da sessão

## API do gateway

### GET /_gateway/health
Retorna o status da aplicação.

Resposta:

```json
{
  "status": "healthy"
}
```

### GET /_gateway/config
Retorna a configuração atual do gateway.

Resposta:

```json
{
  "gateway": {
    "host": "0.0.0.0",
    "port": 8000
  },
  "routes": [
    {
      "name": "users",
      "path": "/",
      "target": "http://localhost:5001"
    }
  ]
}
```

### GET /_gateway/service/<service>
Esse endpoint executa o processamento do serviço solicitado.

Payload esperado em JSON (exemplo):

```json
{
  "service": "users",
  "app": "app-name",
  "token": "token-da-aplicacao",
  "userToken": "token-do-usuario",
  "config_register": "conteudo do arquivo .gmc"
}
```

O comportamento do gateway inclui:

- validação do token da aplicação
- leitura do arquivo `.gmc` do serviço
- checagem de disponibilidade do destino
- limite de requisições
- redirecionamento em caso de falha
- registro de log da resposta

## Linguagem GMC

A linguagem GMC é usada para descrever regras de uso e acesso do gateway. Os blocos principais incluem:

```text
var nome = "valor"
check_service: "servico"
service_use = "rota_destino"
limit_request = 100
limit_request if: "redirect_to" 
check_fail if: "redirect_to"
absolute_request = "http://localhost:8080"
allow_resource_for: "admin,user"
```

### Exemplos de instruções

#### `@use selector_service`
Permite separar lógica por serviço ou rota.

```text
@use selector_service

@users
    var z = 4
    service_use = "listar_usuarios"
@end
```

#### `check_service`
Verifica se o serviço alvo está disponível.

#### `limit_request`
Define uma limitação de requisições por serviço.

#### `check_fail if: "redirect_to"`
Define uma rota alternativa caso o serviço falhe.

#### `allow_resource_for`
Restringe a execução por perfil ou token de usuário.

## Documentação dos métodos e funções

### `GateMonitorApp.py`

#### `load_config(config_path: Path) -> dict`
Carrega e valida o arquivo YAML de configuração do gateway.

#### `validate_config(config: dict) -> None`
Valida a estrutura mínima do arquivo de configuração, verificando:

- existência da chave `gateway`
- existência da chave `routes`
- tipo e validade de `host` e `port`
- estrutura de cada rota com `name`, `path` e `target`

#### `create_app() -> Flask`
Cria a aplicação Flask, inicializa o banco SQLite e define endpoints de saúde e config.

#### `GateMonitor` (classe)
Responsável por inicializar o gateway e iniciar o servidor.

- `__init__(host, port=5000)`
- `start()`

### `GateMonitor/monitor.py`

#### `get_db()`
Cria ou reutiliza uma sessão do banco de dados por requisição.

#### `teardown_db(exception)`
Fecha a sessão do banco ao final da requisição.

#### `login_required(f)`
Decorator que exige autenticação antes de acessar rotas protegidas.

#### `load_gateway_config()`
Lê `config/gateway.yml` e retorna os dados da configuração, ou valores padrão caso o arquivo não exista.

#### Rotas protegidas e públicas

- `GET /` — redireciona para login ou monitoramento
- `GET /login` — autenticação do usuário
- `GET /logout` — finaliza a sessão
- `GET /logs` — página de logs
- `GET /logs/load` — JSON com registros de logs
- `GET /monitoring` — página de monitoramento
- `GET /monitoring/status` — status das rotas configuradas
- `GET /monitoring/connections` — conexões registradas
- `GET /parameters` — página de parâmetros
- `POST /parameters/saved` — salva a configuração YAML
- `POST /parameters/add` — adiciona parâmetro
- `POST /parameters/update/<param_id>` — atualiza parâmetro
- `POST /parameters/delete/<param_id>` — remove parâmetro
- `POST /parameters/change_password` — altera usuário/senha do administrador
- `GET /docs` — documentação interna
- `GET /docs/<page>` — página específica da documentação

#### `yaml_to_custom_text(config_file)`
Lê um YAML e devolve uma string formatada para renderização no HTML.

#### `salvar_yaml(data, output_file)`
Salva um dicionário Python como arquivo YAML no formato do projeto.

#### `limpar_loop()`
Thread de limpeza periódica de registros antigos na tabela de conexões.

### `GateMonitor/api.py`

#### `index()`
Rota base da API do gateway.

#### `gateway_config(service)`
Executa a lógica principal do gateway:

- lê a configuração
- encontra a rota solicitada pelo nome
- valida token da aplicação
- cria ou carrega código `.gmc`
- executa as regras do arquivo
- redireciona para o serviço de destino
- registra os logs da resposta

#### `classify_http_status(status_code: int) -> str`
Classifica o código HTTP como:

- `Ok` para 2xx
- `Warning` para 3xx
- `Erro` para 4xx
- `Crítico` para 5xx

### `GateMonitor_package/GateMonitorHttp.py`

#### `GateMonitorHttp.__init__(data, host=0, port=0, db="GateMonitor_db")`
Inicializa a camada de comunicação HTTP do gateway.

#### `HttpRequestGet(url, headers=None, params=None, method="GET")`
Faz uma requisição HTTP para um destino e salva informações de conexão.

#### `CreateConfigsToServer(config, server)`
Escreve o conteúdo do arquivo `.gmc` em `config/<server>.gmc`.

#### `GetToken(ProjectName)`
Busca o token do projeto na base de parâmetros.

#### `ExecuteGmcFile(code)`
Executa o arquivo GMC e resolve a requisição seguindo as regras configuradas.

### `GateMonitor_package/gmcCopiler.py`

#### `GmcCopiler.__init__(data)`
Inicializa o compilador e atributos internos para regras de acesso e redirecionamento.

#### `Compile(code)`
Processa o conteúdo do arquivo `.gmc` e extrai instruções importantes.

#### `CreateVars(comma)`
Cria variáveis internas usadas no DSL.

#### `check_service(ServiceName)`
Verifica se um serviço está disponível chamando a URL correta.

#### `LimitRequest(LimitRequest)`
Lê o limite de requisições do arquivo GMC.

#### `ifLimitRequest(LimitedRequest)`
Define rota de redirecionamento ao atingir o limite.

#### `ifLimitRequestFail(LimitedRequest)`
Define rota para falha do serviço.

#### `ServiceUse(services)`
Define qual serviço deve ser usado.

#### `allow_resource_for(resource)`
Valida se o token/usuário possui permissão para o recurso.

### Modelos de dados

#### `User`
Tabela `users`.

Campos:

- `id`
- `username`
- `password_hash`

Métodos:

- `set_password(password)`
- `check_password(password)`

#### `Logs`
Tabela `logs_connections`.

Campos:

- `id`
- `timestamp`
- `message`
- `ResposeHttp`
- `Alert`
- `service`
- `RouteRequest`
- `Time`
- `MemoryCoast`

Método:

- `to_dict()`

#### `Parameter`
Tabela `parameters`.

Campos:

- `id`
- `key`
- `value`
- `category`
- `description`

#### `Conections`
Tabela `conections`.

Campos:

- `id`
- `ip`
- `port`
- `Service`

#### `init_db()`
Cria as tabelas do banco e cria o usuário administrador padrão se não existir.

## Exemplos práticos

### Exemplo de chamada HTTP para o gateway

```python
import requests

url = "http://localhost:8000/_gateway/service/users"
headers = {
    "service": "users",
    "method": "GET",
    "role": "admin",
    "token": "XXXX",
    "userToken": "0000",
    "app": "app-name",
}

response = requests.get(url, headers=headers)
print(response.json())
```

### Exemplo de arquivo GMC

```text
var service_name = "users"
check_service: "health"
limit_request = 50
limit_request if: "redirect_to:/fallback"
check_fail if: "redirect_to:/backup"
service_use = "listar_usuarios"
allow_resource_for: "admin,manager"
```

## Observações importantes

- O sistema cria automaticamente o usuário `admin` com senha `admin` na primeira execução.
- O painel web é responsável por controlar a plataforma de monitoramento e configuração.
- O gateway não é um framework de autenticação completo; ele implementa um fluxo simples e funcional para uso interno.
- A arquitetura foi desenhada para manter o roteamento centralizado, com baixa complexidade operacional e fácil visualização de status.

## Dicas de uso

- Mantenha a configuração YAML sempre em ordem e consistente.
- Os tokens e chaves de autenticação devem ser armazenados de forma segura.
- O arquivo `.gmc` deve refletir exatamente a lógica da rota que você quer controlar.
- Use o painel de logs para identificar falhas de integração e status HTTP inválidos.

## Próximos passos sugeridos

- segura de token e secret management mais robusta
- suporte a autenticação por JWT ou OAuth
- balanceamento de carga entre múltiplos destinos
- dashboard mais avançado com gráficos e métricas
- exportação de logs em CSV ou JSON

## Licença

Este projeto está sob a licença [MIT](LICENSE).
