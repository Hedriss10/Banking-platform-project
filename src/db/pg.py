import os
from typing import Dict, List, Optional

import psycopg2
from psycopg2 import InterfaceError, sql

from src.settings._base import config


class PgAdmin(metaclass=type):

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PgAdmin, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'connect'):
            self.dbname = config.DATABASE
            self.host = config.DB_HOST
            self.user = config.USERNAME
            self.password = config.PASSWORD
            self.port = config.DB_PORT
            self.connect: Optional[psycopg2.extensions.connection] = None

    def connect_postgresql(self):
        if not self.connect:
            try:
                self.connect = psycopg2.connect(
                    dbname=self.dbname,
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    port=self.port
                )
                self.connect.autocommit = True
                print("Conexão estabelecida com sucesso.")
            except Exception as e:
                print(f"Erro ao conectar ao banco de dados: {e}")
                self.connect = None

    def commit(self):
        if self.connect:
            try:
                self.connect.commit()
                print("Transação confirmada com sucesso.")
            except Exception as e:
                print(f"Erro ao confirmar transação: {e}")
                self.connect.rollback()

    def execute_query(self, query: str, params: Optional[Dict] = None, fetch: Optional[str] = None):
        if not self.connect:
            self.connect_postgresql()
        if not self.connect:
            return None  # Retorna None se a conexão falhar
        try:
            with self.connect.cursor() as cursor:
                # Executa a consulta passando os parâmetros, se fornecidos
                cursor.execute(sql.SQL(query), params)
                if fetch == 'all':
                    return cursor.fetchall()
                elif fetch == 'one':
                    return cursor.fetchone()
                else:
                    return None
        except psycopg2.errors.UniqueViolation as e:
            self.connect.rollback()
            raise
        except Exception as e:
            self.connect.rollback()
            raise


    def fetch_to_list(self, query: str) -> List:
        return self._fetch(query, fetch_type='all')
    
    def fetch_to_one(self, query: str) -> List:
        return self._fetch(query, fetch_type='one')

    def fetch_to_dict(self, query: str) -> List[Dict]:
        return self._fetch(query, fetch_type='dict', as_dict=True)
    
    def fetch_to_all(self, query: str) -> List[tuple]:
        return self._fetch(query, fetch_type='all', as_dict=True)

    def _fetch(self, query: str, fetch_type: str = 'all', as_dict: bool = False):
        if not self.connect:
            self.connect_postgresql()
        if not self.connect:
            return []  # Retorna uma lista vazia se a conexão falhar
        try:
            with self.connect.cursor() as cursor:
                cursor.execute(query)
                if fetch_type == 'all':
                    result = cursor.fetchall()
                elif fetch_type == 'dict':
                    result = cursor.fetchall()
                elif fetch_type == 'one':
                    result = cursor.fetchone()
                else:
                    result = None

                if as_dict and result:
                    columns = [desc[0] for desc in cursor.description]
                    
                    if isinstance(result, tuple):
                        result = [result]
                        
                    result = [dict(zip(columns, row)) for row in result]
                return result if result else []
        except InterfaceError as e:
            self.connect_postgresql()
            print(f"Erro de interface, tentando reconectar: {e}")
            raise e
        except Exception as e:
            print(f"Erro ao buscar dados: {e}")
            self.connect.rollback()
            raise
        except psycopg2.errors.UniqueViolation as e:
            self.connect.rollback()
            raise

    def close_connection(self):
        if self.connect:
            try:
                self.connect.close()
                print("Conexão fechada com sucesso.")
            except Exception as e:
                print(f"Erro ao fechar a conexão: {e}")
            finally:
                self.connect = None  # Sempre resetar self.connect
