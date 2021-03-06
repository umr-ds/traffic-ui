with import <nixpkgs> {};

( let
    pypcap = python27.pkgs.buildPythonPackage rec {
      pname = "pypcap";
      version = "1.1.6";
      name = "${pname}-${version}";

      src = python27.pkgs.fetchPypi {
        inherit pname version;
        sha256 = "1cx7qm0w2a91g5z8k3kmlwz0b8dkr0h8dlb64rwgyhp2laa33syi";
      };

      patches = [
        # The default setup.py searchs for pcap.h in a static list of default
        # folders. So we have to add the path to libpcap in the nix-store.
        (pkgs.writeText "libpcap-path.patch"
          ''
          --- a/setup.py
          +++ b/setup.py
          @@ -27,7 +27,8 @@ def recursive_search(path, target_files):

           def get_extension():
               # A list of all the possible search directories
          -    dirs = ['/usr', sys.prefix] + glob.glob('/opt/libpcap*') + \
          +    dirs = ['${pkgs.libpcap}', '/usr', sys.prefix] + \
          +        glob.glob('/opt/libpcap*') + \
                   glob.glob('../libpcap*') + glob.glob('../wpdpack*') + \
                   glob.glob('/Applications/Xcode.app/Contents/Developer/Platforms/' +
                             'MacOSX.platform/Developer/SDKs/*')
          '')
      ];

      buildInputs = with pkgs; [ libpcap python27Packages.dpkt ];

      meta = {
        homepage = https://github.com/pynetwork/pypcap;
        description = "Simplified object-oriented Python wrapper for libpcap";
        license = lib.licenses.bsd3;
      };
    };

    # Overriding matplotlib to use a GUI-backend, which is GTK2 for me.
    matplotlib = pkgs.python27Packages.matplotlib.override {
      enableGtk2 = true;
    };

  in python27.buildEnv.override {
    # compare https://github.com/NixOS/nixpkgs/issues/22319
    ignoreCollisions = true;
    extraLibs = with python27Packages; [
      bottle netaddr numpy plotly requests] ++
      [matplotlib pypcap] ++ [python27Packages.ipython];
  }
).env
