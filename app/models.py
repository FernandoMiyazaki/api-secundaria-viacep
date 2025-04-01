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