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

new_user = User('<args>')
db.session.add(new_user)
db.session.commit()

```