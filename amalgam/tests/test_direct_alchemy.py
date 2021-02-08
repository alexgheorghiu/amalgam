from amalgam.models.models import User
from amalgam.delegate import delegate

u = User()
u.name = 'Alex'
u.email = 'alex@scriptoid.com'
u.password=  'test'

delegate.add_user(u)

u = User(name="Adi", email="adi@foo.com", password="zoro")
delegate.add_user(u)
