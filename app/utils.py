import requests
import re
from flask import current_app

# Mapeamento de UF para região e estado completo
UF_MAPEAMENTO = {
    'AC': {'estado': 'Acre', 'regiao': 'Norte'},
    'AL': {'estado': 'Alagoas', 'regiao': 'Nordeste'},
    'AP': {'estado': 'Amapá', 'regiao': 'Norte'},
    'AM': {'estado': 'Amazonas', 'regiao': 'Norte'},
    'BA': {'estado': 'Bahia', 'regiao': 'Nordeste'},
    'CE': {'estado': 'Ceará', 'regiao': 'Nordeste'},
    'DF': {'estado': 'Distrito Federal', 'regiao': 'Centro-Oeste'},
    'ES': {'estado': 'Espírito Santo', 'regiao': 'Sudeste'},
    'GO': {'estado': 'Goiás', 'regiao': 'Centro-Oeste'},
    'MA': {'estado': 'Maranhão', 'regiao': 'Nordeste'},
    'MT': {'estado': 'Mato Grosso', 'regiao': 'Centro-Oeste'},
    'MS': {'estado': 'Mato Grosso do Sul', 'regiao': 'Centro-Oeste'},
    'MG': {'estado': 'Minas Gerais', 'regiao': 'Sudeste'},
    'PA': {'estado': 'Pará', 'regiao': 'Norte'},
    'PB': {'estado': 'Paraíba', 'regiao': 'Nordeste'},
    'PR': {'estado': 'Paraná', 'regiao': 'Sul'},
    'PE': {'estado': 'Pernambuco', 'regiao': 'Nordeste'},
    'PI': {'estado': 'Piauí', 'regiao': 'Nordeste'},
    'RJ': {'estado': 'Rio de Janeiro', 'regiao': 'Sudeste'},
    'RN': {'estado': 'Rio Grande do Norte', 'regiao': 'Nordeste'},
    'RS': {'estado': 'Rio Grande do Sul', 'regiao': 'Sul'},
    'RO': {'estado': 'Rondônia', 'regiao': 'Norte'},
    'RR': {'estado': 'Roraima', 'regiao': 'Norte'},
    'SC': {'estado': 'Santa Catarina', 'regiao': 'Sul'},
    'SP': {'estado': 'São Paulo', 'regiao': 'Sudeste'},
    'SE': {'estado': 'Sergipe', 'regiao': 'Nordeste'},
    'TO': {'estado': 'Tocantins', 'regiao': 'Norte'}
}


def formatar_cep(cep):
    """
    Remove caracteres não numéricos do CEP e garante que tenha 8 dígitos
    """
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) != 8:
        return None
    return cep_limpo


def consultar_viacep(cep):
    """
    Consulta a API externa do ViaCEP para obter dados de endereço
    """
    cep_formatado = formatar_cep(cep)
    if not cep_formatado:
        return None
    
    try:
        api_url = f"{current_app.config['VIACEP_EXTERNAL_API']}/{cep_formatado}/json/"
        response = requests.get(api_url)
        response.raise_for_status()
        
        data = response.json()
        
        # Verifica se o CEP existe
        if "erro" in data:
            return None
        
        # Adiciona informações extras
        uf = data.get('uf')
        if uf and uf in UF_MAPEAMENTO:
            data['estado'] = UF_MAPEAMENTO[uf]['estado']
            data['regiao'] = UF_MAPEAMENTO[uf]['regiao']
        
        return data
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Erro ao consultar ViaCEP: {str(e)}")
        return None
    except ValueError as e:
        current_app.logger.error(f"Erro ao processar resposta do ViaCEP: {str(e)}")
        return None


def validar_email(email):
    """
    Valida se o email está em um formato correto
    """
    # Implementação básica, pode ser expandida
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def validar_cpf(cpf):
    """
    Valida se o CPF é válido
    """
    # Remove caracteres não numéricos
    cpf = re.sub(r'\D', '', cpf)
    
    # Verifica se tem 11 dígitos
    if len(cpf) != 11:
        return False
    
    # Verifica se todos os dígitos são iguais
    if cpf == cpf[0] * 11:
        return False
    
    # Validação do primeiro dígito verificador
    soma = 0
    peso = 10
    for i in range(9):
        soma += int(cpf[i]) * peso
        peso -= 1
    
    resto = soma % 11
    digito1 = 0 if resto < 2 else 11 - resto
    
    if int(cpf[9]) != digito1:
        return False
    
    # Validação do segundo dígito verificador
    soma = 0
    peso = 11
    for i in range(10):
        soma += int(cpf[i]) * peso
        peso -= 1
    
    resto = soma % 11
    digito2 = 0 if resto < 2 else 11 - resto
    
    return int(cpf[10]) == digito2