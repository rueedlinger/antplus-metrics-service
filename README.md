# antplus-metrics

This is a FastAPI and Vue application that provides:
- Display of ANT+ sensors (Power, Speed, Cadence, Heart Rate, Distance)
- Time and interval timer


## Requirements
- ANT+ USB adapter (eg. Tacx ANT+ Antenne, etc.)
- Pythopn
- Node

## Setup
tbd

## Test INstall Script with Docker
```bash
docker build --build-arg CACHE_BUST=$(date +%s) -t app:latest .
docker run -it --rm -p 8000:8000 app:latest bash
```

Then test the install script
```bash
./install.sh 
```

Or directly with

```bash
docker build --build-arg CACHE_BUST=$(date +%s) -t app:latest .
docker run -it --rm -p 8000:8000 app:latest /app/install
```


