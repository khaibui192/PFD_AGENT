import asyncio
import os
import shutil
from pathlib import Path
import base64
from dotenv import load_dotenv
from src import classifier_agent
from agents import Runner
import json
from datetime import datetime

load_dotenv()

DATASET_PATH = Path("dataset")
PFD_FOLDER = DATASET_PATH / "pfd"
NON_PFD_FOLDER = DATASET_PATH / "non_pfd"
RESULTS_FILE = "classification_results.json"

async def classify_image(image_path):
    """Classify a single image using the classifier agent."""
    try:
        # Resolve full path
        full_path = Path(image_path).resolve()
        
        if not full_path.exists():
            return {"error": f"File not found: {full_path}", "classification": "ERROR"}
        
        # Read and encode image
        with open(full_path, "rb") as f:
            image_data = f.read()
        
        base64_image = base64.b64encode(image_data).decode("utf-8")
        
        # Verify base64 encoding
        if not base64_image:
            return {"error": "Failed to encode image to base64", "classification": "ERROR"}
        
        # Create message with agents library format (matching main.py)
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": f"data:image/png;base64,{base64_image}",
                    }
                ],
            },
        ]
        
        result = await Runner.run(starting_agent=classifier_agent, input=messages)
        output = result.final_output
        if isinstance(output, str):
            import json
            output = json.loads(output)

        return output
    
    except Exception as e:
        return {"error": str(e), "classification": "ERROR"}

async def process_dataset():
    """Process all images in the dataset folder."""
    
    # Create output folders if they don't exist
    PFD_FOLDER.mkdir(parents=True, exist_ok=True)
    NON_PFD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    # Get all PNG images
    image_files = sorted(DATASET_PATH.glob("*.png"))
    
    print(f"Found {len(image_files)} images to classify")
    print(f"PFD folder: {PFD_FOLDER.resolve()}")
    print(f"NON_PFD folder: {NON_PFD_FOLDER.resolve()}")
    print()
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "total_images": len(image_files),
        "pfd_count": 0,
        "non_pfd_count": 0,
        "error_count": 0,
        "classifications": []
    }
    
    # Process each image
    for idx, image_file in enumerate(image_files, 1):
        print(f"[{idx}/{len(image_files)}] Classifying {image_file.name}...", end=" ")
        
        classification = await classify_image(image_file)
        
        # Extract classification result
        class_label = classification.get("classification", "ERROR")
        confidence = classification.get("confidence", 0)
        reason = classification.get("reason", "")
        
        print(f"{class_label} (confidence: {confidence:.2f})")
        
        # Determine destination folder
        if class_label == "PFD":
            dest_folder = PFD_FOLDER
            results["pfd_count"] += 1
        elif class_label == "NON_PFD":
            dest_folder = NON_PFD_FOLDER
            results["non_pfd_count"] += 1
        else:
            dest_folder = NON_PFD_FOLDER  # Default to NON_PFD for errors
            results["error_count"] += 1
        
        # Copy image to destination
        dest_path = dest_folder / image_file.name
        shutil.copy2(image_file, dest_path)
        
        # Record result
        results["classifications"].append({
            "filename": image_file.name,
            "classification": class_label,
            "confidence": confidence,
            "reason": reason,
            "destination": str(dest_path.relative_to(DATASET_PATH.parent))
        })
    
    # Save results to JSON
    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)
    
    # Print summary
    print("\n" + "="*60)
    print("CLASSIFICATION COMPLETE")
    print("="*60)
    print(f"Total images: {results['total_images']}")
    print(f"PFD images: {results['pfd_count']}")
    print(f"NON_PFD images: {results['non_pfd_count']}")
    print(f"Errors: {results['error_count']}")
    print(f"Results saved to: {RESULTS_FILE}")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(process_dataset())
