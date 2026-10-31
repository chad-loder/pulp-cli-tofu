# pulp-cli-tofu

[pulp-cli](https://github.com/pulp/pulp-cli) commands for
[pulp_tofu](https://github.com/chad-loder/pulp_tofu): OpenTofu provider mirrors, registry
namespaces, published providers and modules, and registry tokens.

```bash
pip install pulp-cli-tofu

pulp tofu remote create --name opentofu --url https://registry.opentofu.org/
pulp tofu repository create --name providers --remote opentofu
pulp tofu repository sync --name providers --provider hashicorp/aws --latest 2
pulp tofu distribution create --name providers --base-path providers --repository providers

pulp tofu namespace create --name acme --distribution acme
pulp tofu namespace publish --name acme dist/terraform-provider-widget_1.2.0_*
pulp tofu namespace publish-module --name acme --module vpc --system aws --version 1.0.0 vpc.tar.gz
pulp tofu token create --name laptop --namespace <namespace href>
```

`pulp-glue-tofu` is the version-agnostic library the commands are built on.
