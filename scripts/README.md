# Book Text Data Builder

`build_book_data.py` converts a local plain-text novel into website-ready JSON.

## Commands

Inspect the source without writing output:

```bash
python3 scripts/build_book_data.py inspect \
  --input "book_text/《凡人修仙传》（校对版全本+番外）作者：忘语.txt"
```

Build structured data:

```bash
python3 scripts/build_book_data.py build \
  --input "book_text/《凡人修仙传》（校对版全本+番外）作者：忘语.txt" \
  --output book_data \
  --force
```

Validate generated data:

```bash
python3 scripts/build_book_data.py validate --output book_data
```

## Output Shape

- `book_data/book.json`: metadata, table of contents, volume/chapter manifest,
  source stats, and detected source anomalies.
- `book_data/volumes/vNNN.json`: per-volume chapter text stored as paragraphs.
- `book_data/inspection_report.json`: source format and line-accounting report.
- `book_data/validation_report.json`: generated data validation result.

Pages store paragraph index spans instead of duplicating text.
