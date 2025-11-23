from EmotionDetection.emotion_detection import emotion_detector
import unittest

class TestEmotionDetection(unittest.TestCase):

    def test_emotion_detector(self):
        res1 = emotion_detector("Im Glad this happened").get('dominant_emotion')
        self.assertEqual(res1, 'joy')

        res2 = emotion_detector("Im really mad about this").get('dominant_emotion')
        self.assertEqual(res2, 'anger')

        res3 = emotion_detector("Im feeling disgusted just hearing about this").get('dominant_emotion')
        self.assertEqual(res3, 'disgust')

        res4 = emotion_detector("Im so sad about this").get('dominant_emotion')
        self.assertEqual(res4, 'sadness')

        res5 = emotion_detector("Im really afraid this will happen").get('dominant_emotion')
        self.assertEqual(res5, 'fear')
             
        
unittest.main()