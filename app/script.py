import requests

files = requests.get("http://localhost:5000/files").json()
images = [file for file in files if file["extension"] in [".png", ".jpg", ".jpeg"]]
for image in images:
    response = requests.post(
        f"http://localhost:5000/images/{image['id']}/resize",
        json={"new_width": 1920 * 2, "new_height": 1080 * 2},
    )
