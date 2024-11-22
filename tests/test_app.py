import unittest
from app import input, results 

class TestHeartDiseasePrediction(unittest.TestCase):
    
    def setUp(self):
        # Load the model once for all tests
        self.model = load_model("model/model (1).pkl")  # Assuming your model is stored as a .pkl file

    def test_input(self):
        # Test if preprocessing returns the correct format
        input_data = {"age": 45, "sex": "Male", "cholesterol": 200}
        processed_data = preprocess_input(input_data)
        self.assertEqual(len(processed_data), 3)
        self.assertTrue(all(isinstance(x, (int, float)) for x in processed_data))

    def test_results(self):
        # Test the prediction output
        processed_data = [45, 1, 200]  # Example processed input
        result = predict(self.model, processed_data)
        self.assertIn(result, [0, 1])  # Prediction should be 0 or 1 (binary classification)

    def test_load_model(self):
        # Test if model loads correctly
        self.assertIsNotNone(self.model)