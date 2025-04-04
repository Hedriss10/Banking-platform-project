# src/utils/metadata.py


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