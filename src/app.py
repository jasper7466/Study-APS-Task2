from flask import Flask, request, render_template, make_response
from flask.views import MethodView

app = Flask(__name__)


class IndexView(MethodView):
    def get(self):
        return 'Response!', 404

    def post(self):
        return '\n'.join(
            f'{key}: {value}'
            for key, value in request.args.items()
        )


app.add_url_rule('/', view_func=IndexView.as_view('index'))


@app.route('/user/<int:user_id>')
def getuser(user_id):
    return {
        'id': user_id,
        'name': 'John'
    }
