# TrafficUI
A web-UI for assigning labels to network flows present as *pcap*-files. Those
flows can be queried, viewed, rated and uploaded.


## Search
The overview page contains a search field to query flows. A query may contain
tags to search for a specific attribute. Multiple tags will be combined with
a logical AND. If no tag was specified, the search will be applied for each
possible attribute.

The tag-syntax is `:TAG=SEARCH` where `TAG` is an element from the following
list and `SEARCH` is your request. Multiple tags look like this:
`:rating=upload :port=443`

- `as`: Name of an autonomous system
- `asn`: Exact autonomous system number
- `bgp`: BGP-prefix
- `src_ip`: Source IP-address
- `dst_ip`: Destination IP-address
- `ip`: Both source and destination IP-address
- `sport`: Source port
- `dport`: Destination port
- `port`: Both source and destination port
- `rating`: Assigned rating/label
- `file`: Filename in file system


## Configuration
Copy the `config-example.ini` to `config.ini` and configure it for your needs.
You should at least change the upload password, the directories and the path
to the rating's storage file.

### `httpd` section
- `host`: The host or IP-address for the HTTP-server.
  (type: *string*, default: *localhost*)
- `post`: The port on which the server will accept connections.
  (type: *int*, default: *8080*)
- `plotting`: A backend to be used for plotting the graphs.
  (type: one of *png*, *plotly*, default: *png*)
- `upload_password`: The password to protect the web upload against missuse.
  (type: *string*, default: None)

### `dirs` section
- `input`: The directory where all the *pcap*-files will be stored.
  (type: *directory*, default: None)
- `cache`: The directory where the cached files will be stored. Perhaps you
  don't want this on a tmpfs, because rebuilding could take some time.
  (type: *directory*, default None)

### `ratings` section
- `store`: A CSV-file which will contain all assigned ratings.
  (type: *file*, default: None)
- `ratings`: A comma-separated list of available ratings.
  (type: *comma-separated string*, default: *upload,download,interactive*)
- `enforce`: Set this flag to only allow ratings specified in `ratings`.
  (type: *boolean*, default: *true*)


## Installation/Running
### pip
**Prerequisite:** Python 2.7 with [pip][] and [libpcap][]

```bash
pip install -r requirements.txt
./traffic_ui.py
```

### Nix/NixOS
**Prerequisite:** [Nix][nix] Package Manager

```bash
nix-shell --run ./traffic_ui.py
```

### systemd-nspawn container
**Prerequisite:** GNU/Linux distribution with systemd and [debootstrap][]
(available in most distributions) 

**WORK IN PROGRESS**
```bash
# Bootstrap a Debian as root user. This takes some time.
cd /var/lib/machines/
debootstrap --arch=amd64 stable debian-trafficui

# Log in to container, set root's password and log out
systemd-nspawn -UD debian-trafficui
passwd
^D

# Boot container
systemd-nspawn -bUD debian-trafficui
# Now log in as root
# Install required packages
apt-get update
apt-get install git python-pip libpcap-dev
# Add a new user and set it's password
useradd -m -s /bin/bash trafficui
passwd trafficui
^D

# Let's login as trafficui and install the TrafficUI
git clone https://github.com/umr-ds/traffic-ui.git
cd traffic-ui/
pip install -r requirements.txt
cp config{-example,}.ini
vi config.ini
./traffic_ui.py
# You should be able to visit the container's TrafficUI from the host
^C ^D ^]^]^]

# TODO:
# * --private-network for the container
# * systemd service for TrafficUI
# * create an exportable container-file and import it again
```

### Docker container
**TODO**


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
[debootstrap]: https://wiki.debian.org/Debootstrap
[libpcap]: http://www.tcpdump.org/
[matplotlib]: https://matplotlib.org/
[matplotlib-license]: https://github.com/matplotlib/matplotlib/blob/master/LICENSE/LICENSE
[netaddr]: https://pypi.python.org/pypi/netaddr
[nix]: https://nixos.org/nix/
[numpy]: http://www.numpy.org/
[numpy-license]: http://www.numpy.org/license.html#license
[pip]: https://pip.pypa.io/
[plotly]: https://plot.ly/
[pure]: http://purecss.io/
[pure-layout]: https://purecss.io/layouts/
[pypcap]: https://pypi.python.org/pypi/pypcap
[requests]: https://github.com/requests/requests
