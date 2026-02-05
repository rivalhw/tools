import os
from PIL import Image
from imagesbatch import process_image

# Create a dummy image
test_dir = "test_output"
if not os.path.exists(test_dir):
    os.makedirs(test_dir)

dummy_image_path = os.path.join(test_dir, "test_image.jpg")
img = Image.new('RGB', (800, 600), color = (73, 109, 137))
img.save(dummy_image_path)

# Process the image
process_image(dummy_image_path, test_dir, max_width=1280, max_size=1000 * 1024, month='11', day='24', counter=1)

print(f"Test image created and processed in {test_dir}")
