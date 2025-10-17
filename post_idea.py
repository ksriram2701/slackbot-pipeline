import requests
import json


def generate_post_idea_with_groq(api_key, cluster_id, cluster_data):
    keywords = [item["keyword"] for item in cluster_data]
    snippets = [item["serpapi_result"]["snippet"] for item in cluster_data if item.get("serpapi_result")]
    snippet_text = " ".join(snippets) if snippets else "No snippets available."
    prompt = f"""
Based on the following keywords and web snippets, generate one unique, attention-grabbing post idea.

- Create a short **heading** (5-8 words) for the post.  
- Write a **brief paragraph** describing the idea in about 4 lines.  
- Keep it concise and engaging.  

Keywords: {', '.join(keywords)}
Web Snippets:
{snippet_text}

Output format:
---


Heading: <your heading here>
Post Idea: <4-line paragraph describing the post idea>


---
"""

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": [{"role": "system", "content": "You are a creative marketing expert."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.85
    }
    try:
        resp = requests.post("https://api.groq.com/openai/v1/chat/completions",
                             headers=headers, data=json.dumps(payload), timeout=60)
        resp.raise_for_status()
        data = resp.json()
        idea = data["choices"][0]["message"]["content"].strip()
        return {"cluster_id": cluster_id, "post_idea": idea}
    except Exception as e:
        print(f"Error generating post idea for cluster {cluster_id}: {e}")
        return {"cluster_id": cluster_id, "post_idea": None}
