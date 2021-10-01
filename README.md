# Farm Device

## Raspberry Pi Ubuntu 21.04 host setup

Add the required packages by running the following commands.

TODO: Add docker setup steps

```bash
sudo apt install i2c-tools
```

Add the following line to ```/boot/firmware/config.txt```

```dtoverlay=w1-gpio```
