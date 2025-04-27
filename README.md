# Resume Selection API

This project provides an API for selecting the best-matching resumes for a given job description. It is designed for easy integration and automation of resume screening tasks.

---

## 🚀 Running the App

Make sure you have Python 3.8+ and install dependencies:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Start the server with:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

---

## 🔑 Environment Variables

Create a `.env` file in the project root with any required API keys or configuration. Example:

```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 📦 Sample API Request

You can use the `/process-resume` endpoint to process a candidate's resume (PDF or DOCX) and receive an evaluation. Example using `curl`:

```bash
curl -X POST "http://localhost:8000/process-resume" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/resume.pdf"
```

**Sample Response:**
```json
{
  "experience_level": "Senior-level",
  "skill_match": "Match",
  "response": "Candidate has been shortlisted for an HR interview."
}
```

---

## ⚙️ Configuration

- Edit `main.py` to adjust scoring, input/output, or model integration as needed.
- Requirements are listed in `requirements.txt`.

---

## 📁 Project Structure

- `main.py` - Main script for running resume selection logic
- `job_description.txt` - Place your job description here
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (API keys, etc)

---

## 📝 Example

```
python main.py
# Output:
# Top 3 matching resumes:
# 1. John_Doe.pdf
# 2. Jane_Smith.pdf
# 3. ...
```

---

## 🆘 Troubleshooting

- Ensure your Python version is compatible (3.8+ recommended)
- Check `.env` for required API keys
- Review `requirements.txt` for missing packages

---

## 📬 Contact

For questions or issues, please open an issue or contact the maintainer.
