# 🧠 System Workflow

1. User logs into the system.
2. User uploads an OCT retinal image.
3. The image is preprocessed and resized.
4. The trained TensorFlow deep learning model analyzes the image.
5. The model predicts one of the following classes:
   - CNV
   - DME
   - Drusen
   - Normal
6. The prediction result is displayed with a confidence score.
7. The prediction is stored in the user's history for future reference.