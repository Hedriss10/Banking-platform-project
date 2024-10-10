### Flask App


### export comands for cli terminal with Flask
```bash
export FLASK_APP=src:create_app # create app
```

### Create app export database envirion management `developement`

```bash 
# init dabase
flask db init 
flask db -m migrate "init database"
flask db upgrade
```

### Commands to run the application Flask 

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


### CI/CD
`python-app.yml`

```bash
name: CI/CD Workflow

on:
  push:
    branches:
      - main
  pull_request:
    branches:
      - main

jobs:
  build-and-test:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov coverage

    - name: Run tests with coverage
      run: |
        source venv/bin/activate
        pytest --cov=src --cov-report=term-missing

    - name: Report coverage
      run: |
        source venv/bin/activate
        coverage report

```

## 


### Create User fake with `insert_users_fake.py`

**Application to create test users**

```python
# ./script
    python3 insert_users_fake.py
```


### Initi tmux with Flask


**Tmux application**

```bash
# init tmux
tmux new -s flask_app
```

```bash
# load init
tmux attach -t flask_app
```


