#A book downloader for openlibrary.org written in Python3
## Dependence
```
pip3 install requests

pip3 install lxml

pip3 install beautifulsoup4
```
#Usage

###1.Fill your account for openlibrary.org

```
username = “xxx” 

password = “xxx”

scale  = 2 # “scale” represents the quality of the book 1 > 2 > 4 > 8
           #  2 is highly recommened
           
downloader = BookDownloader(username,password,scale)
downloader.begin()
``` 


### 2.Run and then choose the book you want to download

### 3.Merge *.jpg to a single pdf by some softwares
