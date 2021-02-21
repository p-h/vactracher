{ pkgs ? import <nixpkgs> { }, python ? pkgs.python3 }:
pkgs.poetry2nix.mkPoetryApplication {
  inherit python;
  projectDir = ./.;
}
