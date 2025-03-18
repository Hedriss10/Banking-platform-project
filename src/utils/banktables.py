import os
from pandas import read_excel
from pandas import Series
import pandas as pd
from pandas import DataFrame, Series
from typing import Optional
from src.utils.log import logs_and_save_db
from src.service.response import Response


class ExcelTablesBank:

    # helpers for rate 
    def clean_taxa(self, value):
        if pd.isna(value):  # Se o valor for NaN, retorna NaN
            return None
        if isinstance(value, str):
            # Remove o símbolo '%' e substitui ',' por '.'
            value = value.replace("%", "").replace(",", ".")
            # Converte para float
            return float(value)
        return float(value)  # Converte valores numéricos diretamente

    def __init__(self, file_path: str) -> None:
        """
        Initializes the class with the path of the Excel file and contains two functions, 
        one for loading and one for handling `templatestring` so that it can be input into the database.

        :param file_path: path of the .xlsx
        """
        self.xlsx = file_path

    def load_file(self) -> DataFrame:
        """
            Automatically loads the only spreadsheet in the Excel file and redoes the transfer. 
            Contains a print marked in hardcode precisely 
            to make a treatment within the core to make it easier to count the spreadsheets in the document.
        :return: DataFrame with data sheetnames.
        """
        try:
            sheets = pd.read_excel(self.xlsx, sheet_name=None, dtype="object", engine="openpyxl")
            # print(f"O arquivo contém {len(sheets)} planilha(s): {', '.join(sheets.keys())}")
            first_sheet_name = next(iter(sheets))
            return sheets[first_sheet_name]

        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return None

    def processing_pan(self, sheet_data: DataFrame, is_pan: bool) -> DataFrame:
        """
            Process data from Banco Pan, this data is the commission tables, making a treatment, where we can collect the spreadsheet index
            greater than zero, cutting lines and resetting the index, and aggregating the tables, taking the necessary columns, separating the deadlines, treating null values
            renaming the columns, converting and rounding values, formatting as a string with two decimal places and returning the value with `templatestring`
            
        :param sheet_data: DataFrame with data sheetname.
        :return: DataFrame processing with templatestring.
        """
        try:
            if is_pan and len(sheet_data) > 0:
                new_sheet = sheet_data.iloc[6:]  
                new_sheet = new_sheet.reset_index(drop=True)
                new_sheet['Tabela'] = new_sheet[['Unnamed: 4', 'Unnamed: 5']].agg(' '.join, axis=1)

                df_tmp = new_sheet[['Unnamed: 0', 'Unnamed: 1', 'Unnamed: 2', 'Tabela', 'Unnamed: 3', 'Unnamed: 6', 'Unnamed: 9']]

                df_tmp[['Prazo Inicio', 'Prazo Fim']] = df_tmp['Unnamed: 6'].apply(
                    lambda x: x.split('-') if '-' in str(x) else [x, x]
                ).apply(Series)

                df_tmp['Prazo Inicio'] = df_tmp['Prazo Inicio'].fillna('0').astype(str)
                df_tmp['Prazo Fim'] = df_tmp['Prazo Fim'].fillna('0').astype(str)
                df_tmp.rename(columns={
                    'Unnamed: 0': 'Convenio',
                    'Unnamed: 1': 'Empregado',
                    'Unnamed: 2': 'Tipo',
                    'Unnamed: 3': 'Cod Tabela',
                    'Unnamed: 9': 'Flat',
                }, inplace=True)

                df_tmp.loc[:, 'Flat'] = (df_tmp['Flat'].astype(float) * 100).round(2)
                df_tmp.loc[:, 'Flat'] = df_tmp['Flat'].apply(lambda x: f"{x:.2f}")
                
                output_dir = 'TESTANDO'
                os.makedirs(output_dir, exist_ok=True)

                select_convenio = df_tmp['Convenio'].unique()
                for select in select_convenio:
                    df_filtered = df_tmp[df_tmp['Convenio'] == select].copy()
                    dff2 = df_filtered[['Tipo', 'Tabela', 'Cod Tabela', 'Prazo Inicio', 'Prazo Fim', 'Flat']]
                    
                    output_file = os.path.join(output_dir, f"{df_filtered['Empregado'].iloc[0]}.xlsx")
                    
                    dff2.to_excel(output_file, index=False)
                    print(f'Salvo: {output_file}')
            else:
                raise ValueError("Arquivo inválido.")
        
        except Exception as e:
            logs_and_save_db("error", message=f"Error Processing add tables bank pan -> {e}")
            return Response().response(status_code=500, error=True, message_id="error_add_tables", exception=str(e))

    def processing_master(self, is_master: bool, sheet_data: DataFrame) -> DataFrame:
        try:
            if is_master and len(sheet_data) > 0:
                sheet_data.rename(columns={'Unnamed: 1': 'COD_TABLE', 'Unnamed: 2': 'EMPREGADOR', 'Unnamed: 4': 'UF', 'Unnamed: 5': 'Tipo', 
                                'Unnamed: 6': 'Flat 1 a 6', 'Unnamed: 11': 'Flat 1 a 12', 'Unnamed: 16': 'Flat 13 a 24', 'Unnamed: 21': 'Flat 25 a 36', 'Unnamed: 26': 'Flat 37 a 48', 'Unnamed: 31': 'Flat 49 a 60', 
                                'Unnamed: 36': 'Flat 61 a 72', 'Unnamed: 41': 'Flat 73 a 84', 'Unnamed: 46': 'Flat 85 a 96', 'Unnamed: 51': 'Flat 97 a 108', 'Unnamed: 56': 'Flat 109 a 120',}, inplace=True)
                sheet_data = sheet_data.fillna(0)
                new_df = sheet_data[['COD_TABLE', 'EMPREGADOR', 'UF', 'Tipo', 'Flat 1 a 6', 'Flat 1 a 12', 'Flat 13 a 24', 'Flat 25 a 36', 'Flat 37 a 48', 'Flat 49 a 60', 'Flat 61 a 72', 'Flat 73 a 84', 'Flat 85 a 96', 'Flat 97 a 108', 'Flat 109 a 120']]
                new_df = new_df.iloc[8:]
                new_df = new_df.infer_objects(copy=False)
                new_rows = []
                flat_ranges = {
                    'Flat 1 a 6': (1, 6),
                    'Flat 1 a 12': (1, 12),
                    'Flat 13 a 24': (13, 24),
                    'Flat 25 a 36': (25, 36),
                    'Flat 37 a 48': (37, 48),
                    'Flat 49 a 60': (49, 60),
                    'Flat 61 a 72': (61, 72),
                    'Flat 73 a 84': (73, 84),
                    'Flat 85 a 96': (85, 96),
                    'Flat 97 a 108': (97, 108),
                    'Flat 109 a 120': (109, 120),
                }
                
                for index, row in new_df.iterrows():
                    for flat_col, (prazo_inicio, prazo_fim) in flat_ranges.items():
                        if flat_col in new_df.columns and row[flat_col] != 0:
                            valor_flat = round(float(row[flat_col]), 4) * 100
                            new_row = {
                                'Tipo': row['Tipo'],
                                'Tabela': row['EMPREGADOR'],
                                'Cod Tabela': str(row['COD_TABLE']).zfill(5),
                                'UF': row['UF'],
                                'Prazo Inicio': prazo_inicio,
                                'Prazo Fim': prazo_fim,
                                'Flat': f"{valor_flat:.2f}"
                            }
                            new_rows.append(new_row)
                
                new_df = pd.DataFrame(new_rows)
                return new_df
                
            else:
                raise ValueError("Erro ao processar o arquivo: Banco Master")
                
        except Exception as e :
            logs_and_save_db("error", message=f"Error Processing add tables bank master -> {e}")
            Response().response(status_code=500, error=True, message_id="error_add_tables", exception=str(e))

    def processing_safra(self, is_safra: bool, sheet_data: DataFrame) -> DataFrame:
        if is_safra and len(sheet_data) > 0:
            new_sheet = sheet_data[1:].reset_index(drop=True)
            new_sheet.columns = new_sheet.iloc[0]
            new_sheet = new_sheet[1:].reset_index(drop=True)
            new_sheet.columns = range(1, len(new_sheet.columns) + 1)
            new_sheet.rename(
                columns={
                    2: "Convenio",
                    3: "Tabela",
                    4: "Tipo",
                    6: "Prazo Inicio",
                    7: "Prazo Fim",
                    10: "Taxa",
                    15: "Flat"
                },
                inplace=True  # Modifica o DataFrame diretamente
            )

            df2 = new_sheet[["Convenio", "Tabela", "Tipo", "Prazo Inicio", "Prazo Fim", "Taxa", "Flat"]]
            df2 = df2.drop(0).reset_index(drop=True)
            
            df2["Taxa Inicio"] = None
            df2["Taxa Fim"] = None
            
            for index, row in df2.iterrows():
                taxa_value = row["Taxa"]
                if pd.isna(taxa_value):
                    continue
                if isinstance(taxa_value, str) and "-" in taxa_value:
                    # Se o valor contiver '-', divide em "Taxa Inicio" e "Taxa Fim"
                    taxa_inicio, taxa_fim = taxa_value.split("-")
                    df2.at[index, "Taxa Inicio"] = self.clean_taxa(taxa_inicio)
                    df2.at[index, "Taxa Fim"] = self.clean_taxa(taxa_fim)
                else:
                    # Caso contrário, copia o valor para "Taxa Inicio" e "Taxa Fim"
                    taxa_convertida = self.clean_taxa(taxa_value)
                    df2.at[index, "Taxa Inicio"] = taxa_convertida
                    df2.at[index, "Taxa Fim"] = taxa_convertida
            # convert taxa
            df2["Taxa Inicio"] = df2["Taxa Inicio"].astype(float) * 100
            df2["Taxa Fim"] = df2["Taxa Fim"].astype(float) * 100
            df2["Flat"] =  df2["Flat"].astype(float) * 100
            return df2
        else:
            return sheet_data
        
