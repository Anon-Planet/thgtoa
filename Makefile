all: guide

guide: clean
	./script/make

.phony: serve
serve: # This gets all gems and installs bundler.
       # Serves the guide locally using Jekyll. 🍽️
	@echo "Serving site..."
	./script/serve

clean: # Clean artifacts. 🧹
	@echo "Cleaning..."
	./script/clean

