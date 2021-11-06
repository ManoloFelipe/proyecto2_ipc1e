class User:

    # CONSTRUCTOR
    def __init__(
        self,
        id,
        name,
        gen,
        username,
        password,
        email,
        rol
    ):
        self.id         = id
        self.gen        = gen
        self.username   = username
        self.name       = name
        self.password   = password
        self.email      = email
        self.rol        = rol

    # METODOS
    def dump(self):
        return {
            'id':           self.id,
            'gen':          self.gen,
            'username':     self.username,
            'name':         self.name,
            'password':     self.password,
            'email':        self.email,
            'rol':          self.rol,
        }
