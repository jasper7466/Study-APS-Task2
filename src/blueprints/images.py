from flask import (
    Blueprint,
    request,
    jsonify,
    url_for,
    send_from_directory
)
from flask.views import MethodView
from werkzeug.utils import secure_filename
from auth import seller_required
from fileloader import fl


bp = Blueprint('images', __name__)


class ImagesUploadView(MethodView):
    @seller_required
    def post(self, account=None):
        """
        Обработчик метода POST для запроса на добавление сохранение файла.
        Из тела запроса извлекает файл.
        Проверяет имя файла на предмет безопасности и инициирует процедуру сохранения.
        Возвращает ответ в JSON-формате в виде объекта с url файла.

        :param account: {"account_id": account_id, "seller_id": seller_id}
        :return: {"url": image_url}
        """
        file = request.files['file']
        if not file:
            return '', 400

        file.filename = secure_filename(file.filename)
        file_name = fl.save_file(file)
        if not file_name:
            return '', 500

        file_url = url_for('images.download', image_name=file_name,  _external=True)

        return jsonify({"url": file_url}), 200


class ImagesDownloadView(MethodView):
    def get(self, image_name):
        """
        Обработчик метода GET для запроса на получение файла по его имени.
        Получает путь до директории загрузки и производит отправку файла с заданным именем.
        Возвращает путь до запрашиваемого файла.
        :param image_name: имя файла
        :return: image
        """
        upload_dir = fl.get_dir()
        return send_from_directory(upload_dir, image_name)


bp.add_url_rule('', view_func=ImagesUploadView.as_view('upload'))
bp.add_url_rule('/<image_name>', view_func=ImagesDownloadView.as_view('download'))
