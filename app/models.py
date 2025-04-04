from datetime import datetime
from .extensions import db


class CepConsulta(db.Model):
    __tablename__ = 'cep_consultas'

    id = db.Column(db.Integer, primary_key=True)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(100), nullable=True)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(50), nullable=True)
    localidade = db.Column(db.String(50), nullable=True)
    uf = db.Column(db.String(2), nullable=True)
    estado = db.Column(db.String(50), nullable=True)
    regiao = db.Column(db.String(50), nullable=True)
    ibge = db.Column(db.String(10), nullable=True)
    gia = db.Column(db.String(10), nullable=True)
    ddd = db.Column(db.String(2), nullable=True)
    siafi = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<CepConsulta {self.cep}>"
        
    def to_dict(self):
        return {
            "cep": self.cep,
            "logradouro": self.logradouro,
            "complemento": self.complemento,
            "bairro": self.bairro,
            "localidade": self.localidade,
            "uf": self.uf,
            "estado": self.estado,
            "regiao": self.regiao,
            "ibge": self.ibge,
            "gia": self.gia,
            "ddd": self.ddd,
            "siafi": self.siafi
        }


class Usuario(db.Model):
    __tablename__ = 'usuarios'

    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    cep = db.Column(db.String(9), nullable=False)
    logradouro = db.Column(db.String(100), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(50), nullable=False)
    localidade = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Usuario {self.nome_completo}>"
    
    def to_dict(self):
        """
        Retorna uma representação do usuário em forma de dicionário para serialização
        """
        return {
            'id': self.id,
            'nome_completo': self.nome_completo,
            'email': self.email,
            'cpf': self.cpf,
            'cep': self.cep,
            'logradouro': self.logradouro,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'localidade': self.localidade,
            'estado': self.estado,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }