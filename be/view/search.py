from flask import Blueprint
from flask import request
from flask import jsonify
from be.model import searchManager

bp_search = Blueprint("search", __name__, url_prefix="/search")


@bp_search.route("/search", methods=["POST"])
def search_info():
    page_id: int = request.json.get("page_id")
    store_id: str = request.json.get("store_id")
    search_info: dict = request.json.get("search_info")
    s = searchManager.SearchManager()
    code, message, books = s.search(store_id, page_id, search_info)

    return jsonify({"message": message, "books": books}), code
