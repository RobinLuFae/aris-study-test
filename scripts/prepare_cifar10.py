"""Stage the official small CIFAR-10 archive under the authorized D: project."""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import torchvision
from torchvision.datasets.utils import download_url, extract_archive

root=Path(__file__).resolve().parents[1]
assert Path(sys.prefix).resolve()==(root/'.conda').resolve()
assert root.drive.upper()=='D:'
downloads=root/'downloads'
data=root/'data'
downloads.mkdir(exist_ok=True);data.mkdir(exist_ok=True)
cls=torchvision.datasets.CIFAR10
archive=downloads/cls.filename
download_url(cls.url,str(downloads),filename=cls.filename,md5=cls.tgz_md5)
assert hashlib.md5(archive.read_bytes()).hexdigest()==cls.tgz_md5
extract_archive(str(archive),str(data))
train=cls(str(data),train=True,download=False)
assert len(train)==50000 and train.data.shape==(50000,32,32,3)
receipt={'timestamp':datetime.datetime.now(datetime.timezone.utc).isoformat(),
         'source':cls.url,'archive':str(archive),'bytes':archive.stat().st_size,
         'md5_expected':cls.tgz_md5,'md5_verified':True,'training_images':len(train),
         'training_shape':list(train.data.shape),'test_split_loaded_for_training':False,
         'citation':'Alex Krizhevsky, Learning Multiple Layers of Features from Tiny Images, 2009',
         'dataset_page':'https://www.cs.toronto.edu/~kriz/cifar.html'}
(root/'logs/cifar10-data.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(receipt,ensure_ascii=False,indent=2))
print('CIFAR10_DATA_READY')
