# TrafficUI
A web-UI for assigning labels to existing flows.

## Configuration
Copy the `config-example.ini` to `config.ini` and configure it for your needs.

## Starting
### Nix/NixOS
The `shell.nix`-file knows what to do. Just let [nix][] do the work for you.

```bash
$ nix-shell --run ./traffic_ui.py
```

### Other systems
Install the *Python Libraries* listed below with your favorite tools and start
`traffic_up.py`.

## Dependencies
### Backend, Python Libraries

- [Bottle][bottle] (MIT license)
- [Matplotlib][matplotlib] ([Matplotlib license][matplotlib-license])
- [netaddr][] (BSD-3-Clause license)
- [NumPy][numpy] ([NumPy license][numpy-license])
- [Plotly.py][plotly] (MIT license)
- [pypcap][] (BSD-3-Clause license)
- [requests][] required by Plotly (Apache license)

### Frontend

- [Awesomplete][awesomplete] (MIT license)
- [Plotly.js][plotly] (MIT license)
- [Pure CSS-Framework][pure] (BSD-3-Clause license)
- [Responsive Side Menu, Pure Layout][pure-layout] (zLib license)

[awesomplete]: https://leaverou.github.io/awesomplete/
[bottle]: http://bottlepy.org/
[matplotlib]: https://matplotlib.org/
[matplotlib-license]: https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE
[netaddr]: https://pypi.python.org/pypi/netaddr
[nix]: https://nixos.org/nix/
[numpy]: http://www.numpy.org/
[numpy-license]: http://www.numpy.org/license.html#license
[plotly]: https://plot.ly/
[pure]: http://purecss.io/
[pure-layout]: https://purecss.io/layouts/
[pypcap]: https://pypi.python.org/pypi/pypcap
[requests]: https://github.com/requests/requests
