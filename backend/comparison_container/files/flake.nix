{
  description = "DiffKemp dependencies with additional dependencies";

  inputs = {
    diffkemp.url = "/diffkemp";
  };

  outputs = { self, diffkemp }:
    let
      system = "x86_64-linux";
      pkgs = import diffkemp.inputs.nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        inherit (diffkemp.devShells.${system}) default;
        inputsFrom = [
          diffkemp.packages.${system}.default
          diffkemp.devShells.${system}.default
        ];
        buildInputs = with pkgs; [
          # commit-analysis dependency
          python312
          util-linux
          # diffkemp-analysis dependency
          python3Packages.gitpython
          # mbedtls dependencies
          python3Packages.jsonschema
          python3Packages.jinja2
          perl
          # other
          procps
        ];
        IN_DEV_SHELL = true;
        # Fixing DiffKemp build that throws an error.
        shellHook = ''
          export PYTHONPATH="/diffkemp:$PYTHONPATH"
        '';
      };
    };
}
