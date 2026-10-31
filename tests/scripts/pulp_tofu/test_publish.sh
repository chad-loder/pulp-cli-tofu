#!/bin/bash

set -eu

# shellcheck source=tests/scripts/config.source
. "$(dirname "$(dirname "$(realpath "$0")")")/config.source"

ENTITIES_NAME="test_tofu_publish"
NAMESPACE="clitest${RANDOM}"

cleanup() {
  pulp tofu namespace destroy --name "${NAMESPACE}" || true
  pulp tofu distribution destroy --name "${ENTITIES_NAME}" || true
  pulp tofu repository destroy --name "${ENTITIES_NAME}" || true
}
trap cleanup EXIT

python3 - <<'EOF'
import zipfile

for platform in ("linux_amd64", "darwin_arm64"):
    with zipfile.ZipFile(f"terraform-provider-demo_1.0.0_{platform}.zip", "w") as archive:
        archive.writestr("terraform-provider-demo_v1.0.0", f"demo for {platform}\n")
EOF
mkdir vpc
printf 'variable "cidr" {}\n' > vpc/main.tf
tar -czf vpc.tar.gz -C vpc .

expect_succ pulp tofu repository create --name "${ENTITIES_NAME}"
expect_succ pulp tofu distribution create --name "${ENTITIES_NAME}" \
  --base-path "${ENTITIES_NAME}" --repository "${ENTITIES_NAME}"
expect_succ pulp tofu namespace create --name "${NAMESPACE}" --distribution "${ENTITIES_NAME}" \
  --private
NAMESPACE_HREF="$(echo "$OUTPUT" | jq -r .pulp_href)"

expect_fail pulp tofu namespace publish-module --name "${NAMESPACE}" \
  --module vpc --system aws --version 1.0.0 vpc.tar.gz
[[ "$ERROUTPUT" == *"does not accept uploads"* ]]
expect_succ pulp tofu distribution update --name "${ENTITIES_NAME}" --allow-uploads

expect_succ pulp tofu namespace publish-module --name "${NAMESPACE}" \
  --module vpc --system aws --version 1.0.0 vpc.tar.gz
expect_succ pulp tofu content -t module_version list --namespace "${NAMESPACE}"
[[ "$(echo "$OUTPUT" | jq -r '.[0].name')" == "vpc" ]]

expect_succ pulp tofu namespace role add --name "${NAMESPACE}" \
  --role tofu.tofunamespace_consumer --user admin
expect_succ pulp tofu namespace role remove --name "${NAMESPACE}" \
  --role tofu.tofunamespace_consumer --user admin

expect_succ pulp tofu token create --name "${ENTITIES_NAME}" --namespace "${NAMESPACE_HREF}" \
  --scope publish --expires-at 2099-01-01T00:00:00Z
TOKEN_HREF="$(echo "$OUTPUT" | jq -r .pulp_href)"
[[ "$(echo "$OUTPUT" | jq -r .token)" != "null" ]]
[[ "$(echo "$OUTPUT" | jq -r .expires_at)" == "2099-01-01T00:00:00Z" ]]
expect_succ pulp tofu token show --href "${TOKEN_HREF}"
[[ "$(echo "$OUTPUT" | jq -r .token)" == "null" ]]
expect_succ pulp tofu token destroy --href "${TOKEN_HREF}"

expect_fail pulp tofu namespace publish --name "${NAMESPACE}" terraform-provider-demo_1.0.0_*.zip
[[ "$ERROUTPUT" == *"no signing service"* ]]

# Unsigned releases need a tofu signing service on the server; exit 23 skips the rest.
pulp signing-service show --name "${TOFU_SIGNING_SERVICE:-tofu-e2e}" >signing.json 2>/dev/null || exit 23
expect_succ pulp tofu namespace update --name "${NAMESPACE}" \
  --signing-service "$(jq -r .pulp_href signing.json)"

expect_succ pulp tofu namespace publish --name "${NAMESPACE}" terraform-provider-demo_1.0.0_*.zip
expect_succ pulp tofu content list --namespace "${NAMESPACE}"
[[ "$(echo "$OUTPUT" | jq -r '.[0].version')" == "1.0.0" ]]
expect_succ pulp tofu content -t provider_package list --namespace "${NAMESPACE}"
[[ "$(echo "$OUTPUT" | jq length)" == "2" ]]

expect_fail pulp tofu namespace publish --name "${NAMESPACE}" vpc.tar.gz
