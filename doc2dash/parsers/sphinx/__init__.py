from ..doctype import DocType

from .detector import detect
from .parser import parse

doctype = DocType('sphinx', detect, parse)
