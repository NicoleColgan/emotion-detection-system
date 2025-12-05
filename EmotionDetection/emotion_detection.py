import requests

def emotion_detector(text_to_analyse):
    url = 'https://sn-watson-emotion.labs.skills.network/v1/watson.runtime.nlp.v1/NlpService/EmotionPredict'
    headers = {"grpc-metadata-mm-model-id": "emotion_aggregated-workflow_lang_en_stock"}
    myobj = { "raw_document": { "text": text_to_analyse } }

    # Default response (if anything goes wrong)
    empty_result = {
        'anger': None,
        'disgust': None,
        'fear': None,
        'joy': None,
        'sadness': None,
        'dominant_emotion': None
    }
    # can uncomment below and comment out try catch for testing
    #return {'anger': 0.85, 'disgust': 0.05, 'fear': 0.05, 'joy': 0.01, 'sadness': 0.04, 'dominant_emotion': 'anger'}

    try:
        # Send post request to API
        response = requests.post(url, json=myobj, headers=headers)
        response.raise_for_status()  # raise HTTPError automatically for bad request

        # convert to JSON
        formatted_Response = response.json()    # safer than json.loads()

        predictions = formatted_Response.get('emotionPredictions', [])  # avoid KeyError
        if not predictions:
            return empty_result

        emotions = predictions[0].get('emotion', {})
        if not emotions:
            return empty_result

        dominant_emotion = max(emotions, key=emotions.get)
        emotions['dominant_emotion'] = dominant_emotion
        return emotions
    # HTTPError is a subclass of RequestException so if you put RequestException catch block first, it will catch the HTTPError too => put HTTPError first
    except requests.HTTPError as http_error:
        print(f"HTTPError occured: {http_error}")
        return empty_result
    except requests.RequestException as request_exception:
        print(f"API request failed: {request_exception}")
        return empty_result
