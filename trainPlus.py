from PIL import Image, ImageEnhance, ImageOps
import random
import os

def augment_image(image_path, save_dir, num_augmented_images=10):
    # .DS_Store 파일은 건너뛰기
    if image_path.endswith('.DS_Store'):
        return

    # 이미지 파일 이름에서 공백을 언더스코어(_)로 대체
    image_name = os.path.basename(image_path)
    image_name = image_name.replace(" ", "_")
    save_path = os.path.join(save_dir, image_name)

    image = Image.open(image_path)
    for i in range(num_augmented_images):
        augmented_image = image.copy()

        # 회전
        if random.random() > 0.5:
            angle = random.randint(-30, 30)
            augmented_image = augmented_image.rotate(angle)
        
        # 밝기 조절
        if random.random() > 0.5:
            enhancer = ImageEnhance.Brightness(augmented_image)
            augmented_image = enhancer.enhance(random.uniform(0.7, 1.3))

        # 색상 조절
        if random.random() > 0.5:
            enhancer = ImageEnhance.Color(augmented_image)
            augmented_image = enhancer.enhance(random.uniform(0.7, 1.3))
        
        # 플립
        if random.random() > 0.5:
            augmented_image = ImageOps.mirror(augmented_image)
        
        # 증강된 이미지 저장
        augmented_image.save(os.path.join(save_dir, f"augmented_{i}.jpg"))


# 모든 방향의 이미지를 증강하여 non_defective 폴더에 저장
directions = ['front', 'left', 'right', 'back', 'top', 'bottom']  # 모든 방향 리스트

for direction in directions:
    image_dir = f'dataset/train/{direction}/non_defective'  # 증강할 이미지가 있는 폴더
    save_dir = f'dataset/train/{direction}/defective'  # 증강된 이미지를 저장할 폴더

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    # image_dir에 있는 모든 이미지를 증강
    for image_file in os.listdir(image_dir):
        image_path = os.path.join(image_dir, image_file)
        augment_image(image_path, save_dir, num_augmented_images=5)
