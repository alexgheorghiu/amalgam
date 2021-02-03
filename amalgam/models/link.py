import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from amalgam.database import db

class Link(db.Model):
    __tablename__ = "links"

    TYPE_EXTERNAL = "external"
    TYPE_INTERNAL = "internal"

    id = db.Column(db.Integer, primary_key=True)
    absolute_url = db.Column(db.String, nullable=False)
    url = db.Column(db.String, nullable=True)
    content = db.Column(db.String, nullable=True)
    mime_type = db.Column(db.String, nullable=True)
    crawl_id = db.Column(db.Integer, ForeignKey('crawls.id'))
    type = db.Column(db.String, nullable=True) # external or internal

    def __init__(self, absolute_url, url, type):
        self.absolute_url = absolute_url
        self.url = url
        self.type = type

    def __repr__(self):
        return '<{}={}'.format(self.id, self.absolute_url)