from slack_bolt import App
from slack_sdk import WebClient
from dotenv import load_dotenv
import os
import csv
import tempfile
import requests
import threading
from keywords import get_keywords
from preprocess import preprocess_keywords
from embedding import get_embeddings
from clustering import reduce_dimensionality, cluster_keywords
from serpapi import get_top_result_serpapi
from outline import generate_outline_with_groq
from post_idea import generate_post_idea_with_groq
from pdf_report import generate_pdf_report

# -----------------------------
# Load environment variables
# -----------------------------
load_dotenv()
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
SERPAPI_KEY = os.getenv("SERPAPI_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Slack App
app = App(token=SLACK_BOT_TOKEN)

# -----------------------------
# Pipeline function
# -----------------------------
def run_pipeline(input_data):
    raw_keywords = get_keywords(input_data)
    cleaned_keywords = preprocess_keywords(raw_keywords)
    embeddings = get_embeddings(cleaned_keywords)
    reduced = reduce_dimensionality(embeddings)
    clusters_dict, labels = cluster_keywords(reduced, cleaned_keywords)

    cluster_results = {}
    for cid, keyword_list in clusters_dict.items():
        cluster_results[cid] = []
        for kw in keyword_list:
            serp = get_top_result_serpapi(kw, SERPAPI_KEY)
            cluster_results[cid].append({"keyword": kw, "serpapi_result": serp})

    outlines = {}
    post_ideas = {}
    for cid, data in cluster_results.items():
        if cid == -1:
            continue
        outlines[cid] = generate_outline_with_groq(GROQ_API_KEY, cid, data)["outline"]
        post_ideas[cid] = generate_post_idea_with_groq(GROQ_API_KEY, cid, data)["post_idea"]

    pdf_path = "content_report.pdf"
    generate_pdf_report(pdf_path, raw_keywords, cleaned_keywords, clusters_dict, post_ideas, outlines)
    return pdf_path

# -----------------------------
# Background task runner
# -----------------------------
def background_task(client: WebClient, user_id, input_data):
    try:
        pdf_path = run_pipeline(input_data)

        # Open DM channel with the user
        dm_response = client.conversations_open(users=user_id)
        channel_id = dm_response["channel"]["id"]

        # Upload PDF to DM channel
        client.files_upload_v2(
            channel=channel_id,
            file=pdf_path,
            title="ContentBot Report",
            initial_comment="✅ Your PDF report is ready!"
        )

    except Exception as e:
        # Send error message to DM if something goes wrong
        try:
            dm_response = client.conversations_open(users=user_id)
            channel_id = dm_response["channel"]["id"]
            client.chat_postMessage(channel=channel_id, text=f"❌ Error processing keywords: {e}")
        except:
            print(f"Failed to send error message: {e}")

# -----------------------------
# Slash command handler
# -----------------------------
@app.command("/upload_keywords")
def handle_upload(ack, body, client: WebClient):
    ack("Processing your keywords... ⏳")  # immediate response
    user_id = body["user_id"]
    text_input = body.get("text", "").strip()

    input_data = []

    # CSV file input
    if text_input.lower().endswith(".csv"):
        try:
            response = requests.get(text_input)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(mode="w+", delete=False) as tmp_file:
                tmp_file.write(response.text)
                tmp_file.flush()
                with open(tmp_file.name, newline="", encoding="utf-8") as csvfile:
                    reader = csv.reader(csvfile)
                    for row in reader:
                        input_data.extend([kw.strip() for kw in row if kw.strip()])
        except Exception as e:
            client.chat_postMessage(channel=user_id, text=f"❌ Failed to read CSV: {e}")
            return
    elif text_input:
        # Comma-separated keywords input
        input_data = [kw.strip() for kw in text_input.split(",")]

    if not input_data:
        client.chat_postMessage(channel=user_id, text="❌ Please provide either a CSV URL or a list of keywords.")
        return

    # Run pipeline in a separate thread to avoid Slack timeout
    threading.Thread(target=background_task, args=(client, user_id, input_data)).start()

# -----------------------------
# Start Slack App with Socket Mode
# -----------------------------
if __name__ == "__main__":
    from slack_bolt.adapter.socket_mode import SocketModeHandler
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
