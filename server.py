'''
Flask server that exposes emotion detection endpoing and renders UI
'''

from flask import Flask, request, render_template
from EmotionDetection.emotion_detection import emotion_detector


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

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
