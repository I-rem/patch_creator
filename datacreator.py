import random
import os
import xml.etree.ElementTree as ET
import json
import pickle

pas_cpg_annotations_xml_path = "annotations/xml"
patch_annotations_path = "patch_annotations/xml"
patch_images_out_path = "patches"

lymphocyte = 0
monocyte = 1

patch_size = 1024

monocyte_box_size = 42
lymphocyte_box_size = 16

train_ratio = 0.8 # 80% train, 20% test



patchId = 0
dataset_dict = []
for fileName in os.listdir(pas_cpg_annotations_xml_path):
    patches = []
    patchesDict = []
    with open(os.path.join(patch_annotations_path, fileName[:9] + "_inflammatory-cells.xml")) as f:
        patch_xml = ET.parse(f)
        root = patch_xml.getroot()
        for annotation in root.find("Annotations").findall("Annotation"):
            if annotation.get("Name").startswith("Patch"):
                coordinates = annotation.find(
                    "Coordinates").findall("Coordinate")
                patches.append([int(coordinates[0].get("X")),
                               int(coordinates[0].get("Y")), patchId])
                patch_last_char = annotation.get("Name")[-1]
                patchesDict.append({"file_name": os.path.join(patch_images_out_path, fileName[:9] + f"_inflammatory-cells_{patch_last_char}.png"), "imageId": str(
                    patchId), "height": patch_size, "width": patch_size, "annotations": []})
                patchId += 1

    with open(os.path.join(pas_cpg_annotations_xml_path, fileName), "r") as f:
        cell_xml = ET.parse(f)
        root = cell_xml.getroot()
        for annotation in root.find("Annotations").findall("Annotation"):
            if annotation.get("Type") == "Dot":
                coordinates = annotation.find("Coordinates").find("Coordinate")
                x = int(float(coordinates.get("X")))
                y = int(float(coordinates.get("Y")))
                for i, patch in enumerate(patches):
                    if x >= patch[0] and x <= patch[0] + patch_size and y >= patch[1] and y <= patch[1] + patch_size:
                        box_size = monocyte_box_size if annotation.get(
                            "PartOfGroup") == "monocytes" else lymphocyte_box_size
                        x_min = int(max(0, x - patch[0] - box_size / 2))
                        y_min = int(max(0, y - patch[1] - box_size / 2))
                        w = int(min(x_min + box_size, 1024) - x_min)
                        h = int(min(y_min + box_size, 1024) - y_min)
                        patchesDict[i]["annotations"].append(
                            {"bbox": [x_min, y_min, w, h], "bbox_mode": 1, "category_id": lymphocyte if annotation.get("PartOfGroup") == "lymphocytes" else monocyte})
                        break
    dataset_dict.extend(patchesDict)

random.seed(42)
random.shuffle(dataset_dict)
train_size = int(len(dataset_dict) * train_ratio)
train_data = dataset_dict[:train_size]
test_data = dataset_dict[train_size:]

with open("test.json", "w") as f:
    json.dump(test_data, f)
with open("train.json", "w") as f:
    json.dump(train_data, f)

with open("test.pkl", "wb") as f:
    pickle.dump(test_data, f)
with open("train.pkl", "wb") as f:
    pickle.dump(train_data, f)