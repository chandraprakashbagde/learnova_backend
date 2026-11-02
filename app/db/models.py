"""Import every model module so SQLAlchemy registers all mapped classes.

Importing this module (e.g. from the application entry point) guarantees
that string-based relationships such as ``relationship("TeacherProfile")``
can be resolved, regardless of which module is imported first.

Keep the import order from leaf modules upward: auth -> teacher -> admin.
"""
from app.auth import models  # noqa: F401
from app.teacher.profile import models  # noqa: F401
from app.admin.subjects import models  # noqa: F401
from app.admin.qaulifications import models  # noqa: F401
