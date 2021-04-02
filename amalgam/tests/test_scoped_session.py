from sqlalchemy.orm import scoped_session
from sqlalchemy import func, or_, desc

from amalgam.database import session_factory, engine
from amalgam.models.models import Site, User, Crawl, Url, Resource

_scoped_session = scoped_session(session_factory)

s = _scoped_session()

# s.remove()

_scoped_session.remove()