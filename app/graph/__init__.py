from flask import Blueprint

graph_bp = Blueprint("graph", __name__, template_folder="templates")


from . import views
