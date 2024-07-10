from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from schemas.error import ErrorSchema
from schemas.ingredientes import IngredienteBuscaSchema, IngredientesDelSchema, IngredientesSchema, IngredientesViewSchema, apresenta_ingredientes
from schemas.receita import ListagemReceitasSchema, ReceitaBuscaSchema, ReceitaDelSchema, ReceitaSchema, ReceitaViewSchema, apresenta_receita, apresenta_receitas
from sqlalchemy.exc import IntegrityError

from model import Session, Receita, Ingredientes
from logger import logger
from flask_cors import CORS

info = Info(title="Minha API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(
    name="Documentação",
    description="Seleção de documentação: Swagger, Redoc ou RapiDoc",
)
receita_tag = Tag(
    name="Receita", description="Adição, visualização e remoção de receitas culinárias"
)
ingredientes_tag = Tag(
    name="Ingredientes", description="Adição de ingredientes a receitas inserida a base"
)


@app.get("/", tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação."""
    return redirect("/openapi")


@app.post(
    "/receita",
    tags=[receita_tag],
    responses={"200": ReceitaViewSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def add_receita(form: ReceitaSchema):
    """Adiciona uma nova receita à base de dados"""
    receita = Receita(
        titulo=form.titulo,
        status=form.status,
        preparo=form.preparo,
        categoria=form.categoria,
    )

    logger.debug(f"Adicionando receita de nome: '{receita.titulo}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando receita
        session.add(receita)
        # efetivando o camando de adição de novo item na tabela
        session.commit()

        logger.debug(f"Adicionado receita de nome: '{receita.id}'")
        return apresenta_receita(receita), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Receita de mesmo titulo já salvo na base :/"
        logger.warning(f"Erro ao adicionar receita'{receita.titulo}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar produto '{receita.titulo}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.put(
    "/receita",
    tags=[receita_tag],
    responses={"200": ReceitaViewSchema, "409": ErrorSchema, "400": ErrorSchema},
)
def update_receita(form: ReceitaSchema):
    """Adiciona uma nova receita à base de dados"""
    logger.info(f"titulo: '{form.titulo}'")
    logger.info(f"status: '{form.status}'")
    logger.info(f"preparo: '{form.preparo}'")

    receita_titulo = form.titulo

    logger.debug(f"Coletando dados sobre receita #{receita_titulo}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    receita = session.query(Receita).filter(Receita.titulo == receita_titulo).first()

    if not receita:
        # se o produto não foi encontrado
        error_msg = "Receita não encontrado na base :/"
        logger.warning(f"Erro ao buscar receita '{receita_titulo}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.info(f"Receita econtrado: '{receita.titulo}'")
        receita.status = form.status
        receita.preparo = form.preparo
        receita.categoria = form.categoria

        # efetivando o camando de adição de novo item na tabela
        session.commit()
        # retorna a representação de produto
        return apresenta_receita(receita), 200
        # return apresenta_ingredientes(ingredientes), 200


@app.get(
    "/receitas",
    tags=[receita_tag],
    responses={"200": ListagemReceitasSchema, "404": ErrorSchema},
)
def get_receitas():
    """Faz a busca por todas as receitas cadastradas

    Retorna uma lista de receitas cadastradas.
    """
    logger.debug(f"Coletando dados sobre receita ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    receitas = session.query(Receita).all()

    if not receitas:
        # se a receita não foi encontrado
        return {"receitas": []}, 200
    else:
        logger.debug(f"%d  Receita econtrada:" % len(receitas))
        print(receitas)
        # retorna a representação da receita
        return apresenta_receitas(receitas), 200


@app.get(
    "/receita",
    tags=[receita_tag],
    responses={"200": ReceitaViewSchema, "404": ErrorSchema},
)
def get_receita(query: ReceitaBuscaSchema):
    """Faz a busca por uma Receita a partir do título informado. O id é utilizado internamente para buscar os ingredientes


    Retorna uma representação das receitas.
    """
    receita_titulo = query.titulo
    receita_id = query.id

    logger.debug(f"Coletando dados sobre receita #{receita_titulo}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    receita = session.query(Receita).filter(Receita.titulo == receita_titulo).first()

    ingredientes = session.query(Ingredientes).filter(
        Ingredientes.receita == receita_id
    )

    if not receita:
        # se o produto não foi encontrado
        error_msg = "Receita não encontrado na base :/"
        logger.warning(f"Erro ao buscar receita '{receita_titulo}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Receita econtrado: '{receita.titulo}'")
        logger.debug(f"Ingredientes econtrado: '{ingredientes}'")
        # retorna a representação de produto
        return apresenta_receita(receita), 200
    # return apresenta_ingredientes(ingredientes), 200


@app.delete(
    "/receita",
    tags=[receita_tag],
    responses={"200": ReceitaDelSchema, "404": ErrorSchema},
)
def del_receita(query: ReceitaBuscaSchema):
    """Deleta uma Receita a partir do título informado

    Retorna uma mensagem de confirmação da remoção.
    """
    receita_nome = unquote(unquote(query.titulo))

    print(receita_nome)
    logger.debug(f"Deletando dados sobre receita #{receita_nome}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Receita).filter(Receita.titulo == receita_nome).delete()

    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado receita #{receita_nome}")
        return {"mesage": "Receita removida", "Título": receita_nome}
    else:
        # se o produto não foi encontrado
        error_msg = "Receita não encontrado na base :/"
        logger.warning(f"Erro ao deletar receita #'{receita_nome}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.delete(
    "/ingrediente",
    tags=[receita_tag],
    responses={"200": IngredientesDelSchema, "404": ErrorSchema},
)
def del_ingrediente(query: IngredienteBuscaSchema):
    """Deleta um Ingrediente a partir da descrição(nome) informado e ID da receita que ele pertence.

    Retorna uma mensagem de confirmação da remoção.
    """
    ingrediente_descricao = unquote(unquote(query.descricao))
    receita_id = unquote(unquote(query.receita))

    print(ingrediente_descricao)
    logger.debug(f"Deletando dados sobre ingredientes #{ingrediente_descricao}")
    # criando conexão com a base
    session = Session()

    # fazendo a remoção
    count = (
        session.query(Ingredientes)
        .filter(
            Ingredientes.descricao == ingrediente_descricao
            and Ingredientes.receita == receita_id
        )
        .delete()
    )

    logger.info(f"Ingrediente #{ingrediente_descricao}")

    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado ingrediente #{ingrediente_descricao}")
        return {"mesage": "Ingrediente removido", "Título": ingrediente_descricao}
    else:
        # se o produto não foi encontrado
        error_msg = "Ingrediente não encontrado na base :/"
        logger.warning(
            f"Erro ao deletar ingrediente #'{ingrediente_descricao}', {error_msg}"
        )
        return {"mesage": error_msg}, 404


@app.post(
    "/ingrediente",
    tags=[ingredientes_tag],
    responses={"200": IngredientesViewSchema, "404": ErrorSchema},
)
def add_ingrediente(form: IngredientesSchema):
    """Adiciona novo ingrediente a receita cadastrada na base identificado pelo id

    Retorna uma representação das receitas e ingredientes associados.
    """

    ingredientes = Ingredientes(
        descricao=form.descricao,
        quantidade=form.quantidade,
        unidade_medida=form.unidade_medida,
        receita=form.receita_id,
    )

    logger.debug(f"Adicionando ingrediente de nome: '{ingredientes.descricao}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando receita
        session.add(ingredientes)
        # efetivando o camando de adição de novo item na tabela
        session.commit()

        logger.debug(f"Adicionado ingrediente de nome: '{ingredientes.descricao}'")
        return apresenta_ingredientes(ingredientes), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Receita de mesmo titulo já salvo na base :/"
        logger.warning(f"Erro ao adicionar receita'{ingredientes.titulo}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(
            f"Erro ao adicionar produto '{ingredientes.descricao}', {error_msg}"
        )
        return {"mesage": error_msg}, 400