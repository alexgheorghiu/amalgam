# class Site(db.Model):
#     __tablename__ = "sites"
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String, nullable=False)
#     crawls = relationship("Crawl", backref="site")