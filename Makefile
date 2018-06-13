.PHONY: test build-test-container test-env-toolkit

test: test-env-toolkit

build-test-container-env-toolkit:
	docker build -t env-toolkit-test -f tests/Dockerfile-env-toolkit.test .

test-env-toolkit: build-test-container-env-toolkit
	docker run -it --rm env-toolkit-test
