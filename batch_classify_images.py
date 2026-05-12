import asyncio
import base64
import json
from pathlib import Path
from src import classifier_agent
from dotenv import load_dotenv

load_dotenv()

async def classify_image(image_path):
    """Classify a single image using the classifier agent."""
    try:
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Determine image type from file extension
        image_type = image_path.suffix.lower()
        if image_type in ['.jpg', '.jpeg']:
            image_type = 'image/jpeg'
        elif image_type == '.png':
            image_type = 'image/png'
        else:
            image_type = 'image/png'  # default
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_image",
                        "image_url": {
                            "url": f"data:{image_type};base64,{base64_image}"
                        }
                    }
                ],
            },
        ]
        
        # Call classifier agent
        result = await classifier_agent(input=messages)
        
        # Parse response
        try:
            if isinstance(result, dict):
                return result
            else:
                # Try to parse as JSON string
                classification_result = json.loads(str(result))
                return classification_result
        except:
            return {
                "classification": "ERROR",
                "confidence": 0.0,
                "reason": f"Failed to parse response: {result}"
            }
    
    except Exception as e:
        return {
            "classification": "ERROR",
            "confidence": 0.0,
            "reason": f"Error processing image: {str(e)}"
        }

async def batch_classify_and_organize(input_folder, output_base_folder="classified_images"):
    """
    Classify all images in input_folder and organize them into subfolders.
    
    Args:
        input_folder: Path to folder containing images
        output_base_folder: Base folder for output (will create PFD/ and NON_PFD/ subfolders)
    """
    input_path = Path(input_folder)
    output_path = Path(output_base_folder)
    
    # Create output directories
    pfd_folder = output_path / "PFD"
    non_pfd_folder = output_path / "NON_PFD"
    mixed_folder = output_path / "MIXED"
    
    pfd_folder.mkdir(parents=True, exist_ok=True)
    non_pfd_folder.mkdir(parents=True, exist_ok=True)
    mixed_folder.mkdir(parents=True, exist_ok=True)
    
    # Find all image files
    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    image_files = [f for f in input_path.rglob('*') 
                   if f.suffix.lower() in image_extensions and f.is_file()]
    
    print(f"Found {len(image_files)} images to classify")
    
    results = {
        "processed_at": str(Path.cwd()),
        "total_images": len(image_files),
        "classified": {
            "PFD": [],
            "NON_PFD": [],
            "MIXED": [],
            "ERROR": []
        }
    }
    
    # Process images
    for i, image_file in enumerate(image_files, 1):
        print(f"\n[{i}/{len(image_files)}] Processing: {image_file.name}")
        
        classification = await classify_image(image_file)
        cls_type = classification.get("classification", "ERROR")
        
        print(f"  Classification: {cls_type} (confidence: {classification.get('confidence', 'N/A')})")
        print(f"  Reason: {classification.get('reason', 'N/A')}")
        
        # Copy image to appropriate folder
        if cls_type == "PFD":
            target_path = pfd_folder / image_file.name
            results["classified"]["PFD"].append(image_file.name)
        elif cls_type == "NON_PFD":
            target_path = non_pfd_folder / image_file.name
            results["classified"]["NON_PFD"].append(image_file.name)
        elif cls_type == "MIXED":
            target_path = mixed_folder / image_file.name
            results["classified"]["MIXED"].append(image_file.name)
        else:
            target_path = output_path / "ERROR" / image_file.name
            target_path.parent.mkdir(parents=True, exist_ok=True)
            results["classified"]["ERROR"].append(image_file.name)
        
        # Copy file
        try:
            with open(image_file, 'rb') as src:
                with open(target_path, 'wb') as dst:
                    dst.write(src.read())
            print(f"  ✓ Copied to {target_path.parent.name}/")
        except Exception as e:
            print(f"  ✗ Error copying file: {e}")
    
    # Summary
    print(f"\n{'='*50}")
    print("CLASSIFICATION SUMMARY")
    print(f"{'='*50}")
    print(f"PFD images: {len(results['classified']['PFD'])}")
    print(f"NON_PFD images: {len(results['classified']['NON_PFD'])}")
    print(f"MIXED images: {len(results['classified']['MIXED'])}")
    print(f"ERROR: {len(results['classified']['ERROR'])}")
    
    # Save results to JSON
    results_file = output_path / "classification_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to: {results_file}")
    
    return results

if __name__ == "__main__":
    import sys
    
    # Get input folder from command line or use default
    input_folder = sys.argv[1] if len(sys.argv) > 1 else "dataset"
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "classified_images"
    
    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")
    
    # Run classification
    asyncio.run(batch_classify_and_organize(input_folder, output_folder))
