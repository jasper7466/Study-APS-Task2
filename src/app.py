from flask import Flask, request, render_template, make_response

app = Flask(__name__)


@app.route('/', methods = ['GET', "POST"])
def index():
    if request.method == 'GET':
        response = make_response('Hello, world!')
        response.headers['X-My-Header'] = 'test'
        return response
        # return 'Response!', 404
    else:
        return '\n'.join(
            f'{key}: {value}'
            for key, value in request.args.items()
        )
        # return 'This is POST!'


@app.route('/user/<int:user_id>')
def getuser(user_id):
    return {
        'id': user_id,
        'name': 'John'
    }
