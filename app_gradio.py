import gradio as gr
from PIL import Image
from detection import SkinDiseasePredictor

predictor = SkinDiseasePredictor()

def classify_skin_image(image):
    if image is None:
        return None, "Please upload an image."
    
    # Save temp PIL image
    temp_path = "temp_upload.jpg"
    if isinstance(image, Image.Image):
        image.save(temp_path)
    else:
        Image.fromarray(image).save(temp_path)
        
    results = predictor.predict(temp_path, top_k=7)
    # Convert list of (class_name, conf_pct) to dict for Gradio Label: {class_name: conf_decimal}
    conf_dict = {cls.replace("_", " "): conf / 100.0 for cls, conf in results}
    return conf_dict

demo = gr.Interface(
    fn=classify_skin_image,
    inputs=gr.Image(type="pil", label="Upload Skin Lesion Image"),
    outputs=gr.Label(num_top_classes=5, label="Prediction Probabilities"),
    title="🔬 AI Skin Disease Detection & Classifier",
    description="""
    ### Educational Demo — Dermatological Image Classification
    Upload an image of a skin lesion to analyze it using a fine-tuned ResNet-18 model trained on the HAM10000 dataset.
    
    ⚠️ **Disclaimer:** This application is for **educational & demonstration purposes only**. It is NOT a medical device and should NEVER replace professional medical advice, diagnosis, or treatment.
    """,
    examples=[],
    theme="soft"
)

if __name__ == "__main__":
    demo.launch()
