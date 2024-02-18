#!/usr/bin/env bash

docker exec -i stringwave-test bash -c "pytest -q tests"
