# DAG-OS

## Development

### Windows

Get path to repository in WSL, e.g.,

```bash
wslpath -w .
\\wsl$\ubuntu\home\dev\coding\dagos\dagos
```

Add this path to `PYTHONPATH` in Windows:

* PowerShell

  ```powershell
  $env:PYTHONPATH='\\wsl$\ubuntu\home\dev\coding\dagos\dagos'
  ```

* Command Prompt

  ```cmd
  set PYTHONPATH=\\wsl$\ubuntu\home\dev\coding\dagos\dagos
  ```

Afterwards, run `dagos`:

```powershell
python -m dagos
Usage: python -m dagos [OPTIONS] COMMAND [ARGS]...
```
