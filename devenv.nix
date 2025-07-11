{ ... }:

{
  # https://devenv.sh/basics/

  # https://devenv.sh/packages/

  # https://devenv.sh/languages/
  languages.python = {
    enable = true;
    venv.enable = true;
    uv = {
      enable = true;
      sync.enable = true;
    };
  };

  # https://devenv.sh/pre-commit-hooks/
  git-hooks.hooks = {
    ruff = {
      enable = true;
      args = [ "--select" "I" ];
    };
    ruff-format.enable = true;
    check-added-large-files.enable = true;
    check-toml.enable = true;
    check-yaml.enable = true;
    trim-trailing-whitespace = {
      enable = true;
      excludes = [ ".*.md$" ];
    };
    end-of-file-fixer.enable = true;
  };

  # See full reference at https://devenv.sh/reference/options/
}
