import cv2


def vision_agent(state):
    if "vision" not in state.get("selected_agents", []):
        return {}

    image_path = state.get("image_path")

    if not image_path:
        return {
            "vision_result": {
                "error": "No image path provided"
            }
        }

    image = cv2.imread(image_path)

    if image is None:
        return {
            "vision_result": {
                "error": f"Could not read image at {image_path}"
            }
        }

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()
    brightness = gray.mean()
    height, width = gray.shape

    if blur_score < 100:
        image_quality = "blurry"
        confidence = 0.6
    elif brightness < 50 or brightness > 220:
        image_quality = "poor_lighting"
        confidence = 0.6
    else:
        image_quality = "good"
        confidence = 0.85

    return {
        "vision_result": {
            "image_quality": image_quality,
            "blur_score": round(float(blur_score), 2),
            "brightness": round(float(brightness), 2),
            "resolution": f"{width}x{height}",
            "confidence": confidence
        }
    }