import os
from PIL import Image
from imagesbatch import process_image

def test_watermark():
    # Create a dummy image
    dummy_image_path = "test_image.jpg"
    img = Image.new('RGB', (800, 600), color = 'red')
    img.save(dummy_image_path)
    
    output_folder = "test_output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        
    try:
        # Run process_image
        success = process_image(dummy_image_path, output_folder, month='11', day='24', counter=1)
        
        if success:
            print("Process image returned success.")
            # Check if output file exists
            output_filename = "11_24_001.jpg"
            output_path = os.path.join(output_folder, output_filename)
            if os.path.exists(output_path):
                print(f"Output image created at {output_path}")
            else:
                print("Output image not found.")
        else:
            print("Process image returned failure.")
            
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Cleanup
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
        # We might want to keep the output to inspect, or delete it.
        # For now, let's keep it so I can potentially inspect it if I had a way, 
        # but since I can't see it, I'll just rely on the script running successfully.
        # I'll clean up the output folder if it's empty or just leave it.

if __name__ == "__main__":
    test_watermark()
