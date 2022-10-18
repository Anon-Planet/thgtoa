all: guide

guide: clean
	./script/make.sh

.phony: serve
serve: # This gets all gems and installs bundler.
       # Serves the guide locally using Jekyll. 🍽️
	@echo "Serving site..."
	./script/serve.sh

clean: # Clean artifacts. 🧹
	@echo "Cleaning..."
	./script/clean.sh

