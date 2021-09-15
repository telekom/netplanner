# mimir

## How to use it

```console
# This is a developer command --local ensures that ./ is set on the output.
$ mimir --local --config examples/worker-config-old.yaml --output /run/systemd/network --only-networkd configure

$ mimir --help
usage: mimir [-h] [--config CONFIG] [--local] [--only-sriov] [--only-networkd] [--output OUTPUT] {configure} ...

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Defines the path to the configuration file
  --local          This templates the configuration into a local directory
  --only-sriov     This only runs sriov configuration
  --only-networkd  This templates only networkd
  --output OUTPUT  The output directory to which the files will be written.

subcommands:
  valid subcommands

  {configure}      sub-command help
    configure      Configure Network Adapters flawlessly with the knowledge of mimir.
```

## Have a look at the examples dir

Inside the examples you find different configuration examples for different type of configurations.

Currently for bond-type configuration only the active-backup is supported.
For the vxlan configuration active-active is supported.
Also it is not completely compliant with netplan because a lot of configurations are not supported regarding dhcp.
The implementation relies on a static imperative top-down approach you normally find in a datacenter.