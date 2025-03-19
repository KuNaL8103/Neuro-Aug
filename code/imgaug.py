import sys
import os
import random
from PIL import Image, ImageEnhance, ImageFilter

def add_noise(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    pixels = image.load()
    for i in range(image.size[0]):
        for j in range(image.size[1]):
            r, g, b = pixels[i, j]
            noise = random.randint(-20, 20)
            pixels[i, j] = (
                max(0, min(r + noise, 255)),
                max(0, min(g + noise, 255)),
                max(0, min(b + noise, 255))
            )
    return image

def mirror_image(image):
    return image.transpose(Image.FLIP_LEFT_RIGHT)

def shift_image(image, shift_x, shift_y):
    return image.transform(image.size, Image.AFFINE, (1, 0, shift_x, 0, 1, shift_y))

def augment_image(image):
    augmentations = [
        lambda img: img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.5, 1.5))),
        lambda img: ImageEnhance.Brightness(img).enhance(random.uniform(0.8, 1.2)),
        lambda img: ImageEnhance.Contrast(img).enhance(random.uniform(0.8, 1.2)),
        lambda img: add_noise(img),
        lambda img: img.rotate(random.choice([90, 180, 270])),
        lambda img: mirror_image(img),
        lambda img: shift_image(img, random.randint(20, 30), random.randint(-10, 10))
    ]
    
    num_augmentations = random.randint(1, 4)
    selected_augmentations = random.sample(augmentations, min(num_augmentations, len(augmentations)))
    
    try:
        for augmentation in selected_augmentations:
            image = augmentation(image)
        return image
    except Exception as e:
        print(f"Error applying augmentation: {e}")
        return image 

def main(input_folder, output_folder, num_copies):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    processed = 0
    skipped = 0
    
    valid_extensions = ('.jpg', '.jpeg', '.png', '.bmp')
    
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(valid_extensions):
            input_path = os.path.join(input_folder, filename)
            try:
                img = Image.open(input_path)
                
                for i in range(num_copies):
                    augmented_img = augment_image(img.copy())
                    base_name = os.path.splitext(filename)[0]
                    output_filename = f"{base_name}_aug_{i+1}.jpg"
                    output_path = os.path.join(output_folder, output_filename)
                    augmented_img.save(output_path, 'JPEG')
                
                processed += 1
                print(f"Processed: {filename} ({processed}/{len(os.listdir(input_folder))})")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")
                skipped += 1
        else:
            print(f"Skipping {filename} - not a supported image format")
            skipped += 1
    
    print(f"\nSummary: {processed} images processed, {skipped} skipped")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python program.py <folder of jpg images> <output folder> <number of augmented copies>")
        sys.exit(1)
    
    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    
    try:
        num_copies = int(sys.argv[3])
        if num_copies <= 0:
            raise ValueError("Number of copies must be positive")
    except ValueError as e:
        print(f"Error: {e}")
        print("Number of copies must be a positive integer")
        sys.exit(1)
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' does not exist")
        sys.exit(1)
    
    main(input_folder, output_folder, num_copies)
