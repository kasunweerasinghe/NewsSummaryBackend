from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from newspaper import Article
import logging  # Added for better logging
from translate import Translator

from textblob import TextBlob

app = FastAPI()

origins = [
    "http://localhost:4200",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummaryRequest(BaseModel):
    url: str


class SummaryResponse(BaseModel):
    summary: str
    translated_summary: str 
    title: str
    author: str
    publication_date: str
    sentiment: dict


def translate_text(text, target_language, chunk_size=500):
    """
    Splits the text into chunks and translates them individually.

    Args:
        text (str): The text to translate.
        target_language (str): The target language for translation.
        chunk_size (int, optional): The maximum size of each text chunk. Defaults to 500.

    Returns:
        str: The translated text.
    """

    translator = Translator(to_lang=target_language)
    translated_chunks = []

    # Split the text into chunks
    for i in range(0, len(text), chunk_size):
        chunk = text[i:i + chunk_size]
        translated_chunk = translator.translate(chunk)
        translated_chunks.append(translated_chunk)

    # Combine the translated chunks and return the translated text
    return "".join(translated_chunks)


@app.post("/summarize", response_model=SummaryResponse)
async def summarize(request: Request):
    data = await request.json()
    url = data.get("url")
    target_language = data.get("target_language")

    print("Received URL:", url)
    print("Target language:", target_language)

    try:
        article = Article(url)
        article.download()
        article.parse()
        article.nlp()

        # Extract and format author and publication_date as strings
        author = article.authors[0]  # Assuming single author
        publication_date = article.publish_date.strftime("%Y-%m-%d")

        # Extract summary and title
        summary = article.summary
        translated_summary = translate_text(summary, target_language)
        title = article.title

        # Perform sentiment analysis
        analysis = TextBlob(article.text)
        sentiment = {
            'polarity': analysis.polarity,
            'sentiment': 'positive' if analysis.polarity > 0 else 'negative' if analysis.polarity < 0 else 'neutral'
        }

        return {
            'summary': summary,
            'translated_summary': translated_summary,
            'title': title,
            'author': author,
            'publication_date': publication_date,
            'sentiment': sentiment
        }

    except Exception as e:
        logging.error("Error processing article: %s", e)
        raise HTTPException(status_code=500, detail="Failed to process article. Please check the URL and try again.")
