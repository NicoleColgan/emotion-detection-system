"""
Flask server that exposes emotion detection endpoing and renders UI
"""

from flask import Flask, request, render_template, jsonify, Response, stream_with_context
from EmotionDetection.emotion_detection import emotion_detector
from embeddings import store_feedback, search_feedback, count_points
from agent import generate_support_reply, stream_support_reply

app = Flask(__name__)

@app.route("/emotionDetector")
def emotion_detector_endpoint() -> str:
    """
    Endpoint for getting emotion detection result to be displayed on UI

    Returns:
        str: emotion detetction text string to display on UI
    """
    input_text = request.args.get('inputText', '')
    response = emotion_detector(input_text)

    if response.get('dominant_emotion'):
        return f"For the given statement, the system response is 'anger': {response.get('anger')}, 'disgust: {response.get('disgust')}, 'fear': {response.get('fear')}, 'joy': {response.get('joy')} and 'sadness': {response.get('sadness')}. The dominant emotion is {response.get('dominant_emotion')}."
    return 'Invalid text! Please try again'

@app.route("/")
def render_index() -> str:
    """
    Return default html
    """
    return render_template("index.html")

@app.route("/api/analyse_and_store", methods=["POST"])
def analyse_and_store() -> Response:
    """
    Analyses feedback for emotion and persists the results to the vector database.

    Workflow:
    1. Pass raw feedback through the emotion_detector model.
    2. Extract dominant emotion and confidence scores.
    3. Store the text and its emotional metadata in Qdrant.

    Returns:
        Response: A Flask JSON response containing original text and analysis
    """
    data = request.get_json() or {}
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
def search_feedback_endpoint() -> Response:
    """
    Semantic search over stored feedback using Qdrant.

    Query parameter: 
        query (str): query to search in the database

    Returns:
        Response: json response containing original query and the database results
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
def health() -> dict:
    """Returns health status of application"""
    return {"status": "ok"}

@app.route("/count")
def count() -> dict:
    """
    Returns number of points in collection
    """
    return {"count": count_points()}

@app.route("/api/suggest_reply", methods=["POST"])
def suggest_reply() -> Response | tuple[Response, int]:
    """
    Agent endpoint that returns a response to the user feedback

    Workflow:
    - Takes customer feedback text
    - Runs emotion detection
    - Fetched similar feedback from Quadrant
    - Asks LLM to generate an empathetic reply

    Response:
        Response: A JSON object with the response and a status
    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    
    try:
        result = generate_support_reply(text)
        return jsonify(result)
    except Exception as e:
        # Basic safety net so the API doesnt hard crash
        print(f"Error in generate_support_reply(): {e}")
        return jsonify({"error": "failed to generate reply"}), 500

@app.route("/api/suggest_reply_stream", methods=["POST"])
def suggest_reply_stream() -> Response:
    """
    Streaming agent endpoint that returns LLM response to customer feedback

    Workflow
    1. Takes text in body
    2. Streams back suggested reply as plain text chunks

    JSON body:
        text (str): The cutomer feedback for which the LLM must respond

    Returns:
        Response: Streamed LLM response

    """
    data = request.get_json() or {}
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "Missing 'text' in request body"}), 400
    def generate():
        try:
            for chunk in stream_support_reply(text):    # get next chunk from agent
                yield chunk # send piece of reply to client as they arrive
        except Exception as e:
            # log error and end stream
            print(f"error in suggest_reply_stream: {e}")
    # stream_with_context keeps the request data (text) for the generate function
    # Response wrape the generator so flask can send the chunks as soon as they appear.
    return Response(stream_with_context(generate()), mimetype="text/plain")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
