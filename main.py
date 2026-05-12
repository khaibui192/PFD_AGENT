from dotenv import load_dotenv
from agents import Runner
from src import classifier_agent
from src.helper.response_helper import safe_json, collect_images
import base64
import asyncio
import argparse
from pathlib import Path
import shutil

load_dotenv()

async def run_classifier(image):

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{image}",
                }
            ],
        },
    ]

    result = await Runner.run(
        starting_agent=classifier_agent,
        input=messages
    )
    response = result.final_output
    return safe_json(response)

async def classify_and_organize(image_path, output_folder):
    """Classify an image and copy it to the appropriate folder."""
    
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    # Classify
    result = await run_classifier(base64_image)
    classification = result.get("classification", "ERROR")
    confidence = result.get("confidence", 0.0)
    
    # Determine output folder
    if classification == "PFD":
        target_folder = Path(output_folder) / "PFD"
    elif classification == "NON_PFD":
        target_folder = Path(output_folder) / "NON_PFD"
    elif classification == "MIXED":
        target_folder = Path(output_folder) / "MIXED"
    else:
        target_folder = Path(output_folder) / "ERROR"
    
    target_folder.mkdir(parents=True, exist_ok=True)
    
    # Copy file
    target_path = target_folder / Path(image_path).name
    shutil.copy2(image_path, target_path)
    
    return {
        "path": image_path,
        "classification": classification,
        "confidence": confidence,
        "reason": result.get("reason", ""),
        "target": str(target_path)
    }

async def read_pfd(image_path, output_folder):
    return await classify_and_organize(image_path, output_folder)

async def main(args):
    paths = collect_images(args.images, args.folder)
    output_folder = args.output or "classified_images"

    print(f"Processing {len(paths)} files...")
    print(f"Output folder: {output_folder}")

    tasks = [(p, read_pfd(p, output_folder)) for p in paths]

    results = await asyncio.gather(
        *[t[1] for t in tasks],
        return_exceptions=True
    )

    final = [
        (str(res) if isinstance(res, Exception) else res)
        for (path, _), res in zip(tasks, results)
    ]

    # Print summary
    pfd_count = sum(1 for r in final if isinstance(r, dict) and r.get("classification") == "PFD")
    non_pfd_count = sum(1 for r in final if isinstance(r, dict) and r.get("classification") == "NON_PFD")
    mixed_count = sum(1 for r in final if isinstance(r, dict) and r.get("classification") == "MIXED")
    
    print(f"\n{'='*50}")
    print("CLASSIFICATION SUMMARY")
    print(f"{'='*50}")
    print(f"PFD images: {pfd_count}")
    print(f"NON_PFD images: {non_pfd_count}")
    print(f"MIXED images: {mixed_count}")
    print(f"Total processed: {len(final)}")
    print(f"\nImages organized in: {output_folder}/")

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description="Classify images as PFD or NON_PFD and organize them into folders"
    )

    parser.add_argument("--images", nargs="+", help="List of image paths")
    parser.add_argument("--folder", type=str, help="Folder containing images")
    parser.add_argument("--output", type=str, default="classified_images", help="Output folder for classified images")

    args = parser.parse_args()

    if not args.images and not args.folder:
        parser.error("At least one of --images or --folder is required")

    asyncio.run(main(args))