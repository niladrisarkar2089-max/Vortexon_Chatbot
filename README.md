# Vortexon Chatbot
A Python-based AI chatbot with intelligent query routing between local LLM inference and real-time web search.

---

## Overview

Vortexon is a hybrid AI chatbot built entirely in Python. Upon receiving a user query, a dedicated judge model performs intent classification to determine whether the query can be resolved using the LLM's parametric knowledge or requires live web retrieval. If web search is triggered, the system fetches and synthesizes content from multiple external sources and returns a coherent, consolidated response. All retrieved sources are listed after each response, allowing the user to independently verify the accuracy of the output.

To open a retrieved source directly in the browser, use the command:

    open 1

Replace 1 with the index number of the desired source.

---

## Architecture
```text
                        [ User Query ]
                               |
                               v
                   [ Judge Model - gemma3:1b ]
                  ( Intent Classification - JSON )
                               |
              -----------------+-----------------
              |                                 |
      search_web: true                  search_web: false
              |                                 |
              v                                 v
   [ DuckDuckGo Search ]           [ Internal Knowledge ]
   ( Top 3 results via ddgs )
              |
              v
   [ Content Extraction ]
   ( title, url, body snippet )
              |
              v
   [ Prompt Assembly ]
   ( Sources + Query + System Time )
              |
              +---------------------------------+
                               |
                               v
                  [ Answer Model - gemma3:1b ]
                  ( Streaming Response via Ollama )
                               |
                               v
                      [ Response Output ]
                  ( Sources listed if web search )
                               |
                               v
                  [ Conversation History ]
                  ( Trimmed to last 3 turns )
```

---

## Installation and Setup

Step 1 — Install Python
Download and install Python 3.8 or higher with pip from the official source:
https://www.python.org/downloads/

Step 2 — Install Ollama
Ollama is required to run the LLM locally. Download and install it from:
https://ollama.com/download

Step 3 — Pull the Required Model
Run the following command in your terminal to download the model:

    ollama pull gemma3:1b

Step 4 — Start the Ollama Server
Ollama must be running as a local server before launching the chatbot:

    ollama serve

Step 5 — Install Python Dependencies
Refer to requirements.txt for the full list of packages and installation commands.

Step 6 — Run the Chatbot
Save the source code as a .py file and execute:

    python vortexon.py

---

## Performance Considerations

This chatbot runs inference locally using the Gemma 3 1B model via Ollama. No external API calls are made for the LLM. Performance is highly dependent on available hardware.

Without a dedicated GPU, inference runs entirely on the CPU:

- Older or budget-class CPU : approximately 3 to 8 tokens per second
- Modern CPU (Intel i5/i7, AMD Ryzen 5/7 or higher) : approximately 8 to 20 tokens per second

Each query invokes two sequential model calls — one for the judge and one for the answer — which increases total response latency compared to a single-call architecture.

---

## Limitations

- Gemma 3 1B is a lightweight 1 billion parameter model. Due to its limited capacity, it has a relatively higher tendency to produce hallucinated or inaccurate outputs. Users are advised to verify responses against the cited sources.
- Inference speed is significantly lower on CPU-only systems compared to GPU-accelerated hardware.
- Web search results are limited to the top 3 DuckDuckGo results per query.
