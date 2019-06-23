from application import db


attribute_tags = db.Table('attribute_tags',
                          db.Column('attribute_id',
                                    db.Integer,
                                    db.ForeignKey('Attributes.id'),
                                    primary_key=True),
                          db.Column('tag_id',
                                    db.Integer,
                                    db.ForeignKey('Tags.id'),
                                    primary_key=True))


class Attributes(db.Model):
    __tablename__ = 'Attributes'
    id = db.Column(db.Integer, primary_key=True)
    attribute = db.Column(db.String(128), index=True, unique=False)
    value = db.Column(db.String(128), index=True, unique=False, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    tags = db.relationship('Tags', secondary=attribute_tags, lazy='subquery',
                           backref=db.backref('Class', lazy=True))

    def __init__(self, attribute, value, weight):
        self.attribute = attribute
        self.value = value
        self.weight = weight

    def __repr__(self):
        return '<Attribute {} Value {} Weight {}>'.format(self.attribute, self.value, self.weight)


class Tags(db.Model):
    __tablename__ = 'Tags'
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String(128), nullable=False)
    tag_value = db.Column(db.String(128), nullable=False)

    def __init__(self, tag, value):
        self.tag_name = tag
        self.tag_value = value

    def __repr__(self):
        return '<tag {}: {}>'.format(self.tag_name, self.tag_value)



