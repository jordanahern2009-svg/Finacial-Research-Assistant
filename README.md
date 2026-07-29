# SignalDesk — Financial Research Assistant

SignalDesk is a portfolio project built by an upcoming high school senior who is exploring data science, financial research, and responsible AI. Search a ticker and explore market data, price history, financial statements, company news, charts, an AI-generated research brief, and company Q&A.

## Why this project belongs on a data science portfolio

This project turns messy public data into a repeatable research workflow:

- **Data ingestion:** price history, company metadata, statements, and news
- **Data transformation:** normalized provider responses and display-ready tables
- **Visualization:** interactive Plotly price and volume charts
- **Applied AI:** grounded summaries and Q&A using only the current research context
- **Product thinking:** clear uncertainty, refresh timestamps, and a financial-data disclaimer

## Tech stack

Python · Streamlit · yfinance · pandas · Plotly · requests · an OpenAI-compatible LLM API

## Run locally

```powershell
cd financial-research-assistant
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

For development and tests, install the optional test dependency too:

```powershell
pip install -r requirements-dev.txt
pytest -q
```

The app works without an LLM key. To enable the research brief and Q&A, put an API key in `.env`:

```text
LLM_API_KEY=your-key-here
LLM_BASE_URL=https://integrate.api.nvidia.com/v1/chat/completions
LLM_MODEL=z-ai/glm-5.2
```

`LLM_BASE_URL` is intentionally configurable so the project can work with any provider that supports the common chat-completions request format.

## Deploy a public demo

Keep localhost for development, then deploy the portfolio demo with [Streamlit Community Cloud](https://streamlit.io/cloud):

1. Push this repository to GitHub.
2. Connect GitHub at [share.streamlit.io](https://share.streamlit.io/).
3. Create an app using `app.py` as the entrypoint and `main` as the branch.
4. In Advanced settings, add these secrets without committing `.env`:

```text
LLM_API_KEY = "your-nvidia-key"
LLM_BASE_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
LLM_MODEL = "z-ai/glm-5.2"
```

After deployment, add the public `streamlit.app` URL to the top of this README and your GitHub profile README. Keep the API key in the platform's secrets settings only.

## Project structure

```text
financial-research-assistant/
├── app.py              # Streamlit user interface
├── src/
│   ├── ai.py            # LLM adapter and grounded prompts
│   ├── charts.py        # Plotly chart builders
│   └── data.py          # Provider access and normalization
├── tests/               # Small unit tests for data transformations
├── .env.example
├── requirements.txt
└── README.md
```

## Responsible-use notes

This is an educational research tool, not an investment adviser. Public market data may be delayed, incomplete, restated, or inaccurate. AI output can be wrong, so important claims should be checked against primary company filings and official sources.

## Next milestones

1. Add SEC EDGAR company facts and filing links as a primary-source layer.
2. Add a watchlist and saved research notes.
3. Add an evaluation set for testing whether AI answers stay grounded in the supplied data.
4. Deploy a public demo with secrets stored outside the repository.
5. Build the companion algorithmic trading backtester with reusable analytics modules.
