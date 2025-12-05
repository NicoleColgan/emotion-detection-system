'''
Flask server that exposes emotion detection endpoing and renders UI
'''

from flask import Flask, request, render_template, jsonify
from EmotionDetection.emotion_detection import emotion_detector
from embeddings import store_feedback, search_feedback, count_points

app = Flask(__name__)

@app.route("/emotionDetector")
def emotion_detector_endpoint():
    '''
    enpoint for getting emotion detection result and returning it to be displayed on the ui
    '''
    input_text = request.args.get('inputText', '')
    response = emotion_detector(input_text)

    if response.get('dominant_emotion'):
        return f"For the given statement, the system response is 'anger': {response.get('anger')}, 'disgust: {response.get('disgust')}, 'fear': {response.get('fear')}, 'joy': {response.get('joy')} and 'sadness': {response.get('sadness')}. The dominant emotion is {response.get('dominant_emotion')}."
    return 'Invalid text! Please try again'

@app.route("/")
def render_index():
    '''
    render default html
    '''
    return render_template("index.html")

@app.route("/api/analyse_and_store", methods=["POST"])
def analyse_and_store():
    """
    Analyse a piece of feedback using emotion_detector,
    store it in Qdrant with its emotions,
    and return the analysis.
    """
    data = request.get_json()
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "Missing 'text' in request body"}), 400

    result = emotion_detector(text)

    # Store in Qdrant for later semantic search
    store_feedback(text, result)

    return jsonify({
        "text": text,
        "analysis": result
    })

@app.route("/api/search_feedback", methods=["GET"])
def search_feedback_endpoint():
    """
    Semantic search over stored feedback using Qdrant.
    Query parameter: ?query=...
    """
    query = request.args.get("query", "")

    if not query:
        return jsonify({"error": "Missing 'query' parameter"}), 400

    results = search_feedback(query)

    return jsonify({
        "query": query,
        "results": results
    })
    
@app.route("/health")
def health():
    return {"status": "ok"}

@app.route("/count")
def count():
    """
    Returns number of points in collection
    """
    return {"count": count_points()}

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
