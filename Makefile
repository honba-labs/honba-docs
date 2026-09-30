.PHONY: help bootstrap bootstrap-dev bootstrap-rust build build-mkdocs build-mdbook serve serve-mdbook clean distclean

help:
	@echo "make bootstrap        # venv + python deps"
	@echo "make bootstrap-dev    # + dev extras"
	@echo "make bootstrap-rust   # + cargo install mdbook tooling"
	@echo "make build            # build both sites"
	@echo "make build-mkdocs     # MkDocs only"
	@echo "make build-mdbook     # mdBook only"
	@echo "make serve            # mkdocs live-reload on :8000"
	@echo "make serve-mdbook     # serve built mdBook on :8001"
	@echo "make clean            # remove build artifacts"
	@echo "make distclean        # clean + remove .venv"

bootstrap:
	./scripts/bootstrap.sh

bootstrap-dev:
	./scripts/bootstrap.sh --dev

bootstrap-rust:
	./scripts/bootstrap.sh --rust

.PHONY:extract
extract:
	./script/extract.sh

build:
	./scripts/extract.sh
	./scripts/build.sh

build-mkdocs:
	./scripts/build.sh --mkdocs

build-mdbook:
	./scripts/build.sh --mdbook

serve:
	./scripts/serve.sh

serve-mdbook:
	./scripts/serve.sh --mdbook --port 8001

clean:
	./scripts/clean.sh

distclean:
	./scripts/clean.sh --all --venv
