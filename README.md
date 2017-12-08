# TrafficUI
A web-UI for assigning labels to existing flows.

## Configuration
Copy the `config-example.ini` to `config.ini` and configure it for your needs.
You should at least change the upload password, the directories and the path
to the rating's storage file.

## `httpd` section
- `host`: The host or IP-address for the HTTP-server.
  (type: *string*, default: *localhost*)
- `post`: The port on which the server will accept connections.
  (type: *int*, default: *8080*)
- `plotting`: A backend to be used for plotting the graphs.
  (type: one of *png*, *plotly*, default: *png*)
- `upload_password`: The password to protect the web upload against missuse.
  (type: *string*, default: None)

## `dirs` section
- `input`: The directory where all the *pcap*-files will be stored.
  (type: *directory*, default: None)
- `cache`: The directory where the cached files will be stored. Perhaps you
  don't want this on a tmpfs, because rebuilding could take some time.
  (type: *directory*, default None)

## `ratings` section
- `store`: A CSV-file which will contain all assigned ratings.
  (type: *file*, default: None)
- `ratings`: A comma-separated list of available ratings.
  (type: *comma-separated string*, default: *upload,download,interactive*)
- `enforce`: Set this flag to only allow ratings specified in `ratings`.
  (type: *boolean*, default: *true*)


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
