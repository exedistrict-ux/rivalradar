import os
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types
from bs4 import BeautifulSoup

load_dotenv()

BRIGHT_DATA_API_KEY = os.getenv("BRIGHT_DATA_API_KEY")
SERP_ZONE          = os.getenv("SERP_ZONE")
SCRAPING_ZONE      = os.getenv("SCRAPING_ZONE")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)

BRIGHT_DATA_ENDPOINT = "https://api.brightdata.com/request"
BD_HEADERS = {
    "Authorization": f"Bearer {BRIGHT_DATA_API_KEY}",
    "Content-Type": "application/json",
}

SYSTEM_PROMPT = """You are RivalRadar, an elite competitor intelligence agent.
When given a company name, research their TOP 3-5 competitors deeply using live web data.

STRATEGY:
1. First search for competitors list
2. For each competitor: search their pricing, news, hiring
3. Scrape actual pages when you need deeper info (pricing pages, news articles, LinkedIn jobs)
4. Compile everything into a structured report

For each competitor gather:
- Company overview & business model
- Pricing information (actual numbers if possible)
- Recent news & funding rounds
- Hiring signals (growing or shrinking?)
- Key strengths & weaknesses

Produce a detailed structured markdown report with clear sections per competitor."""


def search_web(query: str) -> str:
    try:
        search_url = f"https://www.google.com/search?q={requests.utils.quote(query)}"
        payload = {"zone": SERP_ZONE, "url": search_url, "format": "raw"}
        resp = requests.post(BRIGHT_DATA_ENDPOINT, headers=BD_HEADERS, json=payload, timeout=30)
        body = resp.json()
        organic = body.get("organic", [])
        if not organic:
            return f"No results found for: {query}"
        results = []
        for r in organic[:5]:
            link  = r.get("link") or r.get("href") or r.get("url") or "N/A"
            title = r.get("title") or "No title"
            desc  = r.get("description") or r.get("snippet") or ""
            results.append(f"{title}: {link}\n{desc}")
        return "\n\n".join(results)
    except Exception as e:
        return f"Search error: {str(e)}"


def scrape_page(url: str) -> str:
    try:
        payload = {"zone": SCRAPING_ZONE, "url": url, "format": "raw"}
        resp = requests.post(BRIGHT_DATA_ENDPOINT, headers=BD_HEADERS, json=payload, timeout=60)
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe"]):
            tag.decompose()
        text  = soup.get_text(separator="\n", strip=True)
        lines = [l.strip() for l in text.splitlines() if l.strip()]
        clean = "\n".join(lines)
        if len(clean) > 3000:
            clean = clean[:3000] + "\n...[truncated]"
        return clean if clean else "No readable content found."
    except Exception as e:
        return f"Scrape error: {str(e)}"


TOOLS = [
    types.Tool(function_declarations=[
        types.FunctionDeclaration(
            name="search_web",
            description="Search Google for competitor intelligence, pricing, news, hiring signals",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(type=types.Type.STRING, description="Search query")
                },
                required=["query"]
            )
        ),
        types.FunctionDeclaration(
            name="scrape_page",
            description="Scrape full content of any webpage — pricing pages, news articles, LinkedIn jobs",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "url": types.Schema(type=types.Type.STRING, description="Full URL to scrape")
                },
                required=["url"]
            )
        ),
    ])
]

TOOL_MAP = {
    "search_web": search_web,
    "scrape_page": scrape_page,
}


def run_agent_stream(company: str):
    yield {"type": "thinking", "text": f'Starting deep research on "{company}"...'}

    contents = [
        types.Content(
            role="user",
            parts=[types.Part(text=(
                f"Research the top competitors of: {company}. "
                "Use search_web to find competitors, pricing, news, hiring signals. "
                "Use scrape_page to get deeper data from relevant URLs. "
                "Give me a full competitive intelligence report."
            ))]
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        tools=TOOLS,
        max_output_tokens=8192,
    )

    iteration = 0
    max_iterations = 20

    while iteration < max_iterations:
        iteration += 1

        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=contents,
                config=config,
            )
        except Exception as e:
            yield {"type": "report", "content": f"API Error: {str(e)}"}
            yield {"type": "complete"}
            return

        # Safety: check candidate exists
        if not response.candidates:
            yield {"type": "report", "content": "No response from Gemini API."}
            yield {"type": "complete"}
            return

        candidate = response.candidates[0]

        # Safety: content or parts could be None
        if not candidate.content or not candidate.content.parts:
            # Try to get text from response.text directly
            try:
                text = response.text
                if text:
                    yield {"type": "report", "content": text}
            except Exception:
                pass
            yield {"type": "complete"}
            return

        # Append model response to history
        contents.append(types.Content(role="model", parts=candidate.content.parts))

        has_tool_call = False
        tool_results = []

        for part in candidate.content.parts:
            if part.function_call:
                has_tool_call = True
                func_name = part.function_call.name
                func_args = dict(part.function_call.args)

                if func_name == "search_web":
                    yield {"type": "search", "query": func_args.get("query", "")}
                elif func_name == "scrape_page":
                    yield {"type": "scrape", "url": func_args.get("url", "")}

                result = TOOL_MAP.get(func_name, lambda **k: "Unknown tool")(**func_args)

                tool_results.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=func_name,
                            response={"result": result}
                        )
                    )
                )

        if has_tool_call:
            contents.append(types.Content(role="user", parts=tool_results))
            continue

        # No tool calls — final text response
        final_text = "".join(
            p.text for p in candidate.content.parts
            if hasattr(p, "text") and p.text
        )
        if final_text:
            yield {"type": "report", "content": final_text}
        yield {"type": "complete"}
        return

    yield {"type": "complete"}


if __name__ == "__main__":
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "Zomato"
    for event in run_agent_stream(company):
        print(event)
