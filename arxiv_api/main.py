from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import json

app = FastAPI()

@app.get("/arxiv/{paper_id}")
def get_arxiv_info(paper_id: str):
    try:
        url = f"https://arxiv.org/html/{paper_id}"
        response = requests.get(url)
        response.raise_for_status()
        html = response.text
        soup = BeautifulSoup(html, "html.parser")
        h1_tag = soup.select_one("#main")
        title = soup.select('title')[0].getText()
        abstract = soup.select("body > div > div > article > div.ltx_abstract > p")[0].get_text()
        section_list = []
        for section in soup.select("body > div > div > article > section"):
            ## Extract section title
            heading = section.select("section > h2")[0].get_text().replace('\n', ' ').strip()
            ## Extract content
            content = ''
            for para in section.select("section > div.ltx_para"):
                for p in para.select('p'):
                    content += p.get_text().replace('\n','').strip() + "\n"
            ## Extract images
            image_list = []
            for img_meta in section.select("figure.ltx_figure"):
                if img_meta.find("img"):
                    img_url = url + '/' + img_meta.find("img")['src']
                    caption = img_meta.find("figcaption").get_text().strip()
                    image_list += [{
                        "image_url": img_url,
                        "caption": caption
                    }]
            section_list += [{
                "section_title": heading,
                "content": content.strip(),
                "images": image_list
            }]
            

        # Build structured result
        result = {
            "url": url,
            "title": title,
            "abstract": abstract,
            "sections": section_list
        }
    except:
        return {
            "url": None,
            "title": None,
            "abstract": None,
            "sections": None,
        }

    return result
