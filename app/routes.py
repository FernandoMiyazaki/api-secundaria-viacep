from flask import Blueprint, request, jsonify
from flask_restx import Resource, fields
from .extensions import db, api
from .models import CepConsulta
from .utils import consultar_viacep, formatar_cep

# Blueprint
main = Blueprint('main', __name__)

# Namespace
ns_cep = api.namespace('cep', description='Operações relacionadas a CEP')

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

cep_input = api.model('CEPInput', {
    'cep': fields.String(required=True, description='CEP a ser consultado')
})


@ns_cep.route('/<string:cep>')
@ns_cep.param('cep', 'CEP a ser consultado')
class CepResource(Resource):
    @ns_cep.doc('get_cep')
    @ns_cep.response(200, 'Sucesso', cep_model)
    @ns_cep.response(404, 'CEP não encontrado')
    @ns_cep.response(400, 'CEP inválido')
    def get(self, cep):
        """Consulta um CEP e retorna os dados de endereço"""
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
        
        # Salva no banco de dados
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
            
            return endereco
        except Exception as e:
            db.session.rollback()
            api.logger.error(f"Erro ao salvar consulta: {str(e)}")
            return endereco  # Retorna os dados mesmo em caso de erro ao salvar


@ns_cep.route('/')
class CepList(Resource):
    @ns_cep.doc('create_cep')
    @ns_cep.expect(cep_input)
    @ns_cep.response(200, 'Sucesso', cep_model)
    @ns_cep.response(404, 'CEP não encontrado')
    @ns_cep.response(400, 'CEP inválido')
    def post(self):
        """Consulta um CEP via POST e retorna os dados de endereço"""
        data = request.json
        
        if not data or 'cep' not in data:
            return {'message': 'CEP não informado'}, 400
        
        cep = data['cep']
        cep_formatado = formatar_cep(cep)
        
        if not cep_formatado:
            return {'message': 'CEP inválido'}, 400
        
        # Delega para o método GET
        return CepResource().get(cep_formatado)
        
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
    
    @ns_cep.doc('update_cep')
    @ns_cep.response(200, 'Consulta atualizada', cep_model)
    @ns_cep.response(404, 'Consulta não encontrada')
    def put(self, id):
        """Atualiza uma consulta com base na API externa"""
        consulta = CepConsulta.query.get_or_404(id)
        
        # Consulta novamente a API externa
        endereco = consultar_viacep(consulta.cep)
        
        if not endereco:
            return {'message': 'Erro ao consultar API externa'}, 400
        
        try:
            # Atualiza os campos
            consulta.logradouro = endereco.get('logradouro', '')
            consulta.complemento = endereco.get('complemento', '')
            consulta.bairro = endereco.get('bairro', '')
            consulta.localidade = endereco.get('localidade', '')
            consulta.uf = endereco.get('uf', '')
            consulta.ibge = endereco.get('ibge', '')
            consulta.gia = endereco.get('gia', '')
            consulta.ddd = endereco.get('ddd', '')
            consulta.siafi = endereco.get('siafi', '')
            consulta.estado = endereco.get('estado', '')
            consulta.regiao = endereco.get('regiao', '')
            
            db.session.commit()
            return consulta.to_dict()
        except Exception as e:
            db.session.rollback()
            return {'message': f'Erro ao atualizar consulta: {str(e)}'}, 400