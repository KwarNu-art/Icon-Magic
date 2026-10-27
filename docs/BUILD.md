# Build

## Requirements

- Python 3.10+  
- Pillow  

```bash
pip install -r requirements.txt
python3 tools/render_icons.py
python3 tests/test_theme.py
python3 tools/build_packages.py
```

## Outputs

- `theme/*.theme/IconBundles/*-large.png`  
- `assets/svg/**`  
- `assets/previews/contact-*.png`  
- `packaging/dist/*.deb`  

## CI

See `.github/workflows/ci.yml` and `release.yml`.
