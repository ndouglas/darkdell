.PHONY: build serve deploy new

build:
	python build.py

serve: build
	python -m http.server -d public 8000

deploy: build
	aws s3 sync public/ s3://darkdell.www --delete
	aws cloudfront create-invalidation --distribution-id ERL3QRNQL3Q5K --paths "/*"

new:
	@read -p "Post slug: " slug; \
	dir="content/posts/$$(date +%Y)/$$(date +%m)"; \
	mkdir -p "$$dir"; \
	file="$$dir/$$(date +%d)-$$slug.md"; \
	echo "# $$slug" > "$$file"; \
	$${EDITOR:-vim} "$$file"
