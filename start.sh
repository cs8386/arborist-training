#!/bin/sh
set -e
echo "Testing import..."
python -c "
import sys
try:
    import app.main
    print('Import OK')
except Exception as e:
    import traceback
    traceback.print_exc()
    sys.exit(1)
"
echo "Starting server on port $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
