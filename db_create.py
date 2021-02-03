from amalgam.database import db

#create db and tables
db.create_all()

#inserts
# db.session.add(BlogPost("Good","I feel good."))
# db.session.add(BlogPost("Well","I feel well."))

#save changes
print(db.session.commit())