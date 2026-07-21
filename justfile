scrape:
	uv run --directory src python -m main

reply url:
	uv run --directory src python -m reply {{url}}

auth:
	uv run --directory src python -m hh.auth

scrape-relevant:
	uv run --directory src python -m hh.browser_parser 4e8c8ee5ff10b35db40039ed1f6d5634587052
