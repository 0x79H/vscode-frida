import urllib.request
import json
import shutil
import tempfile
import subprocess

from pathlib import Path
from base import BaseTool

class Installer(BaseTool):
    def download(self, local: Path):
        with urllib.request.urlopen('https://api.github.com/repos/NyaMisty/fouldecrypt/releases/latest') as response:
            info = json.loads(response.read())

        url = next(asset['browser_download_url']
                   for asset in info['assets'] if asset['name'].endswith('.deb'))

        with urllib.request.urlopen(url) as response, local.open('wb') as fp:
            shutil.copyfileobj(response, fp)

    def deploy(self, local: Path):
        remote = '/tmp/fouldecrypt.deb'
        subprocess.call(self.scp(str(local), remote, direction='up'))
        subprocess.call(self.ssh('dpkg', '-i', remote))
        subprocess.call(self.ssh('rm', remote))
        subprocess.call(self.ssh('apt-get', 'install', '-y', 'zip'))


if __name__ == "__main__":
    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int)
    parser.add_argument('-o', '--output', dest='output', action='store')
    parser.add_argument('-H', '--host', dest='host', action='store')
    parser.add_argument('-u', '--user', dest='user', action='store')
    opt = parser.parse_args()

    if opt.host and opt.user:
        i = Installer(opt.port, host=opt.host, user=opt.user)
    else:
        i = Installer(opt.port)

    cwd = Path(tempfile.gettempdir())
    tmp = cwd / 'fouldecrypt.deb'
    sys.stderr.write('downloading latest fouldecrypt from GitHub\n')
    i.download(tmp)
    sys.stderr.write('downloaded\n')
    sys.stderr.write('deploying to iOS\n')
    i.deploy(tmp)
    sys.stderr.write('done\n')
