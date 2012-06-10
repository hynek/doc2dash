from . import pydoctor, sphinx


DOCTYPES = [sphinx.doctype, pydoctor.doctype]


def get_doctype(path):
    """Gets the apropriate doctype for *path*."""
    for dt in DOCTYPES:
        if dt.detect(path):
            return dt
    else:
        return None
