#!/bin/bash

set -eu

# shellcheck source=tests/scripts/config.source
. "$(dirname "$(dirname "$(realpath "$0")")")/config.source"

ENTITIES_NAME="test_tofu_remote"

cleanup() {
  pulp tofu remote destroy --name "${ENTITIES_NAME}" || true
}
trap cleanup EXIT

expect_fail pulp tofu remote create --name "${ENTITIES_NAME}"

expect_succ pulp tofu remote create --name "${ENTITIES_NAME}" --url "$TOFU_REGISTRY_URL" \
  --include "registry.opentofu.org/hashicorp/*" --metadata-ttl 600
[[ "$(echo "$OUTPUT" | jq -r .policy)" == "streamed" ]]
[[ "$(echo "$OUTPUT" | jq -r '.includes[0]')" == "registry.opentofu.org/hashicorp/*" ]]

expect_succ pulp tofu remote update --name "${ENTITIES_NAME}" --exclude "*/hashicorp/aws" \
  --require-signatures
expect_succ pulp tofu remote show --name "${ENTITIES_NAME}"
[[ "$(echo "$OUTPUT" | jq -r '.excludes[0]')" == "*/hashicorp/aws" ]]
[[ "$(echo "$OUTPUT" | jq -r .require_signatures)" == "true" ]]

expect_succ pulp tofu remote list --limit 1000
[[ "$(echo "$OUTPUT" | jq --arg n "${ENTITIES_NAME}" '[.[] | select(.name == $n)] | length')" == "1" ]]

expect_succ pulp tofu remote destroy --name "${ENTITIES_NAME}"
