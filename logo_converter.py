import base64

# Read the image file
with open('attached_assets/idggKYNyFJ_logos.jpeg', 'rb') as img_file:
    # Convert to base64
    b64_string = base64.b64encode(img_file.read()).decode('utf-8')
    
# Print the result
print(f"Base64 logo: {b64_string[0:50]}...")
print(f"Length: {len(b64_string)}")

# Save to file for use in app.py
with open('logo_base64.txt', 'w') as f:
    f.write(b64_string)
    
print("Base64 encoded logo saved to logo_base64.txt")