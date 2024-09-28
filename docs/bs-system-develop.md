## export comands for cli terminal with Flask

```bash
export FLASK_APP=src/external.py:create_app
export DEBUG=True
export APP_SETTINGS=config.DevelopmentConfig
export FLASK_APP=src
export FLASK_DEBUG=1
```

## Create app in cli with Flask

```bash
# export app flask
export FLASK_APP=src:create_app
flask db init 
flask db -m migrate "init database"
flask db upgrade
```

<hr>

## Flask cli create user

```python
from src import db
from src.models.bsmodels import User


new_user = User(user_identification=40028922, username='hedris', lastname='pereira', email='test@gmail.com', type_user_func='Administrador', typecontract='Funcionario', password='40028922')
db.session.add(new_user)
db.session.commit()
```


### comands exec app flask 

`development`
```bash
export FLASK_ENV=development
flask run
```

`production`
```bash
export FLASK_ENV=production
flask run --host=0.0.0.0 --port=7500
```


`testing`

```bash
export FLASK_ENV=testing
flask run
```