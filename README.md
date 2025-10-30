# documentacion-PagoPar-Py

Este repositorio consolida la documentación pública del centro de ayuda de PagoPar y provee un entorno de pruebas local.

## Contenido principal

- `docs/programmers-guide.md`: guía resumida para desarrolladores con los flujos, tokens y endpoints más importantes.
- `docs/source/articles/`: copias en Markdown de cada artículo descargado automáticamente.
- `data/pagopar_articles.json`: volcado estructurado de los artículos (título, resumen, contenido HTML, Markdown y texto plano).
- `mock_server/`: API simulada construida con FastAPI que reproduce los endpoints clave de la documentación.
- `scripts/fetch_pagopar_docs.py`: script que descarga los artículos desde soporte.pagopar.com y genera los artefactos anteriores.

## Cómo actualizar la documentación

```bash
python scripts/fetch_pagopar_docs.py
```

## Cómo ejecutar el mock

```bash
cd mock_server
pip install -r requirements.txt
uvicorn mock_server.app:app --reload
```

Luego accede a `http://127.0.0.1:8000/docs` para interactuar con el mock mediante la interfaz automática de FastAPI.
