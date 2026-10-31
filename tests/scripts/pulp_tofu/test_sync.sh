#!/bin/bash

set -eu

# shellcheck source=tests/scripts/config.source
. "$(dirname "$(dirname "$(realpath "$0")")")/config.source"

ENTITIES_NAME="test_tofu_sync"

cleanup() {
  pulp tofu distribution destroy --name "${ENTITIES_NAME}" || true
  pulp tofu repository destroy --name "${ENTITIES_NAME}" || true
  pulp tofu remote destroy --name "${ENTITIES_NAME}" || true
}
trap cleanup EXIT

expect_succ pulp tofu remote create --name "${ENTITIES_NAME}" --url "$TOFU_REGISTRY_URL" \
  --policy on_demand
expect_succ pulp tofu repository create --name "${ENTITIES_NAME}" --remote "${ENTITIES_NAME}"

expect_fail pulp tofu repository sync --name "${ENTITIES_NAME}" --provider "hashicorp"
expect_succ pulp tofu repository sync --name "${ENTITIES_NAME}" \
  --provider "hashicorp/null@3.2.4" --platform linux_amd64

expect_succ pulp tofu repository version show --repository "${ENTITIES_NAME}" --version 1
expect_succ pulp tofu content list --namespace hashicorp --version 3.2.4
[[ "$(echo "$OUTPUT" | jq -r '.[0].provider_type')" == "null" ]]

expect_succ pulp tofu distribution create --name "${ENTITIES_NAME}" \
  --base-path "${ENTITIES_NAME}" --repository "${ENTITIES_NAME}"
[[ "$(echo "$OUTPUT" | jq -r .base_url)" == http* ]]
