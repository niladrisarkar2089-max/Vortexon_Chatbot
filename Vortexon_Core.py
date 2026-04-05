#!/usr/bin/env python3
"""
Vortexon AI - THE PERFECT MERGE
 Dynamic Routing → Memory → Streaming → Silent Time Context → Seamless Synthesis
"""

import requests
import webbrowser
import json
import re
import sys
from datetime import datetime
from ddgs import DDGS

class OllamaModel:
    def __init__(self, model_name, system_instruction="", is_json=False):
        self.model_name = model_name
        self.system_instruction = system_instruction
        self.is_json = is_json

    def generate(self, prompt, history=None, stream=False):
        messages = []
        if self.system_instruction:
            messages.append({"role": "system", "content": self.system_instruction})
        
        if history:
            messages.extend(history)
            
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": stream,
            "options": {"temperature": 0.0 if self.is_json else 0.4}
        }
        
        if self.is_json:
            payload["format"] = "json"

        try:
            response = requests.post("http://localhost:11434/api/chat", json=payload, stream=stream, timeout=30)
            response.raise_for_status()
            
            if stream:
                return response
            else:
                return response.json().get("message", {}).get("content", "")
                
        except Exception as e:
            if stream:
                print(f"\n Connection Error: {e}")
                sys.exit(1)
            return f'{{"error": "{e}"}}'

class UltraCleanAI:
    def __init__(self):
        self.chat_history = []
        self.sources = [] 
        
        self.judge_model = OllamaModel(
            "gemma3:1b",
            system_instruction='Analyze the user query. If it requires recent information, news, weather, live sports, current prices, or specific real-time facts, return {"search_web": true}. If it relies on general knowledge, history, coding, math, creative writing, or casual conversation, return {"search_web": false}. Return strictly valid JSON.',
            is_json=True
        )

    
        self.answer_model = OllamaModel(
            "gemma3:1b",
            system_instruction="You are Vortexon, a highly intelligent and friendly AI assistant. Answer the user clearly, naturally, and with high quality. Do NOT use inline citations like [1] or [2]. Do NOT arbitrarily state the date unless the user explicitly asks for time-sensitive information."
        )

    def silent_decision(self, query):
        """ AI Judge decides if we need the internet"""
        try:
            resp_text = self.judge_model.generate(query)
            json_match = re.search(r'\{.*?\}', resp_text, re.DOTALL)
            
            if json_match:
                decision = json.loads(json_match.group())
                val = decision.get("search_web", False)
                if isinstance(val, str):
                    return val.lower().strip() == "true"
                return bool(val)
        except Exception:
            pass
        return any(kw in query.lower() for kw in ['today','weather','news','current','score','live','latest'])

    def web_search(self, query):
        print(f"\nSearching the Web")
        self.sources = []
        
        try:
            results = DDGS().text(query, max_results=3)
            if results:
                for res in results:
                    title = res.get('title', 'No Title')
                    url = res.get('href', '')
                    content = res.get('body', '')
                    
                    if url and content:
                        self.sources.append({
                            'title': title, 
                            'url': url, 
                            'content': content
                        })
        except Exception as e:
            print(f" Search fetching failed: {e}")
            return

        self.show_sources()
    
    def show_sources(self):
        if not self.sources:
            print(" No readable text extracted from websites.")
            return
            
        print("\n SOURCES:")
        print("=" * 60)
        for i, s in enumerate(self.sources, 1):
            print(f"[{i}] {s['title']}")
            print(f"   {s['url']}")
            preview = s['content'][:120] + "..." if len(s['content']) > 120 else s['content']
            print(f"   📄 {preview}")
            print()
        print(" 'open 1' to visit\n")

    def chat(self, user_query):
        """ Manages the flow of conversation"""
        
        needs_search = self.silent_decision(user_query)
        if needs_search:
            self.web_search(user_query)
        else:
            print(f"\n[  Using internal knowledge... ]\n")
            self.sources = [] 

        current_time = datetime.now().strftime("%A, %B %d, %Y")

        
        if self.sources:
            context_blocks = []
            for s in self.sources:
                
                context_blocks.append(f"Source Title: {s['title']}\nContent: {s['content']}")
            
            context_str = "\n\n".join(context_blocks)
            
            prompt = f"""[Hidden System Time: {current_time}]

WEB SOURCES:
{context_str}

USER QUESTION: {user_query}

INSTRUCTIONS:
1. Read the WEB SOURCES carefully to gather facts.
2. Synthesize the facts into a highly refined, accurate, and natural-sounding answer.
3. DO NOT use citation markers like [1], [2], etc. in the text. Weave the information seamlessly.
4. DO NOT write an 'Analysis' section or list out the sources one by one. 
5. DO NOT state the current date in your answer unless it is directly required to make sense of the user's question."""

        else:
            
            prompt = f"[Hidden System Time: {current_time}]\n\nUser Question: {user_query}\n\nAnswer the user naturally and comprehensively based on your internal knowledge. Do not state the current date unless specifically relevant."

        print("🤖 Vortexon: ", end="", flush=True)
        full_response = ""
        
        response_stream = self.answer_model.generate(prompt, history=self.chat_history, stream=True)
        
        for line in response_stream.iter_lines():
            if line:
                chunk = json.loads(line)
                text_chunk = chunk.get("message", {}).get("content", "")
                print(text_chunk, end="", flush=True)
                full_response += text_chunk
                
        print("\n\n" + "="*60 + "\n")

        self.chat_history.append({"role": "user", "content": user_query})
        self.chat_history.append({"role": "assistant", "content": full_response})
        
        if len(self.chat_history) > 6:
            self.chat_history = self.chat_history[-6:]

def main():
    ai = UltraCleanAI()
    print("\n" + "="*60)
    print(" Vortexon Chatbot")
    print("="*60 + "\n")
    
    while True:
        try:
            query = input("You > ").strip()
            if not query: 
                continue
                
            if query.lower().startswith('open '):
                try:
                    num = int(query.split()[1]) - 1
                    if 0 <= num < len(ai.sources):
                        webbrowser.open_new_tab(ai.sources[num]['url'])
                        print(" Opened in browser!")
                    else:
                        print(" No source available at that number.")
                except:
                    print(" Try formatting like: 'open 1'")
                continue
            
            if query.lower() in ['bye', 'quit', 'exit', 'clear']:
                print(" Catch you later!")
                break
            
            ai.chat(query)
            
        except KeyboardInterrupt:
            print("\n Exiting...")
            sys.exit(0)

if __name__ == "__main__":
    main()
