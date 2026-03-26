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
	touch "content/posts/$$slug.md"; \
	echo "# $$slug" > "content/posts/$$slug.md"; \
	$${EDITOR:-vim} "content/posts/$$slug.md"
