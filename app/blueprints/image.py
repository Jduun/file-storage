from flask import Blueprint, jsonify, request
from http import HTTPStatus
from rabbitmq import publish_message
from services import FileStorageService

image = Blueprint("image", __name__)


@image.route("/images/<string:image_id>/resize", methods=["POST"])
def resize_image(image_id):
    data = request.get_json()
    new_width, new_height = data["new_width"], data["new_height"]
    image_path = FileStorageService.get_abs_path(
        FileStorageService.get_file_by_id(image_id)
    )
    task = {"image_path": image_path, "new_width": new_width, "new_height": new_height}
    publish_message(task)
    return jsonify({"message": "Task has been submitted"}), HTTPStatus.OK
