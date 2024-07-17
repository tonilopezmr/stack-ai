## Setting up the Environment

**Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate 
    ```

**Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## How to run

```bash
uvicorn app.main:app --reload
```