# DAG-OS

## Development

### Linux

You may start a tmux session with [tmuxinator](https://github.com/tmuxinator/tmuxinator) by running following command in repository root.
It uses the `.tmuxinator.yml` to start a tmux session.

```console
tmuxinator local
```

### Windows

Get path to repository in WSL, e.g.,

```bash
wslpath -w .
\\wsl$\ubuntu\home\dev\coding\dagos\dagos\src
```

Add this path to `PYTHONPATH` in Windows:

* PowerShell

  ```powershell
  $env:PYTHONPATH='\\wsl$\ubuntu\home\dev\coding\dagos\dagos\src'
  ```

* Command Prompt

  ```cmd
  set PYTHONPATH=\\wsl$\ubuntu\home\dev\coding\dagos\dagos\src
  ```

Afterwards, run `dagos`:

```powershell
python -m dagos
Usage: python -m dagos [OPTIONS] COMMAND [ARGS]...
```
