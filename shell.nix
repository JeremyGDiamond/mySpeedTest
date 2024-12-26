{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "speedtest-env";

  buildInputs = [
    pkgs.fast-cli                     # Command-line tool for fast.com
    pkgs.speedtest-cli                # Command-line interface for Speedtest.net
    pkgs.coreutils                    # Common Unix tools
    (pkgs.python311.withPackages (ps: with ps; [ numpy pwntools ])) # Python 3.11 with numpy and pwntools
  ];

  shellHook = ''
    echo "Environment ready!"
    echo "Tools available: fast-cli, speedtest-cli, coreutils, Python 3.11 with numpy and pwntools."
  '';
}
