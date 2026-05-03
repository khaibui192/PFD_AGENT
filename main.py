from dotenv import load_dotenv
from agents import Runner
from src import classifier_agent, pfd_agent, inspection_agent
from src.helper.response_helper import safe_json
import base64
import asyncio
# from pdf2image import convert_from_path
import argparse
# from src.prompts.fuel_cell_prompts import SYSTEM_PROMPT

load_dotenv()

async def run_classifier(image):

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
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

async def run_pfd_agent(image):

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{image}",
                }
            ],
        },
    ]

    result = await Runner.run(
        starting_agent=pfd_agent,
        input=messages
    )

    response = result.final_output
    return safe_json(response)

async def run_inspection(graph):

    messages = [
        {
            "role": "user",
            "content": str(graph)
        }
    ]

    result = await Runner.run(
        starting_agent=inspection_agent,
        input=messages
    )

    response = result.final_output
    return safe_json(response)

async def root_pipeline(image, image_path):

    cls = await run_classifier(image)
    if cls["classification"] == "NON_PFD":
        return {
            "classification": "NON_PFD",
            "final_status": "skipped_non_pfd"
        }

    best_graph = None
    best_violations = 999
    last_result = None

    for i in range(3):

        graph = await run_pfd_agent(image)
        print(graph)
        result = await run_inspection(graph)
        last_result = result

        if len(result["violations"]) < best_violations:
            best_graph = graph
            best_violations = len(result["violations"])

        if result["is_valid"]:
            return {
                "classification": cls["classification"],
                "final_status": "valid",
                "iterations": i + 1,
                "final_graph": graph,
                "remaining_violations": []
            }

    return {
        "path": image_path,
        "classification": cls["classification"],
        "final_status": "invalid_but_best_effort",
        "iterations": 3,
        "final_graph": best_graph,
        "remaining_violations": last_result["violations"] if last_result else []
    }

async def read_pfd(image_path):
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")
    
    result = await root_pipeline(base64_image, image_path)

    return result


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--images", nargs="+", required=True, help="List of image paths")
    args = parser.parse_args()
    
    
    async def main():
        tasks = [read_pfd(path) for path in args.images]
        results = await asyncio.gather(*tasks)
        print(results)

    asyncio.run(main())