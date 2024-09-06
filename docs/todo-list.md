### Refatoração


**Login:**

- [] - Ajustar a indentificação de permissões 
- [] - Redefinição de senhas


**Usuário:**

- [] - Configurar rotas dinamicas 
- [] - Gerenciar as variaveis com o nome correto
- [] - Validar acesso em login com permissões 



    {% if not is_login %}
    <header  id="header" class="header fixed-top d-flex align-items-center">
        {% block header %} {% endblock  %}
    </header>

    <aside id="sidebar" class="sidebar">
        {% block aside %} {% endblock %}
    </aside>
    {% endif %}
    {% if not is_login %}
    <main id="main" class="main">
        {% block home %} {% endblock %}
    </main>
    {% endif %}
    {% if not is_login %}
    <footer id="footer" class="footer">
        {% block footer %} {% endblock %}
    </footer>
    {% endif %}




<td row="row">
    <!-- Ajustar para passar o token criptografado -->
    <a href="{{ url_for('proposal.state_details', token=generate_token(p.id)) }}" class="btn btn-info btn-sm">Editar</a>
</td>