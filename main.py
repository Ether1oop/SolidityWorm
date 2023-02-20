import json
import solidityWormFunction


if __name__ == '__main__':
    # solidityWormFunction.getSolidityRelatedRepositories() # 获取Solidity的库名
    solidityWormFunction.getCommitContent() # 根据库名获取其所有commit的哈希
    # solidityWormFunction.getAllCommitContent() # 根据哈希值爬取每一次commit的具体信息及其改动部分源码
    # solidityWormFunction.getBlobContent()