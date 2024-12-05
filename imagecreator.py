import os
import openslide
from xml.etree import ElementTree as ET

pas_cpg_images_path = "images/pas-cpg"
patch_annotations_path = "patch_annotations/xml"
patch_images_path = "patches"

patch_size = 1024

def createImages():
    for fileName in os.listdir(pas_cpg_images_path):
        print(os.path.join(pas_cpg_images_path, fileName))
        slide = openslide.OpenSlide(
            os.path.join(pas_cpg_images_path, fileName))
        tree = ET.parse(os.path.join(patch_annotations_path,
                        fileName[:9] + "_inflammatory-cells.xml"))
        root = tree.getroot()
        annotations = root.find("Annotations")
        coordinates = []
        i = 0
        for annotation in annotations.findall("Annotation"):
            if annotation.get("Name").startswith("Patch"):
                coordinates = annotation.find("Coordinates").find("Coordinate")
                slide.read_region((int(coordinates.get("X")), int(coordinates.get("Y"))), 0, (patch_size, patch_size)).convert(
                    "RGB").save(patch_images_path + "/" + fileName[:9] + f"_inflammatory-cells_{i}.png")
                i += 1
createImages()


