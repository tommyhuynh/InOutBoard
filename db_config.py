#import sys
#import os
#sys.path.append(os.path.abspath('../InOutBoard/instance'))
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


app = Flask(__name__)
db = SQLAlchemy(app)
app.config.from_envvar('INOUTBOARD_SETTINGS', silent=False)

class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.String, primary_key=True, unique=True)
    name = db.Column(db.String, unique=False)
    url = db.Column(db.String, nullable=False, unique=False)
    #email = db.Column(db.String, nullable=True, unique=True)

    in_out = db.Column(db.Boolean(), nullable=True, default=True)
    msg = db.Column(db.String, default='')

    first_name = db.Column(db.String(100), nullable=True, server_default='')
    last_name = db.Column(db.String(100), nullable=True, server_default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='')

    roles = db.relationship('Role', secondary='user_roles', passive_deletes=True,
                                 backref=db.backref('roles',lazy='dynamic'))

    def is_in(self):
        return self.in_out

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    users = db.relationship('User', secondary='user_roles', lazy ='dynamic',passive_deletes=True,
                               backref=db.backref('users', lazy='dynamic'))

# Define the UserRoles data model
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))


def init_admins(admin_users):
    for user in admin_users:
        id = user['id']
        if not User.query.get(id):
            # Dictionaries can deliver keyword arguments!
            new_user = User(**user)
            new_user.roles.append(admin_role)
            new_user.roles.append(staff_role)
            db.session.add(new_user)
            db.session.commit()
        continue
    return


guest_role = Role(name='guest')
dept_role = Role(name='dept')
staff_role = Role(name='staff')
admin_role = Role(name='admin')


db.create_all()

init_admins(app.config['ADMIN_USERS'])
