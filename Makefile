.PHONY: build-test-container
build-test-container-env-toolkit:
	docker build -t env-toolkit-test -f tests/Dockerfile-env-toolkit.test .

.PHONY: test
test: test-env-toolkit

.PHONY: build-test-container-env-toolkit
test-env-toolkit: build-test-container-env-toolkit
	docker run -it --rm env-toolkit-test
