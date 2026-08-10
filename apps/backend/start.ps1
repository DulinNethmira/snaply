$env:PYTHONPATH = (Get-Item -Path ".\").FullName

# Start uvicorn with strict memory and process constraints for a 512MB VPS
.\venv\Scripts\uvicorn.exe app.main:app `
    --host 0.0.0.0 `
    --port 8000 `
    --workers 1 `
    --limit-max-requests 10000 `
    --timeout-keep-alive 5 `
    --log-level info
