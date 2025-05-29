# src/utils/metadata.py
import json

from sqlalchemy.engine.row import Row
from sqlalchemy.inspection import inspect


class Metadata:
    def __init__(self, objects):
        self.objects = objects

    def model_to_dict(self, obj=None):
        obj = obj or self.objects
        # Caso seja resultado de SELECT (Row)
        if isinstance(obj, Row):
            return dict(obj._mapping)

        # Caso seja uma tupla simples, tenta converter manualmente
        if isinstance(obj, tuple):
            return {f"col_{i}": value for i, value in enumerate(obj)}

        # Caso seja uma instância ORM
        try:
            return {
                c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs
            }
        except Exception:
            raise ValueError(
                f"Não foi possível converter objeto: {obj}. Tipo: {type(obj)}"
            )

    def model_to_list(self):
        if isinstance(self.objects, list):
            if all(isinstance(obj, Row) for obj in self.objects):
                return [dict(obj._mapping) for obj in self.objects]
            if all(isinstance(obj, tuple) for obj in self.objects):
                return [self.model_to_dict(obj) for obj in self.objects]
            return [self.model_to_dict(obj) for obj in self.objects]
        elif self.objects:
            return [self.model_to_dict(self.objects)]
        return []

    def model_to_json(self):
        return json.dumps(self.model_to_list(), default=str)

    def model_instance_to_dict_get_id(self):
        if hasattr(self.objects, "__table__"):
            return {
                column.name: getattr(self.objects, column.name)
                for column in self.objects.__table__.columns
            }
        raise ValueError(
            "Objeto não possui __table__ para extração de colunas."
        )


def model_to_dict(model):
    """Converte um modelo SQLAlchemy em dicionário sem campos internos."""
    return {
        column.name: getattr(model, column.name)
        for column in model.__table__.columns
    }


def model_to_json(model):
    """Converte um modelo SQLAlchemy em JSON sem campos internos."""
    return model_to_dict(model)


def model_to_list(model):
    """Converte um modelo SQLAlchemy em uma lista sem campos internos."""
    return [model_to_dict(model)]


def model_instance_to_dict(model):
    return [
        {
            column.name: getattr(item, column.name)
            for column in item.__table__.columns
        }
        for item in model
    ]


# Para uma lista de objetos
def model_list_to_dict(instances):
    return [model_instance_to_dict(instance) for instance in instances]


def model_instance_to_dict_get_id(instance):
    return {
        column.name: getattr(instance, column.name)
        for column in instance.__table__.columns
    }
