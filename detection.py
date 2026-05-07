import torch
from torchvision import transforms, models
from PIL import Image
from data_loader import SkinDiseaseDataset

MODEL_PATH = 'models/skin_disease_epoch10.pt'
DISEASES_LIST = 'diseases_list.txt'
IMAGE_PATH = 'test.jpg'  # Example: replace with your test image path

def load_disease_list(path):
    with open(path) as f:
        return [d.strip() for d in f.readlines() if d.strip()]

def predict(image_path, model_path=MODEL_PATH, diseases_list_path=DISEASES_LIST):
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    diseases = load_disease_list(diseases_list_path)
    model = models.resnet18(weights=None)
    model.fc = torch.nn.Linear(model.fc.in_features, len(diseases))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor()
    ])
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(img)
        _, pred = outputs.max(1)
    print(f"Prediction: {diseases[pred.item()]}")
    return diseases[pred.item()]

if __name__ == '__main__':
    predict(IMAGE_PATH)
