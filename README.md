\# Multi-Agent Customer Support (AutoGen + Streamlit)



Three AutoGen agents run in sequence (RoundRobinGroupChat):

1\. \*\*Assistant\*\* – answers from its own knowledge

2\. \*\*Web\_Search\_Assistant\*\* – searches the web (Serper) and answers

3\. \*\*Entry\_Agent\*\* – saves the query + both answers to answers.txt



\## Setup

pip install -r requirements.txt

Create a `.env` file:

OPENAI\_API\_KEY=your-key

SERPER\_API\_KEY=your-key



\## Run

streamlit run app.py

