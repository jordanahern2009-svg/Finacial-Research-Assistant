# SignalDesk - AI Financial Research Assistant

Hey, I'm Jordan. I'm a rising high school senior who is really interested in data science, finance, and the way AI can make complicated information easier to understand.

I built SignalDesk because I wanted to make a tool I would actually use while researching a company. Instead of jumping between a stock chart, financial statements, news articles, and an AI chat, SignalDesk puts those pieces together in one research workspace.

I'm hoping to study data science at Brown University, and this is one of the projects I'm using to learn by building. It is still growing, but it already gives me a place to practice working with real data, APIs, Python, visualizations, and responsible AI.

## What SignalDesk can do

- Search for a stock ticker such as AAPL or MSFT
- Pull recent price history, quote information, company details, and news
- Display income statements, balance sheets, and cash-flow statements
- Create interactive price and volume charts
- Generate an AI-assisted research brief using the current company data
- Answer questions about a company using the current research context
- Show the data timestamp and explain that the output is for education, not financial advice

## Why I built it

I wanted this project to be more than a pretty dashboard. I wanted to learn how a data product actually comes together:

1. Get data from an external provider.
2. Clean up inconsistent responses.
3. Turn the data into tables and visualizations that make sense.
4. Give an LLM enough context to be useful without letting it invent facts.
5. Build an interface that makes someone want to explore.

## Tech stack

Python · Streamlit · yfinance · pandas · Plotly · requests · NVIDIA NIM / GLM-5.2

## Run it locally

```powershell
git clone https://github.com/jordanahern2009-svg/Finacial-Research-Assistant.git
cd Finacial-Research-Assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

The market-data parts work without an LLM key. To turn on the AI research brief and company Q&A, add your key to `.env`:

```text
LLM_API_KEY=your-key-here
LLM_BASE_URL=https://integrate.api.nvidia.com/v1/chat/completions
LLM_MODEL=z-ai/glm-5.2
```

Never commit `.env`. It is already included in `.gitignore`.

## Project layout

```text
financial-research-assistant/
├── app.py                  # Streamlit interface
├── src/
│   ├── ai.py               # Grounded LLM prompts and API client
│   ├── charts.py           # Plotly chart builders
│   └── data.py             # Market-data access and normalization
├── tests/                  # Data transformation tests
├── .env.example
├── requirements.txt
└── README.md
```

## Deploy a demo

My goal is to keep localhost for development and have a public demo that people can click from my GitHub profile. Streamlit Community Cloud can deploy `app.py` directly from this repository.

1. Connect the repository at [share.streamlit.io](https://share.streamlit.io/).
2. Select the `main` branch and `app.py` as the entrypoint.
3. Add `LLM_API_KEY`, `LLM_BASE_URL`, and `LLM_MODEL` in the app's Secrets settings.
4. Do not upload or commit the local `.env` file.

## What I want to build next

- Add SEC EDGAR filings so important claims can be checked against primary sources.
- Add saved watchlists and research notes.
- Add tests that measure whether AI answers stay grounded in the supplied data.
- Add a comparison view for multiple companies.
- Build the companion algorithmic trading backtester with historical stock and crypto data.

## Responsible use

This is an educational project, not investment advice. Public market data may be delayed, incomplete, restated, or inaccurate. AI output can also be wrong, so important claims should be checked against company filings and other primary sources.
