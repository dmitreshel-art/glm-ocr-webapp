# Model Configuration

The default model is GLM-OCR Q8_0 (~950 MB). You can switch to F16 (~1.9 GB) for better OCR quality.

## Option 1: Environment Variable (Recommended)

```powershell
# Q8_0 (default, ~95-98% accuracy)
docker-compose up -d

# F16 (better accuracy, ~98-99%)
$env:MODEL_VARIANT="F16"
docker-compose up -d
```

## Option 2: Edit config.yaml

```yaml
model:
  variant: F16  # Q8_0 or F16
  ctx_size: 16384
  ngl: 99
```

Then restart:

```powershell
docker-compose down
docker-compose up -d
```

## Option 3: .env file

Create `.env` file:

```
MODEL_VARIANT=F16
```

Then:

```powershell
docker-compose up -d
```

## Model Variants Comparison

| Variant | Size | RAM Required | Accuracy | Best For |
|---------|------|---------------|----------|----------|
| Q8_0 | ~950 MB | ~2 GB | 95-98% | Standard documents |
| F16 | ~1.9 GB | ~4 GB | 98-99% | Handwriting, low quality |

## Notes

- First start downloads the model (~1-2 GB download)
- F16 uses ~2x more RAM but provides better OCR on difficult documents
- Both variants support the same context size (16384 tokens)