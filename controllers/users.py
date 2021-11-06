from models.users import User

class db_users:

    def __init__(self):
        self.users = []

     # Crear un nuevo usuario
    def createUsuario(self, name, gen, username, password, email, rol):
        if rol != 'ADMIN' and(len(name) < 8 or len(username) < 8 or len(password) < 8):
            return {'status': 500}
        id = len(self.users)
        nuevo = User(
            id,
            name if name != '' else 'Usuario' + id,
            gen if gen != '' else '-',
            username if username != '' else 'Usuario' + id,
            password,
            email,
            rol)
        for usuario in self.users:
            if usuario.username.lower() == username.lower() or usuario.email.lower() == email.lower():
                return {'status': 500}
        self.users.append(nuevo)
        return {'usuario_id': id, 'status': 200}

    # Leer usuario por id
    def readUsuario(self, id):
        for usuario in self.users:
            if usuario.id == id:
                return usuario.dump()
        
        return None
        
    # Leer todos los users
    def readUsuarios(self):
        usuarios_aux = []

        # Convirtiendo a JSON los users
        for usuario in self.users:
            usuarios_aux.append(usuario.dump())

        return usuarios_aux

    # Actualizar usuario
    def updateUsuario(self, id, name, username, password, email):
        if id != 0 and (len(name) < 8 or len(username) < 8 or len(password) < 8):
            return {'status': 500}
        for usuario in self.users:
            if usuario.id == id:
                usuario.name = name
                usuario.username = username
                usuario.password = password
                usuario.email = email
                return {'usuario': usuario.dump(), 'status': 200}
            elif usuario.username.lower() == username.lower() or usuario.email.lower() == email.lower():
                return {'status': 500}
        return {'status': 404}

    # Eliminar usuario
    def deleteUsuario(self, id):
        for usuario in self.users:
            if usuario.id == id:
                self.users.remove(usuario)
                return {'status': 200}
        return {'status': 404}  

    # Login
    def login(self, email, password):
        for usuario in self.users:
            if (usuario.email == email or usuario.username == email) and usuario.password == password:
                print('Usuario ' + usuario.username + " loggeado correctamente.")
                return {'usuario': usuario.dump(), 'status': 200}
        return {'status': 404}

    # Carga masiva
    def cargaMasiva(self, usuarios_cm):
        for usuario_cm in usuarios_cm:
            self.createUsuario(
                usuario_cm['name'],
                usuario_cm['gen'],
                usuario_cm['username'],
                usuario_cm['password'],
                usuario_cm['email'],
                'USER'
            )
        return "OK"