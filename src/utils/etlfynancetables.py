
from pandas import read_csv, read_excel
from werkzeug.utils import secure_filename


class RefractorFynance():
    
    def __init__(self, dataframe, filename) -> None:
        self.dataframe = dataframe
        self.filename = filename
        
    def extract_transforme(self):
        df = secure_filename(filename=self.filename)
        if df.endswith(".csv"):
            dftemp = read_csv(df, dtype="object", sep=";")
        elif df.endswith(".xlsx"):
            dftemp = read_excel(df, dtype="object")

        def initcap(s):
            return ' '.join(word.capitalize() for word in s.split())

        dftemp['Tabela'] = dftemp['Tabela'].apply(initcap)
        dftemp['Cod Tabela'] = dftemp['Cod Tabela'].apply(initcap)
        dftemp['Tipo'] = dftemp['Tipo'].apply(initcap)