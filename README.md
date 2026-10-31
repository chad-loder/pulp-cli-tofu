# pulp-cli-tofu

[pulp-cli](https://github.com/pulp/pulp-cli) commands for
[pulp_tofu](https://github.com/chad-loder/pulp_tofu): OpenTofu provider mirrors, registry
namespaces, published providers and modules, and registry tokens.

> **Beta.** Like pulp_tofu, this is developed outside the Pulp Project. Neither package is
> on PyPI yet; install both from git. The Pulp server needs the
> [pulp_tofu plugin](https://chad-loder.github.io/pulp_tofu/).

```bash
pip install \
  "pulp-glue-tofu @ git+https://github.com/chad-loder/pulp-cli-tofu#subdirectory=pulp-glue-tofu" \
  "pulp-cli-tofu @ git+https://github.com/chad-loder/pulp-cli-tofu"

pulp tofu remote create --name opentofu --url https://registry.opentofu.org/
pulp tofu repository create --name providers --remote opentofu
pulp tofu repository sync --name providers --provider hashicorp/aws --latest 2
pulp tofu distribution create --name providers --base-path providers --repository providers

pulp tofu namespace create --name acme --distribution acme
pulp tofu namespace publish --name acme dist/terraform-provider-widget_1.2.0_*
pulp tofu namespace publish-module --name acme --module vpc --system aws --version 1.0.0 vpc.tar.gz
pulp tofu token create --name laptop --namespace <namespace href>
```

To drive pulp_tofu from Python instead of the shell, use `pulp-glue-tofu`, the library
these commands call.
