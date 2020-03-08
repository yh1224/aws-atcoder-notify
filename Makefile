PUBLISH_S3_BUCKET := aws-sam-app-yh1224-ap-northeast-1
PUBLISH_S3_PREFIX := NotifyAtCoder

.PHONY: all
all: build

.PHONY: build
build:
	sam build --use-container

env.json: env.json.example
	test -e env.json || cp env.json.example env.json

.PHONY: local-invoke
local-invoke: build env.json
	sam local invoke --env-vars env.json

.PHONY: package
publish: build
	sam package --output-template-file packaged.yaml \
		--s3-bucket $(PUBLISH_S3_BUCKET) --s3-prefix $(PUBLISH_S3_PREFIX)
	sam publish --template packaged.yaml --region ap-northeast-1

.PHONY:
deploy: build
	sam deploy
