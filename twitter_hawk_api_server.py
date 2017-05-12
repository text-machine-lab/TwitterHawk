import sys

sys.path.insert(1, 'TaskB/code/')

from bottle import Bottle, HTTPError, request

from predict import TwitterHawk

app = Bottle()

model_path = 'TaskB/models/trained.model'
th = TwitterHawk(model_path)


@app.route('/analyze', method='POST')
def hello():
    separate = False
    if request.query.get('separate', '0') == '1':
        separate = True

    try:
        data = request.json
    except ValueError as e:
        raise HTTPError(400, e.message)

    if not isinstance(data, list):
        data = [data]

    try:
        X = [(tweet['id'], tweet['text']) for tweet in data]
    except KeyError as e:
        raise HTTPError(400, e.message)

    sentiment_scores = th.predict(X, predict_type='probs')

    if not separate:
        result = [sentiment_scores[i, 0] - sentiment_scores[i, 1] for i in range(sentiment_scores.shape[0])]
    else:
        result = [
            {
                'positive': sentiment_scores[i, 0],
                'negative': sentiment_scores[i, 1],
                'neutral': sentiment_scores[i, 2],
            }
            for i in range(sentiment_scores.shape[0])
        ]

    return {'result': result}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=7654)
