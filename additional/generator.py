# generator.py
import qrcode
import os
import cv2
import numpy as np
from PIL import Image

def generate_qr(user_id):
    data = f"{user_id}"
    img = qrcode.make(data)

    if not os.path.exists("qrcodes"):
        os.makedirs("qrcodes")

    img_path = f"qrcodes/{user_id}.png"
    img.save(img_path)
    print(f"QR code saved at {img_path}")

    # Display QR Code
    img_rgb = img.convert("RGB")
    img_np = np.array(img_rgb)
    img_cv = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    cv2.imshow(f"{user_id}'s QR Code", img_cv)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
