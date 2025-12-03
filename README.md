# Emotion detection system
![deployed-ui](./images/deployed-ui.png)

## Intro
This project aims to create an AI web-based app that performs analytics on customer feedback. To accomplish this, I have created an Emotion Detection System that processes feedback provided by customers in text format and deciphers the emotions expressed.

In this project, I will use the embeddable Watson AI libraries to create an emotion detection application.

Emotion detection extends the concept of sentiment analysis by extracting finer emotions like joy, sadness, anger, and so on, from statements rather than just whether a statement is positive or negative. Emotion detection is widely used for AI based recommendation systems, chatbots, and so on.

## 1. Creating an emotion detection system using Watson NLP library
The Watson NLP libraries are embedded, so only need to send a post request to the correct function in the library and receive the output.
steps:
1. Create `emotion_detector` function in `emotion_detection.py` file
2. Define url, headers, and body and make post Request to emotion detection API
3. Convert response to a json object
4. Extract prediction from response
5. Detect dominant emotion & combine it with above dictionary to return

Example API response
```python
{
    "emotionPredictions":[
        {
            "emotion":{
                "anger":0.010043259, 
                "disgust":0.016082913, 
                "fear":0.051737938, 
                "joy":0.9262508, 
                "sadness":0.04585947
            }, 
            "target":"", 
            "emotionMentions":[
                {
                    "span":{
                        "begin":0, 
                        "end":36, 
                        "text":"This is a really interesting project"
                    }, 
                    "emotion":{
                        "anger":0.010043259, 
                        "disgust":0.016082913, 
                        "fear":0.051737938, 
                        "joy":0.9262508, 
                        "sadness":0.04585947
                    }
                }
            ]
        }
    ],
    "producerId":{
        "name":"Ensemble Aggregated Emotion Workflow", 
        "version":"0.0.1"
    }
}
```

### Testing function
* Open a python shell and import function
```pythoh
from emotion_detection import emotion_detector
```
* Use function
```python
emotion_detector("This is a really interesting project")
```

Example output:
```pyton
{'anger': 0.010043259, 'disgust': 0.016082913, 'fear': 0.051737938, 'joy': 0.9262508, 'sadness': 0.04585947, 'dominant_emotion': 'joy'}
```

## 2. Packaging the application
1. Create the `EmotionDetection` folder and place `emotion_detection.py` inside along with `__init__` file to reference the module.
2. Test the package by importing it in a python shell
```pyton
>>> from EmotionDetection.emotion_detection import emotion_detector
```
3. If no error show, it indicates the package is ready to use
```python
>>> emotion_detector("This is a really interesting course")
{'anger': 0.016279602, 'disgust': 0.01874656, 'fear': 0.05179948, 'joy': 0.88792956, 'sadness': 0.06251001, 'dominant_emotion': 'joy'}
>>> emotion_detector("I hate working long hours")
{'anger': 0.64949876, 'disgust': 0.03718168, 'fear': 0.05612277, 'joy': 0.00862553, 'sadness': 0.1955148, 'dominant_emotion': 'anger'}
```

## 3. Unit tests
1. Create `test_emotion_detection.py` test file and add a unit test to test `emotion_detector`.
2. Test the following statements
    * "Im glad this happened" = "joy"
    * "Im really angry hearing about this" = "anger"
    * "Im feeling so disgusted even just hearing about this" = "disgust"
    * "Im so sad about this" = "sadness"
    * "Im really afraid this will happen" = "fear"
3. Run file
```bash
$ python3.11 test_emotion_detection.py
.
----------------------------------------------------------------------
Ran 1 test in 0.706s

OK
```

## 4. Web deployment of the application using flask
1. `index.html` is a simple html file with a text area where the user enters the sentence to be analysed.
2. The user clicks the Run button which triggers a JavaScript function in `emotion.js`
3. `emotion.js` sends a GET request to our `emotionDetector` endpoint to get the result, then sets the result on the UI
4.  `server.py` file contains the default endpoint which renders `index.html` in `/templates` and an endpoint for calling the `emotion_detector`. This endpoint parses the text from the query parameters and formats and returns it for viewing on the UI
3. The server also contains the function to execute app and deploy on localhost:5000

Example output:
![deployed-ui](./images/deployed-ui.png)

## 5. Incorporating Error handling
1. use `response.raise_for_status()` to automatically raise HTTPError for bad requests
2. If predictions or emotions are empty, return json with None values for predictions
3. Handle `HTTPError` (API responds with bad status eg 400) and `RequestException` (request itself fails before the API even responds eg. no internet connection, invalid url, timeout) errors by printing a useful message and returning the empty prediction json object.
4. In server, check if the response was ok and display a different message depending

UI output:
![error-handling-interface](./images/error_handling_interface.png)

## 6. Running static code analysis on project
* Check the code as per the PEP8 guidlines by running static code analysis
* Normally, this should be done at the time od packaging and unit testing 
* Fix the items it mentions to increase score close to 10
* Install PyLint
```bash
python3.11 -m pip install PyLint
```
* Run PyLint
```bash
pylint server.py
```
example output
```bash
************* Module server
server.py:12:0: C0301: Line too long (299/100) (line-too-long)
server.py:20:0: C0304: Final newline missing (missing-final-newline)
server.py:1:0: C0114: Missing module docstring (missing-module-docstring)
server.py:7:0: C0116: Missing function or method docstring (missing-function-docstring)
server.py:8:4: C0103: Variable name "inputText" doesn't conform to snake_case naming style (invalid-name)
server.py:16:0: C0116: Missing function or method docstring (missing-function-docstring)

-----------------------------------
Your code has been rated at 5.38/10
```

## Dockerising the container
Docker allows you to package your app and its dependencies into a single container. This ensures your app runs consistently accross different environmentts, making it easy to deploy, share, and scale your app.

The Dockerfile describes the steps to build this container, including installing Python, required libraries, copying your code, and starting the Flask server. Once built, you can run your app anywhere Docker is available.

Docker Compose is like combining the docker build and docker run commands (with all their parameters) into a single configuration file. It lets you define how to build your image, set environment variables, map ports, and manage multiple containers—all in one place. Then you just run `docker-compose up` to build and start everything as described in the file.

### .dockerignore
* The `.dockerignore` file lists files and folders that should be excluded from the Docker build context. This keeps your Docker image smaller and prevents sensitive or unnecessary files (like virtual environments, editor settings, and cache files) from being added to the container.

### Dockerfile
1. Use `python:3.10-slim`, a lightweight version of python
2. Set workin dir inside continer
3. install requirements - `--no-cache-dir` prevents pip from storing downloaded packages in cache, keeping the image smaller
4. Document port 5000

#### Build the Docker image
`docker build -t emotion-detection-app .`

#### Run the container from Docker image
`docker run -p 5000:5000 emotion-detection-app`

### docker-compose.yml
1. Define version of docker compose file format - `3.8` is a commonly used modern version
2. Define emotion-detection service. A service is a containerized application managed by Docker Compose.
3. `build: .` tells Docker Compose to build the image for this service using the Dockerfile in the current directory.
Then use: docker-compose up --build
4. Map port 5000 on your computer (host) to port 5000 in the container.

#### Run the container with Docker Compose
* `docker-compose up` starts the container using the existing image if one exists (like if you build one from your image above ^)
* `docker-compose up --build` forces Docker Compose to rebuild the image before starting the container
* Your application will be accessible at http://localhost:5000.


### Setting up Quadrant db
the docker compose created teh quadrant image so you can seperately - docker run -p 6333:6333 qdrant/qdrant
even if you have muliple services in your dockocmpose, you can run them seperately by name like 
docker-compose up qdrant 

you can run a service in the foreg with docker-compose run --service-ports emotion-detection
now if you add `breakpoint()` in your python files, your in the python debugger inside the docker container -> curl -X GET http://localhost:5000/api/search_feedback?query=hello
What you can do now:
At the (Pdb) prompt, you can type commands to inspect and control your code:
n — step to the next line
c — continue execution until the next breakpoint
l — list source code around the current line
p variable_name — print the value of a variable (e.g., p text)
s - step into 
q — quit the debugger
enter moved to next line too

(Pdb) l
 64         """
 65         Semantic search over stored feedback using Qdrant.
 66         Returns a list of payloads with text + emotions.
 67         """
 68         breakpoint()
 69  ->     ensure_collection()
 70         query_vec = embed_text(query)
 71
 72         hits = qdrant.search(
 73             collection_name=COLLECTION_NAME,
 74             query_vector=query_vec,



 does it work for strings


 docker build -t emotion-detection-app .
 docker-compose run --service-ports emotion-detection

 get search looks ok when the query string is one word and theres nothing in the db - need to test for valid entries

C:\Users\colgann>curl -X POST http://localhost:5000/api/analyse_and_store -H "Content-Type: application/json" -d "{\"text\": \"I am really happy with this service\"}"

-> qdrant.upsert(
(Pdb) p payload
{'text': 'I am really happy with this service', 'dominant_emotion': 'joy', 'emotions': {'anger': 0.016279602, 'disgust': 0.01874656, 'fear': 0.05179948, 'joy': 0.88792956, 'sadness': 0.06251001}}
(Pdb)

C:\Users\colgann>curl -X POST http://localhost:5000/api/analyse_and_store -H "Content-Type: application/json" -d "{\"text\": \"I am really happy with this service\"}"
{
  "analysis": {
    "anger": 0.016279602,
    "disgust": 0.01874656,
    "dominant_emotion": "joy",
    "fear": 0.05179948,
    "joy": 0.88792956,
    "sadness": 0.06251001
  },
  "text": "I am really happy with this service"
}

multiple inserts are working - im putting in one thats not simlar right now so we can test it - it should get no matches but the other should

![qdrant](./images/Qdrant.png)
![qdrant-similar](./images/Qdrant-similar.png)


see result for anger - 
(Pdb) p result.points
[ScoredPoint(id='ffc30a96-0a9c-4b0c-bdfa-ca13a99013ed', version=4, score=0.9999999, payload={'text': 'I am so angry', 'dominant_emotion': 'anger', 'emotions': {'anger': 0.85, 'disgust': 0.05, 'fear': 0.05, 'joy': 0.01, 'sadness': 0.04}}, vector=None, shard_key=None, order_value=None), ScoredPoint(id='66d96be4-4456-4a66-8e95-61fbabeaa1d0', version=3, score=0.4017858, payload={'text': 'I am really happy', 'dominant_emotion': 'joy', 'emotions': {'anger': 0.016279602, 'disgust': 0.01874656, 'fear': 0.05179948, 'joy': 0.88792956, 'sadness': 0.06251001}}, vector=None, shard_key=None, order_value=None), ScoredPoint(id='a94a6d7e-c54e-4db5-9310-e5697fde1646', version=2, score=0.31094876, payload={'text': 'I am really happy with this', 'dominant_emotion': 'joy', 'emotions': {'anger': 0.016279602, 'disgust': 0.01874656, 'fear': 0.05179948, 'joy': 0.88792956, 'sadness': 0.06251001}}, vector=None, shard_key=None, order_value=None)]

you can see that "I am so angry is nearly a perfect match so that comes back first) - do more research on how the emotions change it