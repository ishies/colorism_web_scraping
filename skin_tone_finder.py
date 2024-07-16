import cv2
import numpy as np
import json
import requests

# Function to calculate average RGB value in a region defined by a contour
def average_rgb_from_contour(image, contour):
    # Create a mask for the contour
    contour_mask = np.zeros(image.shape[:2], dtype=np.uint8)  # Single channel mask
    cv2.drawContours(contour_mask, [contour], -1, 255, thickness=cv2.FILLED)

    # Calculate the number of non-zero pixels in the mask
    pixels = np.sum(contour_mask // 255)  # Convert to 1s and sum

    # Apply the mask to the original image
    masked_image = cv2.bitwise_and(image, image, mask=contour_mask)

    # Calculate average RGB within the masked region
    if pixels > 0:
        average_color = cv2.mean(masked_image, mask=contour_mask)[:3]  # Calculate mean of RGB channels
        average_color = [int(round(c)) for c in average_color[::-1]]  # Round and convert to integer
    else:
        average_color = None
    
    return average_color

# Load JSON data
with open('fabindia_kids_products.json', 'r') as f:
    data = json.load(f)

# Define bounds for skin detection in HSV
lower_skin = np.array([0, 60, 80], dtype=np.uint8)
upper_skin = np.array([20, 255, 255], dtype=np.uint8)

# Process each image link in the JSON
for entry in data:
    image_url = entry['image']
    response = requests.get(image_url)
    image_data = response.content

    # Load image using OpenCV
    image_array = np.frombuffer(image_data, np.uint8)
    img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    if img is None:
        print(f"Unable to load image from URL: {image_url}")
        continue

    # Convert BGR to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Create a mask for skin detection
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Apply morphological operations to refine the mask
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=2)
    mask = cv2.dilate(mask, kernel, iterations=2)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Process the first contour (if any)
    if contours:
        first_contour = contours[0]
        avg_rgb = average_rgb_from_contour(img, first_contour)

        if avg_rgb is not None:
            # Add average RGB to the entry in the JSON
            entry['average_rgb'] = avg_rgb
        else:
            print(f"Unable to calculate average RGB for image: {image_url}")
    else:
        print(f"No contours found for image: {image_url}")

# Save updated JSON
with open('fab_kids_rgb.json', 'w') as f:
    json.dump(data, f, indent=4)

print("Processing complete. Updated JSON saved.")