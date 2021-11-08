from models.posts import Post
from datetime import date as date_today
 
class db_posts:

    def __init__(self):
        self.posts = []

     # Crear un nuevo Post
    def createPost(self, text, type, url, date, category, author):
        if not author or not type or not url:
            return {'status': 500}
        id = len(self.posts) + 1
        nuevo = Post(
            id,
            text if text != '' else 'publicacion de '+author,
            type,
            url,
            date if date != '' else date_today.today().strftime("%d/%m/%Y"),
            category,
            [],
            author)
        self.posts.append(nuevo)
        return {'post_id': id, 'status': 200}

    # Leer post por id
    def readPost(self, id):
        for post in self.posts:
            if post.id == id:
                return post.dump()
        return None
        
    # Leer todos los posts
    def readPosts(self):
        posts_aux = []

        # Convirtiendo a JSON los posts
        for post in self.posts:
            posts_aux.append(post.dump())

        return posts_aux

    # usuario_loggeado posts
    def myPosts(self, author):
        posts_aux = []

        # Convirtiendo a JSON los posts
        for post in self.posts:
            if author == post.author:
                posts_aux.append(post.dump())

        return posts_aux

    # top 5 posts mas likes
    def top5(self):
        posts_aux = []
        # Convirtiendo a JSON los posts
        for post in self.posts:
            if len(posts_aux) < 5:
                posts_aux.append(post.dump())
            else:
                posts_aux.sort(key=lambda x: len(x['likes']))
                for index, post_aux in enumerate(posts_aux):
                    if len(post.likes) > len(post_aux['likes']):
                        posts_aux.append(post.dump())
                        del posts_aux[0]
                        break
                continue

        posts_aux.sort(key=lambda x: len(x['likes']), reverse=True)
        return posts_aux

    # Actualizar post
    def updatePost(self, id, text, type, url, date, category):
        for post in self.posts:
            if post.id == id:
                post.text = text
                post.type = type
                post.url = url
                post.date = date if date != '' else date_today.today().strftime("%d/%m/%Y"),
                post.category = category
                return {'post': post.dump(), 'status': 200}
        return {'status': 404}

    # agregar like
    def addLike(self, id, user_id):
        for post in self.posts:
            if post.id == id:
                post.likes.append(user_id)
                return {'status':200}
        return {'status': 404}

    # quitar like
    def deleteLike(self, id, user_id):
        for post in self.posts:
            if post.id == id:
                post.likes.remove(user_id)
                return {'status':200}
        return {'status': 404}

    # Eliminar post
    def deletePost(self, id):
        for post in self.posts:
            if post.id == id:
                self.posts.remove(post)
                return {'status': 200}
        return {'status': 404}

    # Carga masiva
    def cargaMasiva(self, posts_cm, type):
        for post_cm in posts_cm:
            self.createPost(
                '',
                type,
                post_cm['url'],
                date_today.today().strftime("%d/%m/%Y"),
                post_cm['category'],
                post_cm['author'],
            )
        return "OK"