# TrafficUI
A web-UI for assigning labels to existing flows.

## Configuration
Copy the `config-example.ini` to `config.ini` and configure it for your needs.

## Starting
### Nix/NixOS
The `shell.nix`-file knows what to do. Just let [nix][] do the work for you.

```bash
$ nix-shell
[nix-shell]$ ./traffic_ui.py
```

### Other systems
Install the *Python Libraries* listed below with your favorite tools and start
`traffic_up.py`.

## Dependencies
### Python Libraries

- [Bottle][bottle] (MIT license)
- [Matplotlib][matplotlib] ([Matplotlib license][matplotlib-license])
- [netaddr][] (BSD-3-Clause license)
- [NumPy][numpy] ([NumPy license][numpy-license])
- [pypcap][] (BSD-3-Clause license)

### Pure CSS Layout

Layout using [Pure CSS][pure] (BSD-3-Clause license) compiled from the
[pure-site][] project. The layout is free to use under the zLib license.


[bottle]: http://bottlepy.org/
[matplotlib]: https://matplotlib.org/
[matplotlib-license]: https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE
[netaddr]: https://pypi.python.org/pypi/netaddr
[nix]: https://nixos.org/nix/
[numpy]: http://www.numpy.org/
[numpy-license]: http://www.numpy.org/license.html#license
[pure]: http://purecss.io/
[pypcap]: https://pypi.python.org/pypi/pypcap
[pure-site]: https://github.com/yahoo/pure-site
