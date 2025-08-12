from flask import Blueprint

videos_bp = Blueprint('videos', __name__)

from . import routes

