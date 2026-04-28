from agents import Runner
from dotenv import load_dotenv
from src import root_agent
import base64
import asyncio
from pfd_system.src.fuel_cell_prompts import system_prompt

load_dotenv()

async def read_pfd(image_path):
    # image_path = "test/image.png"
    with open(image_path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "input_image",
                    "image_url": f"data:image/png;base64,{base64_image}",
                },
                {
                    "type": "input_text",
                    "text": system_prompt,
                },
            ],
        },
    ]

    result = await Runner.run(starting_agent=root_agent, input=messages)


    return result.final_output


if __name__ == "__main__":
    async def main():
        tasks = [
            read_pfd("test/620352_1_En_2_Fig1_HTML.png"),
            read_pfd("test/image.png")
        ]
        results = await asyncio.gather(*tasks)
        print(results)

    asyncio.run(main())