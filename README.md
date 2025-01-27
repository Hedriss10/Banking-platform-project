# Backend Athenas ™️


###  Tecnologias utilizadas na paltaforma 💻
- Flask
- PostgreSQL
- Flask-SQLAlchemy
- Flaskrestx
- Docker
- Gunicorn

## Backend Athenas

**Gestão de APIs para users e login:**
Este projeto é responsável por gerenciar as operações e integrações relacionadas a login da plataforma e gestão de usuários.

## Estrutura de Diretórios

Abaixo está a estrutura do diretório principal do projeto e uma breve descrição de cada arquivo/pasta:


```textplain 
├── Dockerfile.dev          # Configuração do Docker para empacotamento de dev
├── Dockerfile.prd          # Configuração do Docker para empacotamento de prd
├── requirements            # Configuração dos requirements tanto para prd ou dev ou test
├── README.md               # Documentação do projeto
├── docker-compose.yml      # Configuração do Docker Compose para serviços auxiliares
├── src/                    # Código-fonte principal da aplicação
│   ├── __init__.py         # Inicialização do módulo
│   └── ...
├── python3 manage.py       # Gerenciamento de execução do projeto
```

## instalando o projeto:
```bash
# configurando ambiente e instalando as dependencias de desenvolvimento ou produção
python3 -m venv .venv
cd ./requirements pip3 install -r dev.txt 
cd ./requirements pip3 install -r prd.txt
```

## Executando o projeto
```bash
python3 manage.py
```

----

## Docker

**Comando para gerar a imagem com arm64 para linux:**
```bash
docker buildx build --platform linux/arm64,linux/amd64 -f Dockerfile.dev -t platform-athenas:dev --load .
```

**Salvando imagem de desenvolvimento para importar para o portainer:**
```bash
docker save -o platform-athenas-app.tar platform-athenas:dev 
```

**Salvando imagem de produção para importar para o portainer:**
```bash
docker save -o platform-athenas-app.tar platform-athenas:prd 
```

**Executando via docker**
```bash
docker run --rm -it -p 5001:5001 platform-athenas:dev
```

**Comando do TAR**

```bash
tar --exclude=".DS_Store" --exclude="__MACOSX" -czvf platform-athenas.tar src .gitignore Dockerfile.dev docker-compose.yml manage.py
```


## Docker para arquitetura x86

Para gerar imagem de produção so alterar o `dockerfile.dev` para `dockerfile.prd` e setar novo nome para imagem.


**Criando o buildx build, importando: FROM python:3.12-slim**
```bash
docker buildx create --name mybuilder --use
docker buildx inspect --bootstrap
```

**Gerando a imagem**
```bash
docker buildx build --platform linux/amd64 -f Dockerfile.dev -t platform-athenas:x86 --load .
```

**Salvando a imagem**
```bash
docker save -o platform-athenas-x86.tar platform-athenas:x86
```

**Executando para testes**
```bash
docker run --rm -it -p 5001:5001 platform-athenas:x86
```

**Executando o build da imagem**
```bash
docker-compose up --build
```

## Gunicorn 

```bash
gunicorn -w 4 -b 0.0.0.0:5001 'src:create_app()'
```