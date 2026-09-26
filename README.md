# Multi-Agent Customer Support (AutoGen + Streamlit)

Three AutoGen agents run in sequence using `RoundRobinGroupChat`:

1. **Assistant** – answers from its own knowledge
2. **Web_Search_Assistant** – searches the web (Serper) and answers
3. **Entry_Agent** – saves the query and both answers to `answers.txt`

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```
OPENAI_API_KEY=your-key
SERPER_API_KEY=your-key
```

## Run

```bash
streamlit run app.py
```