# ResearchAssistant

We aim to advance the Auto-research framework by developing a comprehensive Research Writing Assistant that streamlines the scientific research process. This system supports literature retrieval, gap analysis, idea brainstorming, summarization, passage generation, and proofreading, enhancing productivity without replacing human authorship.

Users input a research prompt and upload relevant documents, while an advanced LLM curates state-of-the-art literature and performs gap analysis to pinpoint novel research directions. The system then synthesizes bullet points, summaries, and visualizations to generate an initial LaTeX draft, which is further refined for enhanced clarity, persuasiveness, and compliance with publication formats.

## Clone the repository

```bash
git clone https://github.com/arowayasmeen/ResearchAssistant.git
```

## Create a virtual environment

```bash
conda create -n researchassistant python=3.12
conda activate researchassistant
```

```bash
python -m venv venv
venv\Scripts\activate
```

## Set up dependencies

```bash
pip install -r requirements.txt
```

## Create a .env file with your API keys

```env
SERPAPI_KEY=your_serpapi_key_here
```

You can get a SerpAPI key by signing up at [serpapi.com](https://serpapi.com).

## (Optional) Install the Research-Assistant package in development mode if you want to edit
```bash
pip install -e .
```

## Running the application

1. Start the backend API server:

```bash
python run.py
```

2. Open the UI in your broswer:

Open <code>ui/index.html</code> in your web browser to use the application.