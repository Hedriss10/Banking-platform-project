import pandas as pd

data = {
    "Tipo": ["Comissoes"],
    "Detalhamento": ["CREDITO DE COMISSAO"],
    "Ponto de Venda": [6240],
    "Nome Ponto de Venda": ["BSC4 PROMOTORA DE VE"],
    "Agente": ["000021"],
    "Nome Agente": ["HELENILDA SOUSA VIANA"],
    "Conveniada": ["INSS DATAPREV"],
    "Produto": ["CONSIGNACAO EM FOLHA INSS"],
    "Data Digitação": ["08/04/2024"],
    "Data Emissão": ["09/04/2024"],
    "Contrato": [13345677],
    "CPF": ["06472580183"],
    "proposta": ["40028922"],
    "Nome": ["NEUZA DE OLIVEIRA FULY"],
    "Prazo": [84],
    "Parcelas em Aberto": [84],
    "PMT": [404],
    "Valor Operação": [18065.55],
    "Valor Base": [836.88],
    "% IRRF": [0],
    "Valor IRRF": [0],
    "% ISSQN": [0],
    "Valor ISSQN": [0],
    "Valor RCO": [0],
    "Valor Comissão": [50.21],
    "Plano": ["KFMX"],
    "Nome Plano": ["FLEX I REFIN CARTEIRA"],
    "% Comissão": [6],
    "Sit. Comissão": ["P"],
    "Bloqueio": ["B"],
    "Data Liberação": ["10/04/2024"],
    "Data Pagamento": [None],
    "Tipo Operação": ["REFIN"],
    "Login Agente": ["6240HELENI"],
    "Débito OP": ["N"],
    "Contrato Portado": [None],
    "Paperless": ["Sim"]
}

df = pd.DataFrame(data)

df.to_excel("report_banker.xlsx", index=False)
