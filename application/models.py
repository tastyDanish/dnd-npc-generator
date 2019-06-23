from application import db


class Attributes(db.Model):
    id = db.Column(db.Interger, primary_key=True)
    attribute = db.Column(db.String(128), index=True, unique=False)
    value = db.Column(db.String(128), index=True, unique=False, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    tags = db.relationship('tags', backref='attribute', lazy='dynamic')

    def __init__(self, attribute, value, weight):
        self.attribute = attribute
        self.value = value
        self.weight = weight

    def __repr__(self):
        return '<Attribute {} Value {}>'.format(self.attribute, self.value)


class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag = db.Column(db.String(128), nullable=False)

    def __init__(self, tag):
        self.tag = tag

    def __repr__(self):
        return '<tag {}'


attribute_tags = db.Table('attribute_tags',
                          db.Column('attribute_id',
                                    db.Integer,
                                    db.ForeignKey('Attributes.id'),
                                    primary_key=True),
                          db.Column('tag_id',
                                    db.Integer,
                                    db.ForeignKey('Tags.id'),
                                    primary_key=True))
