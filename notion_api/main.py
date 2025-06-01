from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import requests
import os
app = FastAPI()

class NotionAppendRequest(BaseModel):
    page_id: str
    image_list: List[str] = []
    bullet_list: List[str] = []

@app.post("/append_notion_blocks/")
def append_notion_blocks(req: NotionAppendRequest):
    token = os.getenv("NOTION_API_KEY")
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    url = f"https://api.notion.com/v1/blocks/{req.page_id}/children"

    children_blocks = [
        {
            "object": "block",
            "type": "image",
            "image": {
                "type": "external",
                "external": {
                    "url": image_url
                }
            }
        } for image_url in req.image_list
    ] + [
        {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": [{
                    "type": "text",
                    "text": {
                        "content": bullet
                    }
                }]
            }
        } for bullet in req.bullet_list
    ]

    payload = {"children": children_blocks}

    response = requests.patch(url, headers=headers, json=payload)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return {"status": "success", "data": response.json()}
