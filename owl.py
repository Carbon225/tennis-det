import torch
from transformers import AutoProcessor, OwlViTForObjectDetection


processor = AutoProcessor.from_pretrained("google/owlvit-base-patch16")
model = OwlViTForObjectDetection.from_pretrained("google/owlvit-base-patch16").eval()


def predict(images, class_names, confidence_threshold):
    for img in images:
        assert img.mode == "RGB", "Images must be RGB."
        assert img.size == images[0].size, "Images must have the same size."
    inputs = processor(images=images, text=[class_names for _ in images], return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    target_sizes = torch.tensor([images[0].size[::-1]])
    results = processor.post_process_object_detection(
        outputs=outputs, threshold=confidence_threshold, target_sizes=target_sizes)
    detections = [[]]
    for i in range(len(images)):
        boxes, scores, labels = results[i]["boxes"], results[i]["scores"], results[i]["labels"]
        for box, score, label in zip(boxes, scores, labels):
            xmin, ymin, xmax, ymax = box.tolist()
            detections[i].append([label.tolist(), xmin, ymin, xmax, ymax])
    return detections
