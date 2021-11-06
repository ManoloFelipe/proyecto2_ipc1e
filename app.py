from flask import Flask, request, jsonify, render_template, session, redirect, url_for, make_response
from flask_cors import CORS
from jinja2 import Environment, FileSystemLoader

import pdfkit

from controllers.users import db_users

#from routes.users import
user_controller = db_users();
app = Flask(__name__)
CORS(app)

#secret key
app.secret_key = 'fDW1QGnZIbmJSEqYrPCk'

#create default User Admins
user_controller.createUsuario('Cesar Reyes', 'M', 'admin', 'admin@ipc1', 'admin@ipc1.com', 'ADMIN')

#region templates
@app.route('/')
def white_page():
    return redirect(url_for('home'))

@app.route('/home')
@app.route('/admin')
def home():
    session['current_url'] = '/home'
    session['current_function'] = 'home'
    if 'login' in  request.args and request.args['login'] == 'Successful' and 'user_logged' not in session:
        return redirect('/home')
    return render_template('home.html')

@app.route('/mision_vision')
def mision_vision():
    session['current_url'] = '/mision_vision'
    session['current_function'] = 'mision_vision'
    return render_template('mision_vision.html')

@app.route('/admin/users')
def users_list():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN':
        return redirect(url_for(session['current_function']))
    session['current_url'] = '/admin/users'
    session['current_function'] = 'users_list'
    return render_template('usuarios.html', users = user_controller.readUsuarios())
#endregion

#region CRUD USERS
@app.route('/api/login', methods = ['POST'])
def login():
    status = user_controller.login(
        request.form['username'],
        request.form['password']
    )
    if status['status'] == 404 :
        return redirect(url_for(session['current_function'], login='Error'))
    else:
        session['user_logged'] = status['usuario']
        return redirect(url_for(session['current_function'], login='Successful'))

@app.route('/api/logout')
def logout():
    if 'user_logged' in session : session.pop('user_logged')
    return redirect('/')

@app.route('/api/register', methods = ['POST'])
def register():
    params = request.form.values()
    if not verificarParams(params):
        return redirect(url_for(session['current_function'], register='Error'))
    else:
        params = request.form
        status = user_controller.createUsuario(
            params['name'],
            params['gen'],
            params['username'],
            params['password'],
            params['email'],
            'USER'
        )
        if status['status'] == 500 :
            return redirect(url_for(session['current_function'], register='ErrorUsername'))
        else:
            print(user_controller.readUsuarios())
            return redirect(url_for(session['current_function'], register='Successful'))

@app.route('/api/update_user/<int:id>', methods=['POST'])
def update_user(id):
    params = request.form.values()
    if not verificarParams(params):
        return redirect(url_for(session['current_function'], update='Error'))
    else:
        params = request.form
        status = user_controller.updateUsuario(
            id,
            params['name'],
            params['username'],
            params['password'],
            params['email']
        )
        if status['status'] == 500 :
            return redirect(url_for(session['current_function'], update='ErrorUsername'))
        elif status['status'] == 500 :
            return redirect(url_for(session['current_function'], update='Error404'))
        else:
            session['user_logged'] = status['usuario']
            return redirect(url_for(session['current_function'], update='Successful'))

@app.route('/api/delete_user/<int:id>')
def delete_user(id):
    if id == 0:
        return redirect(url_for(session['current_function'], delete='ErrorAdmin'))
    status = user_controller.deleteUsuario(id)
    if status['status'] == 404:
        return redirect(url_for(session['current_function'], delete='Error404'))
    return redirect(url_for(session['current_function'], delete='SuccessfulE'))

@app.route('/api/pdf_users')
def pdf_users():
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('usuarios_pdf.html')
    html = template.render(users = user_controller.readUsuarios())
    pdf = pdfkit.from_string(html, False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Contetn-Disposition'] = 'attachment; filename=reporte_usuarios.pdf'
    return response
#endregion

#region funciones internas
def verificarParams(params):
    for param in params:
        if param == '':
            return False
    return True
#endregion

if __name__ == '__main__':
    app.run(debug=True)