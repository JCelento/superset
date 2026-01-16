# How to Increase WSL2 Memory for Docker/Impala

## Current Configuration
- WSL2 Memory Limit: 10GB (set in `.wslconfig`)
- Docker Available Memory: ~9.7GB
- Impala Needs: More memory for Java heap + query processing

## Solution: Increase WSL2 Memory

### Option 1: Edit from WSL (Recommended)

1. **Open the .wslconfig file:**
   ```bash
   # Find your Windows username
   WINDOWS_USER=$(ls /mnt/c/Users/ | grep -v "Public\|Default" | head -1)
   echo "Windows user: $WINDOWS_USER"
   
   # Edit the file (use nano, vim, or code)
   nano /mnt/c/Users/$WINDOWS_USER/.wslconfig
   # OR
   code /mnt/c/Users/$WINDOWS_USER/.wslconfig  # if VS Code is installed
   ```

2. **Update the memory setting:**
   ```ini
   [wsl2]
   # Increase memory to 16GB (or more if you have it)
   memory=16GB
   processors=6
   ```

3. **Restart WSL:**
   ```bash
   # From WSL, run this command in Windows PowerShell/CMD:
   # wsl --shutdown
   
   # Or from Windows PowerShell (run as Administrator):
   wsl --shutdown
   ```

4. **Restart WSL** (it will auto-restart when you open a new terminal)

### Option 2: Edit from Windows

1. **Open File Explorer** and navigate to:
   ```
   C:\Users\<YourUsername>\.wslconfig
   ```

2. **Edit with Notepad or any text editor:**
   ```ini
   [wsl2]
   memory=16GB
   processors=6
   ```

3. **Restart WSL:**
   - Open PowerShell as Administrator
   - Run: `wsl --shutdown`
   - Open a new WSL terminal

### Recommended Memory Settings

For Impala to work well:
- **Minimum**: 12GB (if you have 16GB total RAM)
- **Recommended**: 16GB (if you have 32GB total RAM)
- **Optimal**: 20GB+ (if you have 64GB total RAM)

### Verify the Change

After restarting WSL, verify the new memory limit:
```bash
docker info | grep "Total Memory"
```

You should see the new memory limit reflected.

### Restart Impala

After increasing memory, restart Impala:
```bash
docker compose -f docker-compose-impala.yml restart impalad
```

### Notes

- The `.wslconfig` file must be in your Windows user directory: `C:\Users\<YourUsername>\.wslconfig`
- Changes only take effect after restarting WSL (`wsl --shutdown`)
- Don't set memory higher than your physical RAM
- Leave some RAM for Windows (at least 4-8GB)
