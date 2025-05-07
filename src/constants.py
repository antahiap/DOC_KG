from pathlib import Path

PAPER_PDF_PATH = Path("../data/article_pdf")
PAPER_TXT_PATH = PAPER_PDF_PATH / "txt"
PAPER_IMG_PATH = PAPER_PDF_PATH / "img"
PAPER_GPT_PATH = PAPER_PDF_PATH / "papergpt"
PAPER_REF_PATH = PAPER_PDF_PATH / "ref"

OPEN_AI=False
OLLAMA=True

OLLAMA_URL = "localhost:11434/"
LLM_MODEL = "llama2"
ABBS_FILE = "../data/Abbreviations.docx"
ABBS_FILE_JSON = "../data/3FM_abbreviations.json"

EMBED_DIR = "../data/embed/"