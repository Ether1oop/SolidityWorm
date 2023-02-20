import http.client
import urllib.error

import requests
import os
import zipfile
import json
import time
import os
import zipfile
from urllib.request import urlopen
from urllib.request import Request
from github import Github


def zip_ya(folder_name, zip_name):  # folder_name 要压缩的文件夹路径; zip_name压缩后文件夹的名字
    z = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(folder_name):
        fpath = dirpath.replace(folder_name, '')  # 不使用replace会从根目录开始复制
        fpath = fpath and fpath + os.sep or ''  # 实现当前文件夹以及包含的所有文件的压缩
        for filename in filenames:
            z.write(os.path.join(dirpath, filename), fpath + filename)
    z.close()
    print("压缩完成！")


def appendFile(absolutlyFilepath, content):
    with open(absolutlyFilepath, 'a') as file:
        file.write(content)


def writeFile(absolutlyFilepath, content):
    with open(absolutlyFilepath, 'w') as file:
        file.write(content)


def openFileByString(absolutlyhFilepath):
    with open(absolutlyhFilepath, 'r') as file:
        return file.read()


def openFileByLines(absolutlyFilepath):
    with open(absolutlyFilepath, 'r') as file:
        return file.readlines()


def getHeaders(token):
    headers = {'User-Agent': 'Mozilla/5.0',
               'Authorization': 'token ' + token,
               'Content-Type': 'application/json',
               'Accept': 'application/json'
               }
    return headers


def getSolidityRelatedReponame():
    _github = Github("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")
    repositories = _github.search_repositories(query='language:solidity')
    try:
        for repo in repositories:
            if repo.stargazers_count >= 3:
                appendFile("name.txt", repo.full_name + "\n")
    except IndexError:
        print(IndexError)


def getTotalCountsByStars(search_info, headers, stars):
    url = 'https://api.github.com/search/repositories?q={search}%20stars:<={stars}&per_page=100&sort=stars' \
          '&order=desc'.format(search=search_info, stars=stars)
    req = requests.get(url=url, headers=headers)
    data = json.loads(req.text)
    return data["total_count"]


def getEachPageMessage(search_info, headers, page, stars):
    url = 'https://api.github.com/search/repositories?q={search}%20stars:<={stars}&page={num}&per_page=100&sort=stars' \
          '&order=desc'.format(search=search_info, num=page, stars=stars)
    req = Request(url, headers=headers)
    response = urlopen(req).read()
    result = json.loads(response.decode())
    return result


def getSolidityRelatedRepositories():
    search_info = 'language:solidity'
    headers = getHeaders('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') # token记得换自己的
    stars = 22700  # 此处应为Integer.Max_Value，取一个极大的值作为筛选标准
    total_counts = getTotalCountsByStars(search_info,headers,stars)
    count = 1
    pages = int(total_counts/1000) + 1 # 此处为总页数，为目标库数目除以1k取整

    print("total_counts:"+str(total_counts)+"\t")
    for i in range(0,pages):
        stars_list=[]
        for page in range(1,11):
            results = getEachPageMessage(search_info,headers,page,stars)
            print("pages:"+str(i))
            for item in results['items']:
                stars_list.append(item['stargazers_count'])
                writeFile("Repositories/"+str(count)+".txt",json.dumps(item))
                count += 1
                print(item['full_name'])
        stars = stars_list[-1]
        time.sleep(1)


def getCommitContent():
    repoFileList = os.listdir("Repositories")
    reponameList = []
    headers=getHeaders("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")
    if not os.path.exists("SHA"):
        os.mkdir("SHA")
    for i in range(100,200):
        jsonStr = json.loads(openFileByString("Repositories/"+str(i + 1) + ".txt"))
        reponameList.append(jsonStr['full_name'])

    for i in range(0,len(reponameList)):
    # for i in range(600,700):
        if not os.path.exists("SHA/" + reponameList[i].replace('/', ' ')):
            os.mkdir("SHA/"+reponameList[i].replace('/',' '))
        for page in range(1, 100):  # 100是最大页数,每页一百个，至多1万个
            url = "https://api.github.com/repos/{repo}/commits?q=stress+test+label:bug+language:python+state:closed&per_page=100&page={num}".format(
                repo=reponameList[i], num=page)
            req = Request(url,headers=headers)
            response = urlopen(req).read()
            result = json.loads(response.decode())

            if not result:
                break
            if isinstance(result, dict):
                time.sleep(60)
                page -= 1
                print("Sleeping~")
                continue
            writeFile("SHA/"+reponameList[i].replace('/',' ')+"/"+str(page)+".json",json.dumps(result))
            print(reponameList[i]+"\t page:"+ str(page) + "\twrite success!")

#https://api.github.com/repos/raj-pranav/learn-solidity/commits/f1bad00681ce5b1ac31d9a95aaee5b174053b9a9

def getAllCommitContent():
    if not os.path.exists("SHA"):
        return None
    if not os.path.exists("everyCommit"):
        os.mkdir("everyCommit")

    headers = getHeaders("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")
    FolderList = os.listdir("SHA")
    urlList = []  # 设置一个空列表存放所有commit的url

    for i in range(0, len(FolderList)):
        FileList = os.listdir("SHA/" + FolderList[i])  # FolderList[i]//SHA下文件夹名称
        # 在everyCommit下为每个库创建一个文件夹，用来存放其每一个commit的内容文件
        if not os.path.exists("everyCommit/" + FolderList[i]):
            os.mkdir("everyCommit/" + FolderList[i])

        for a in range(0, len(FileList)):
            # FileList[a] 每个文件夹里的json文件名
            jsonStr = json.loads(openFileByString("SHA/" + FolderList[i] + "/" + FileList[a]))  # 提取每个json文件内容
            # 接下来从内容里提取url，即下面的jsonStr[x]['url']
            for x in range(0, len(jsonStr)):  # 每个文件里有100个commit，序号0-99
                if os.path.exists('everyCommit/' + FolderList[i] + '/' + jsonStr[x]['sha'] + '.json'):
                    continue

                urlList.append(jsonStr[x]['url'])
                url = jsonStr[x]['url']
                req = Request(url, headers=headers)
                response = urlopen(req).read()
                result = json.loads(response.decode())

                if 'message' in result:
                    time.sleep(60)
                    print("sleeping")
                    x -= 1
                    continue
                print(FolderList[i] + "\t" + jsonStr[x]['sha'] + "\t write success")
                writeFile("everyCommit/" + FolderList[i] + "/" + jsonStr[x]["sha"] + ".json", json.dumps(result))

def getBlobContent():
    if not os.path.exists("EachCommitBlob"):
        os.mkdir("EachCommitBlob")

    # 取得库名
    reponameList = os.listdir("everyCommit")
    for repo in reponameList:
        # 取得该库的每一次commit的内容
        commitList = os.listdir("everyCommit/" + repo)
        for commit in commitList:
            # 解析commit内容，对其files部分进行处理
            jsonStr = json.loads(openFileByString("everyCommit/" + repo + "/" + commit))
            if 'files' in jsonStr:
                #循环其files内容，如果修改的文件后缀以.sol结尾，就是我们需要的内容
                for i in range(0,len(jsonStr['files'])):
                    item = jsonStr['files'][i]
                    if item['filename'][-4:] == '.sol':
                        #以库名+commit的sha进行建立文件夹，以该files的sha作为文件名
                        if not os.path.exists("EachCommitBlob/" + repo):
                            os.mkdir("EachCommitBlob/" + repo)
                        if not os.path.exists("EachCommitBlob/" + repo + "/" + commit[:-5]):
                            os.mkdir("EachCommitBlob/" + repo + "/" + commit[:-5])
                        if item['sha'] == None:
                            continue
                        if os.path.exists("EachCommitBlob/" + repo + "/" + commit[:-5] + "/" + item['sha'] + ".json"):
                            continue
                        #获得其修改后的文件信息，进行存储
                        url = item['contents_url']
                        try:
                            headers = getHeaders("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")
                            req = Request(url, headers=headers)
                            response = urlopen(req).read()
                            result = json.loads(response.decode())
                        except urllib.error.HTTPError or http.client.RemoteDisconnected:
                            print("Sleeping~")
                            time.sleep(60)
                            i -= 1
                            continue
                        #防止出现API Limit
                        if 'message' in result:
                            time.sleep(60)
                            print("Sleeping")
                            i -= 1
                            continue
                        #输出提示信息和保存文本
                        print(repo+"\t"+commit[:-5]+"\t"+item['sha']+"\twrite success")
                        writeFile("EachCommitBlob/" + repo + "/" + commit[:-5] + "/" + item['sha'] + ".json", json.dumps(result))
