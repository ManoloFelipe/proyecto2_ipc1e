from flask import Flask, json, request, jsonify, render_template, session, redirect, url_for, make_response, flash
from flask_cors import CORS
from jinja2 import Environment, FileSystemLoader
from fpdf import FPDF, HTMLMixin, html
from controllers.users import db_users
from controllers.posts import db_posts

#databases
user_controller = db_users();
post_controller = db_posts();
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

@app.route('/posts')
def posts_list():
    session['current_url'] = '/posts'
    session['current_function'] = 'posts_list'
    posts = post_controller.readPosts()
    if len(posts) != 0:
        my_posts = post_controller.myPosts(session['user_logged']['name'])
        top5 = post_controller.top5()
    else:
        my_posts = []
        top5 = []
    return render_template('posts.html', posts = posts, my_posts= my_posts, top5 = top5)

@app.route('/admin/users')
def users_list():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN':
        return redirect(url_for(session['current_function']))
    session['current_url'] = '/admin/users'
    session['current_function'] = 'users_list'
    users = user_controller.readUsuarios()
    return render_template('usuarios.html', users = users)

@app.route('/admin/posts')
def post_admin():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN':
        return redirect(url_for(session['current_function']))
    session['current_url'] = '/admin/posts'
    session['current_function'] = 'post_admin'
    top5 = post_controller.top5()
    valores_chart_barras = [len(top['likes']) for top in top5]
    return render_template('admin_posts.html', top5 = top5, values = valores_chart_barras)
#endregion

#region CRUD USERS
@app.route('/api/login', methods = ['POST'])
def login():
    status = user_controller.login(
        request.form['username'],
        request.form['password']
    )
    if status['status'] == 404 :
        flash('Error al iniciar sesión' ,'danger')
        return redirect(url_for(session['current_function']))
    else:
        session['user_logged'] = status['usuario']
        flash('Bienvenido '+session["user_logged"]["name"] ,'success')
        return redirect(url_for(session['current_function']))

@app.route('/api/logout')
def logout():
    if 'user_logged' in session : session.pop('user_logged')
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for(session['current_function']))

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
            return redirect(url_for(session['current_function'], register='Successful'))

@app.route('/api/update_user/<int:id>', methods=['POST'])
def update_user(id):
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for('logout'))
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
        elif status['status'] == 404 :
            return redirect(url_for('logout', update='Error404'))
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
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN':
        return redirect(url_for(session['current_function']))
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('usuarios_pdf.html')
    html = template.render(users = user_controller.readUsuarios())
    pdf = PDF()
    pdf.add_page()
    pdf.write_html(html)
    response = make_response(pdf.output(dest='S'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Contetn-Disposition'] = 'attachment; filename=reporte_usuarios.pdf'
    return response

@app.route('/api/carga_masiva_users', methods=['POST'])
def carga_masiva_users():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN' or not request.files['file']:
        return redirect(url_for(session['current_function']))
    file = request.files['file']
    flash('Carga masiva realizada con exito!', 'success')
    json_data = json.load(file)
    user_controller.cargaMasiva(json_data['usuarios'])
    return redirect(url_for(session['current_function']))
#endregion

#region CRUD POSTS
@app.route('/api/post/add', methods = ['POST'])
def add_post():
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for(session['current_function']))
    params = request.form.values()
    if not verificarParams(params):
        flash('Todos los campos deben estar llenos','warning')
        return redirect(url_for(session['current_function']))
    else:
        params = request.form
        status = post_controller.createPost(
            params['text'],
            params['type'],
            params['url'],
            '',
            params['category'],
            session['user_logged']['name']
        )
        if status['status'] == 500 :
            flash('Error desconocido, contacte con su proveedor','danger')
            return redirect(url_for(session['current_function']))
        else:
            flash('Publicado!!, publicación realizada con exito','success')
            return redirect(url_for(session['current_function']))

@app.route('/api/post/update/<int:id>', methods = ['POST'])
def update_post(id):
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for(session['current_function']))
    params = request.form.values()
    if not verificarParams(params):
        flash('Todos los campos deben estar llenos','warning')
        return redirect(url_for(session['current_function']))
    else:
        params = request.form
        status = post_controller.updatePost(
            id,
            params['text'],
            params['type'],
            params['url'],
            '',
            params['category']
        )
        if status['status'] == 500 :
            flash('Error desconocido, contacte con su proveedor','danger')
            return redirect(url_for(session['current_function']))
        else:
            flash('Publicado!!, publicación realizada con exito','success')
            return redirect(url_for(session['current_function']))

@app.route("/api/post/delete/<int:id>")
def delete_post(id):
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for(session['current_function']))
    status = post_controller.deletePost(id)
    if status['status'] == 404 :
        flash('Post no encontrado','danger')
        return redirect(url_for(session['current_function']))
    else:
        flash('Publicación eliminada correctamente','success')
        return redirect(url_for(session['current_function']))

@app.route('/api/post/like/<int:id>')
def like_post(id):
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for(session['current_function']))
    status = post_controller.addLike(id,session['user_logged']['id'])
    if status['status'] == 404 :
        flash('Post no encontrado','danger')
        return redirect(url_for(session['current_function']))
    else:
        flash('like agregado correctamente','success')
        return redirect(url_for(session['current_function']))

@app.route('/api/post/dislike/<int:id>')
def dislike_post(id):
    if 'user_logged' not in session:
        flash('Por favor inicie sesión','warning')
        return redirect(url_for(session['current_function']))
    status = post_controller.deleteLike(id,session['user_logged']['id'])
    if status['status'] == 404 :
        flash('Post no encontrado','danger')
        return redirect(url_for(session['current_function']))
    else:
        flash('like eliminado de la publicación','success')
        return redirect(url_for(session['current_function']))

@app.route('/api/post/carga_masiva', methods=['POST'])
def carga_masiva_post():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN' or not request.files['file']:
        flash('Por favor inicie sesión', 'warning')
        return redirect(url_for(session['current_function']))
    file = request.files['file']
    json_data = json.load(file)
    if 'image' not in json_data and 'video' not in json_data:
        flash('Formato de json no valido', 'danger')
        return redirect(url_for(session['current_function']))
    post_controller.cargaMasiva(json_data['image'],'image')
    post_controller.cargaMasiva(json_data['video'],'video')
    flash('Carga masiva realizada con exito!', 'success')
    return redirect(url_for(session['current_function']))

@app.route('/api/pdf_top5')
def pdf_top_5():
    if 'user_logged' not in session or session['user_logged']['rol'] != 'ADMIN':
        return redirect(url_for(session['current_function']))
    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('top5_pdf.html')
    top5 = post_controller.top5()
    html = template.render(top5 = top5)
    pdf = PDF()
    pdf.add_page()
    pdf.write_html(html)
    pdf.output('reporte.pdf')
    response = make_response(html)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Contetn-Disposition'] = 'attachment; filename=reporte_top_5.pdf'
    return response
#endregion

#region pdf class
class PDF(FPDF, HTMLMixin):
    pass
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