scrape:
	uv run --directory src python -m main

reply url:
	uv run --directory src python -m reply {{url}}

info url:
	uv run --directory src python vacancy_info.py {{url}}

auth:
	uv run --directory src python -m hh.auth

scrape-all:
	uv run --directory src python -m hh.browser_parser 4e8c8ee5ff10b35db40039ed1f6d5634587052

pop:
	uv run --directory src python pop_vacancy.py

skip id-or-url:
	uv run --directory src python skip_vacancy.py {{id-or-url}}
