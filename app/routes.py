from flask import Blueprint, request
from flask_restx import Resource, fields
from sqlalchemy.exc import IntegrityError
from .extensions import db, api
from .models import CepConsulta, Usuario
from .utils import consultar_viacep, formatar_cep, validar_cpf, validar_email

# Blueprint
main = Blueprint('main', __name__)

# Namespaces
ns_cep = api.namespace('cep', description='Operações relacionadas a CEP')
ns_usuarios = api.namespace('usuarios', description='Operações relacionadas a usuários')

# Models
cep_model = api.model('CEP', {
    'cep': fields.String(description='CEP no formato 00000-000'),
    'logradouro': fields.String(description='Nome da rua, avenida, etc'),
    'complemento': fields.String(description='Complemento, se houver'),
    'bairro': fields.String(description='Bairro'),
    'localidade': fields.String(description='Cidade'),
    'uf': fields.String(description='Unidade Federativa (sigla)'),
    'estado': fields.String(description='Nome do estado'),
    'regiao': fields.String(description='Região do Brasil'),
    'ibge': fields.String(description='Código IBGE'),
    'gia': fields.String(description='Código GIA'),
    'ddd': fields.String(description='DDD da região'),
    'siafi': fields.String(description='Código SIAFI')
})

usuario_model = api.model('Usuario', {
    'id': fields.Integer(readonly=True, description='ID único do usuário'),
    'nome_completo': fields.String(required=True, description='Nome completo do usuário'),
    'email': fields.String(required=True, description='Email do usuário'),
    'cpf': fields.String(required=True, description='CPF do usuário'),
    'cep': fields.String(required=True, description='CEP do usuário'),
    'complemento': fields.String(description='Complemento do endereço'),
    'logradouro': fields.String(readonly=True, description='Logradouro'),
    'bairro': fields.String(readonly=True, description='Bairro'),
    'localidade': fields.String(readonly=True, description='Cidade'),
    'estado': fields.String(readonly=True, description='Estado')
})


@ns_cep.route('/<string:cep>')
@ns_cep.param('cep', 'CEP a ser consultado')
class CepResource(Resource):
    @ns_cep.doc('get_cep')
    @ns_cep.response(200, 'Sucesso', cep_model)
    @ns_cep.response(404, 'CEP não encontrado')
    @ns_cep.response(400, 'CEP inválido')
    def get(self, cep):
        """Consulta um CEP e retorna os dados de endereço (sem persistir)"""
        cep_formatado = formatar_cep(cep)
        if not cep_formatado:
            return {'message': 'CEP inválido'}, 400
        
        # Verifica se já existe no banco de dados
        consulta_existente = CepConsulta.query.filter_by(cep=cep_formatado).first()
        
        if consulta_existente:
            return consulta_existente.to_dict()
        
        # Se não existir, consulta a API externa
        endereco = consultar_viacep(cep_formatado)
        
        if not endereco:
            return {'message': 'CEP não encontrado'}, 404
        
        # Retorna os dados sem persistir no banco
        return endereco
    
    @ns_cep.doc('post_cep')
    @ns_cep.response(201, 'Consulta salva', cep_model)
    @ns_cep.response(404, 'CEP não encontrado')
    @ns_cep.response(400, 'CEP inválido')
    def post(self, cep):
        """Consulta um CEP e persiste os dados no banco"""
        cep_formatado = formatar_cep(cep)
        if not cep_formatado:
            return {'message': 'CEP inválido'}, 400
        
        # Consulta a API externa (sempre consultamos, mesmo se existir no banco)
        endereco = consultar_viacep(cep_formatado)
        
        if not endereco:
            return {'message': 'CEP não encontrado'}, 404
        
        # Salva no banco de dados (sempre cria um novo registro)
        try:
            nova_consulta = CepConsulta(
                cep=endereco.get('cep', '').replace('-', ''),
                logradouro=endereco.get('logradouro', ''),
                complemento=endereco.get('complemento', ''),
                bairro=endereco.get('bairro', ''),
                localidade=endereco.get('localidade', ''),
                uf=endereco.get('uf', ''),
                estado=endereco.get('estado', ''),
                regiao=endereco.get('regiao', ''),
                ibge=endereco.get('ibge', ''),
                gia=endereco.get('gia', ''),
                ddd=endereco.get('ddd', ''),
                siafi=endereco.get('siafi', '')
            )
            
            db.session.add(nova_consulta)
            db.session.commit()
            
            return endereco, 201
        except Exception as e:
            db.session.rollback()
            api.logger.error(f"Erro ao salvar consulta: {str(e)}")
            return {'message': f'Erro ao salvar consulta: {str(e)}'}, 500


@ns_cep.route('/')
class CepList(Resource):
    @ns_cep.doc('list_ceps')
    @ns_cep.marshal_list_with(cep_model)
    def get(self):
        """Lista todas as consultas de CEP realizadas"""
        consultas = CepConsulta.query.all()
        return [consulta.to_dict() for consulta in consultas]


@ns_cep.route('/<int:id>')
@ns_cep.param('id', 'ID da consulta')
class CepRecordResource(Resource):
    @ns_cep.doc('delete_cep')
    @ns_cep.response(204, 'Consulta excluída')
    @ns_cep.response(404, 'Consulta não encontrada')
    def delete(self, id):
        """Exclui uma consulta salva do banco de dados"""
        consulta = CepConsulta.query.get_or_404(id)
        
        try:
            db.session.delete(consulta)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao excluir consulta: {str(e)}'}, 400


@ns_cep.route('/<int:id>/<string:complemento>')
@ns_cep.param('id', 'ID da consulta')
@ns_cep.param('complemento', 'Complemento a ser atualizado')
class CepUpdateResource(Resource):
    @ns_cep.doc('update_complemento')
    @ns_cep.response(200, 'Complemento atualizado', cep_model)
    @ns_cep.response(404, 'Consulta não encontrada')
    def put(self, id, complemento):
        """Atualiza o complemento de uma consulta salva"""
        consulta = CepConsulta.query.get_or_404(id)
        
        try:
            # Atualiza apenas o complemento
            consulta.complemento = complemento
            
            db.session.commit()
            return consulta.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao atualizar complemento: {str(e)}'}, 400


@ns_usuarios.route('/')
class UsuarioList(Resource):
    @ns_usuarios.doc('list_usuarios')
    @ns_usuarios.marshal_list_with(usuario_model)
    def get(self):
        """Lista todos os usuários"""
        usuarios = Usuario.query.all()
        return [usuario.to_dict() for usuario in usuarios]

    @ns_usuarios.doc('create_usuario',
                  params={
                     'nome_completo': 'Nome completo do usuário',
                     'email': 'Email do usuário',
                     'senha': 'Senha do usuário',
                     'cpf': 'CPF do usuário',
                     'cep': 'CEP do usuário',
                     'complemento': 'Complemento do endereço (opcional)'
                  })
    @ns_usuarios.response(201, 'Usuário criado com sucesso', usuario_model)
    @ns_usuarios.response(400, 'Dados inválidos')
    @ns_usuarios.response(409, 'Email ou CPF já existente')
    def post(self):
        """Cria um novo usuário"""
        # Obtém os dados dos parâmetros
        nome_completo = request.args.get('nome_completo')
        email = request.args.get('email')
        senha = request.args.get('senha')
        cpf = request.args.get('cpf')
        cep = request.args.get('cep')
        complemento = request.args.get('complemento', '')
        
        # Verifica se os campos obrigatórios estão presentes
        if not nome_completo:
            return {'message': 'Campo obrigatório ausente: nome_completo'}, 400
        if not email:
            return {'message': 'Campo obrigatório ausente: email'}, 400
        if not senha:
            return {'message': 'Campo obrigatório ausente: senha'}, 400
        if not cpf:
            return {'message': 'Campo obrigatório ausente: cpf'}, 400
        if not cep:
            return {'message': 'Campo obrigatório ausente: cep'}, 400
        
        # Validação do email
        if not validar_email(email):
            return {'message': 'Email inválido'}, 400
            
        # Validação do CPF
        if not validar_cpf(cpf):
            return {'message': 'CPF inválido'}, 400
        
        # Consulta o CEP
        cep_formatado = formatar_cep(cep)
        if not cep_formatado:
            return {'message': 'CEP inválido'}, 400
            
        endereco = consultar_viacep(cep_formatado)
        if not endereco or 'erro' in endereco:
            return {'message': 'CEP inválido ou não encontrado'}, 400
        
        try:
            novo_usuario = Usuario(
                nome_completo=nome_completo,
                email=email,
                senha=senha,  # Em produção, deve-se usar hash
                cpf=cpf,
                cep=cep_formatado,
                logradouro=endereco['logradouro'],
                complemento=complemento,
                bairro=endereco['bairro'],
                localidade=endereco['localidade'],
                estado=endereco['estado']
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            
            return novo_usuario.to_dict(), 201
            
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Email ou CPF já cadastrado'}, 409
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao criar usuário: {str(e)}'}, 400


@ns_usuarios.route('/<int:id>')
@ns_usuarios.response(404, 'Usuário não encontrado')
@ns_usuarios.param('id', 'ID do usuário')
class UsuarioResource(Resource):
    @ns_usuarios.doc('get_usuario')
    @ns_usuarios.marshal_with(usuario_model)
    def get(self, id):
        """Obtém os dados de um usuário específico"""
        usuario = Usuario.query.get_or_404(id)
        return usuario.to_dict()

    @ns_usuarios.doc('update_usuario',
                  params={
                     'nome_completo': 'Nome completo do usuário',
                     'email': 'Email do usuário',
                     'senha': 'Senha do usuário',
                     'cep': 'CEP do usuário',
                     'complemento': 'Complemento do endereço'
                  })
    @ns_usuarios.marshal_with(usuario_model)
    def put(self, id):
        """Atualiza os dados de um usuário"""
        usuario = Usuario.query.get_or_404(id)
        
        # Obtém os dados dos parâmetros
        nome_completo = request.args.get('nome_completo')
        email = request.args.get('email')
        senha = request.args.get('senha')
        cep = request.args.get('cep')
        complemento = request.args.get('complemento')
        
        # Atualiza os campos fornecidos
        if nome_completo:
            usuario.nome_completo = nome_completo
        if email:
            if not validar_email(email):
                return {'message': 'Email inválido'}, 400
            usuario.email = email
        if senha:
            usuario.senha = senha  # Em produção, deve-se usar hash
        if cep:
            cep_formatado = formatar_cep(cep)
            if not cep_formatado:
                return {'message': 'CEP inválido'}, 400
                
            # Se o CEP foi atualizado, consulta novamente
            endereco = consultar_viacep(cep_formatado)
            if not endereco or 'erro' in endereco:
                return {'message': 'CEP inválido ou não encontrado'}, 400
            
            usuario.cep = cep_formatado
            usuario.logradouro = endereco['logradouro']
            usuario.bairro = endereco['bairro']
            usuario.localidade = endereco['localidade']
            usuario.estado = endereco['estado']
        
        if complemento is not None:  # Permite atualizar para string vazia
            usuario.complemento = complemento
        
        try:
            db.session.commit()
            return usuario.to_dict()
        except IntegrityError:
            db.session.rollback()
            return {'message': 'Email já cadastrado para outro usuário'}, 409
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao atualizar usuário: {str(e)}'}, 400

    @ns_usuarios.doc('delete_usuario')
    @ns_usuarios.response(204, 'Usuário excluído')
    def delete(self, id):
        """Exclui um usuário"""
        usuario = Usuario.query.get_or_404(id)
        
        try:
            db.session.delete(usuario)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao excluir usuário: {str(e)}'}, 400