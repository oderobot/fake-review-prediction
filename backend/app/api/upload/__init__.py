# app/api/upload/__init__.py
from flask import Blueprint

upload_bp = Blueprint('upload', __name__)

from . import routes