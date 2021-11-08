class Post:

    # CONSTRUCTOR
    def __init__(
        self,
        id,
        text,
        type,
        url,
        date,
        category,
        likes,
        author
    ):
        self.id         = id
        self.text         = text
        self.type       = type
        self.url        = url
        self.date        = date
        self.category   = category
        self.likes      = likes
        self.author      = author

    # METODOS
    def dump(self):
        return {
            'id':           self.id,
            'text':         self.text,
            'type':         self.type,
            'url':          self.url,
            'date':         self.date,
            'category':     self.category,
            'likes':        self.likes,
            'author':        self.author,
        }
