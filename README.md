# Minhas Receitas API

Este projeto visa modernizar o tradicional caderno de receitas, permitindo aos usuários armazenar suas receitas favoritas através de uma API desenvolvida como parte do módulo de Arquitetura de Software da pós-graduação em Engenharia de Software.

---
## Como executar 


Será necessário ter todas as bibliotecas python listadas no `requirements.txt` instaladas.
Após clonar o repositório, é necessário ir ao diretório raiz, pelo terminal, para poder executar os comandos descritos abaixo.

> É fortemente indicado o uso de ambientes virtuais, como o [virtualenv](https://virtualenv.pypa.io/en/latest/).

Para criar e ativar o ambiente virtual, execute os seguintes comandos:

$ python -m venv env
$ env\Scripts\activate

```
$ pip install -r requirements.txt
```

Este é o comando para instalar as dependências descritas no arquivo `requirements.txt`.

### Executando o servidor utilizando o Flask
Para executar a API, execute o comando:

```
$ flask run --host 0.0.0.0 --port 5000
```

Para executar a API em modo de desenvolvimento, execute o comando:

```
$ flask run --host 0.0.0.0 --port 5000 --reload
```
---
### Acesso no browser

Abra o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador para verificar a API em execução.

---
## Executando através do Docker

Certifique-se de ter o [Docker](https://docs.docker.com/engine/install/) instalado e em execução na sua máquina.

Navegue no terminal até o diretório que possui o Dockerfile e o requirements.txt.
Execute **como administrador** o seguinte comando para construir a imagem Docker:
```
$ docker build -t minhas-receitas-api .  
```
Uma vez criada a imagem, para executar o container basta executar, **como administrador**, seguinte o comando:

```
$ docker run -p 5000:5000 minhas-receitas-api
```
Uma vez executando, para acessar a API, basta abrir o [http://localhost:5000/#/](http://localhost:5000/#/) no navegador.