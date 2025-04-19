from PIL import Image
from torchvision import transforms


# Função para transformar a imagem de entrada
def transform_input_data(image_path):
    transform_test = transforms.Compose(
        [
            transforms.Resize((224, 224)),  # Redimensiona para 224x224
            transforms.Grayscale(
                num_output_channels=1
            ),  # Converte para escala de cinza
            transforms.ToTensor(),  # Converte a imagem para tensor
            transforms.Normalize(mean=[0.1854], std=[0.1793]),  # Normaliza a imagem
        ]
    )

    # Abre a imagem
    image = Image.open(image_path).convert("RGB")  # Converte para RGB se não for
    # Aplica as transformações
    image = transform_test(image)

    return image
