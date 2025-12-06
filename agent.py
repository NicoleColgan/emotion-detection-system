from typing import Dict, Any, List, Generator

from EmotionDetection.emotion_detection import emotion_detector
from embeddings import search_feedback

from openai import OpenAI

# Initialise OpenAI client (expects OPENAI_API_KEY in env)
client = OpenAI()

def generate_support_reply(text: str) -> Dict[str, Any]:
    """
    Agent workflow:
    1. Detect emotion for incoming feedback
    2. retrieve similar feedback from Qdrant
    3. Ask the LLM to generate a customer friendly reply giving this context
    """

    # 1. Run emotion detection
    emotions = emotion_detector(text)
    dominant_emotion = emotions.get("dominant_emotion")

    # 2. Retrieve similar feedback from Qdrant
    similar_items: List[Dict[str, Any]] = search_feedback(text) # use type checking for safety

    # Build compact string of similar items for the LLM prompt
    similar_items_str = ""
    # Loop over points and start index at 1 for readability in string (this doesnt affect the list itself)
    for idx, item in enumerate(similar_items.get("matches", []), start=1):
        feedback_text = item.get("text") or item.get("payload", {}).get("text")
        # why put feedback emotion in curly brackets???
        feedback_emotion = item.get("dominant_emotion") or item.get("payload", {}).get("dominant_emotion")
        
        if feedback_text:
            similar_items_str += f"Example {idx}:\n- Text: {feedback_text}\n- Emotion: {feedback_emotion}\n"
    if not similar_items_str:
        similar_items_str = "\n(No similar past feedback was found in the database)"

    # Call LLm to get reply
    system_prompt = (
        "You are a kind, conside customer support agent."
        "You receive a piece of customer feedback and its detected emotion"
        "Optionally, you also get a few similar past examples"
        "Your job is to write a short empathetic reply that acknowledges the emotion"
        "and either reassures the customer or gives them a clear next step"
        "Do NOT mention that you are using AI, emotions, or embeddings"
        "Just sound like a human support agent"
    )
    user_prompt = f"""
    Customer feedback: {text}

    Detected dominant emotion: {dominant_emotion}

    Similar past feedback and emotions {similar_items_str}

    Write a short reply (3-5 sentences max)
    """

    response = client.chat.completions.create(
        model="gpt-4.1-mini",   # lightweight and fast but still high-quality
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4 # clear but some variety
    )
    response_text = response.choices[0].message.content.strip()

    return {
        "input_feedback": text,
        "detected_emotion": dominant_emotion,
        "suggested_reply": response_text,
        "similar_feedback": similar_items
    }

def stream_support_reply(text: str) -> Generator[str, None, None]:
    """
    Streaming version of the support agent:
    - Detects emotions
    - Retrieves similar feedback from Qdrant
    - Streams an LLM reply chunk by chunk
    Yields plain text chunks of the reply
    """

    # 1. Emotion detection
    emotions = emotion_detector(text)
    dominant_emotion = emotions.get("dominant_emotion")

    # 2. Retrieve similar feedback
    similar_items = search_feedback(text)

    similar_items_str = ""
    for idx, item in enumerate(similar_items.get("matches", []), start=1):
        feedback_text = item.get("text") or item.get("payload", {}).get("text")
        # why put feedback emotion in curly brackets???
        feedback_emotion = item.get("dominant_emotion") or item.get("payload", {}).get("dominant_emotion")
        
        if feedback_text:
            similar_items_str += f"Example {idx}:\n- Text: {feedback_text}\n- Emotion: {feedback_emotion}\n"
    if not similar_items_str:
        similar_items_str = "\n(No similar past feedback was found in the database)"

    system_prompt = (
        "You are a kind, conside customer support agent."
        "You receive a piece of customer feedback and its detected emotion"
        "Optionally, you also get a few similar past examples"
        "Your job is to write a short empathetic reply that acknowledges the emotion"
        "and either reassures the customer or gives them a clear next step"
        "Do NOT mention that you are using AI, emotions, or embeddings"
        "Just sound like a human support agent"
    )
    user_prompt = f"""
    Customer feedback: {text}

    Detected dominant emotion: {dominant_emotion}

    Similar past feedback and emotions {similar_items_str}

    Write a short reply (3-5 sentences max)
    """
    # Call openAI with streaming enabled
    stream = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.4, # clear but some variety
        stream=True,    # API will return a generator that yields chunks as soon as they are available
    )

    # 4. Yield chunks of the reply text as soon as they are available
    for chunk in stream:    # Iterate over the streamed response - each iteration calls the `next()` function under the hood which gives you the next chunk - this is how we're calling the generator function from openai
        delta = chunk.choices[0].delta 
        content_piece = delta.content
        if not content_piece:
            continue    # skip role updates or empty chunks
        # Each chunk contains a small piece of the reply
        yield delta.content # send the chunk back to the caller as soon as it arrives
