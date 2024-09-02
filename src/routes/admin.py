from flask_sqlalchemy import pagination
from flask import Blueprint, render_template, flash, jsonify, abort, request, redirect, url_for
from flask_login import login_required
from src import db
from src.models.user import UserPermission , User, Permission


bp_admin = Blueprint("admin", __name__)

@bp_admin.route("/admin/permissions/bulk", methods=['POST'])
@login_required
def manage_permissions_bulk():
    user_ids = request.form.getlist('user_ids[]')
    print(user_ids)
    for user_id in user_ids:
        permissions = request.form.getlist(f'permissions_{user_id}[]')

        UserPermission.query.filter_by(user_id=user_id).delete()

        for permission_id in permissions:
            new_permission = UserPermission(user_id=user_id, permission_id=permission_id)
            db.session.add(new_permission)

    db.session.commit()
    return redirect(url_for("overview.home"))


@bp_admin.route("/remove-permissions", methods=['POST'])
@login_required
def remove_permissions():
    permissions_to_remove = request.form.getlist('permissions_to_remove[]')
    print("Permissões para remover:", permissions_to_remove)
    
    if permissions_to_remove:
        for permission_id in permissions_to_remove:
            permission = UserPermission.query.filter_by(permission_id=permission_id).first()
            if permission:
                db.session.delete(permission)

        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False)


@bp_admin.route("/get-permissions", methods=['GET'])
@login_required
def index_permission():
    permissions_data = db.session.query(
        UserPermission.permission_id,
        User.username,
        User.type_user_func.label('register_permission'),
        Permission.name.label('permission')
    ).join(User, User.id == UserPermission.user_id)\
     .join(Permission, UserPermission.permission_id == Permission.id)\
     .all()
    users = User.query.all()
    permissions = Permission.query.all()

    return render_template("admin/permissions_admin.html", users=users, permissions=permissions, permissions_data=permissions_data)