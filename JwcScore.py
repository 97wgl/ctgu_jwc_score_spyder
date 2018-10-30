import requests
import io
import ImgProcess
import MyKNN
import os
from bs4 import BeautifulSoup
from PIL import Image

sno = "2015114103"   # 学号
pwd = ""   # 密码

# 登录时需要提交的表单数据
postData = {
    "__VIEWSTATE": "/wEPDwUKLTQ4NjU1OTA5NGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgEFCGJ0bkxvZ2luMRg1SjrafPmtoydz1mPeR4vBlIE=",
    "__EVENTVALIDATION": "/wEWBQK8vuPMAgKl1bKzCQKC3IeGDAK1qbSRCwLO44u1DdFTNDJgcOwlCVJHcDBqwrj3IMXf",
    "txtUserName": sno,
    "txtPassword": pwd,
    "btnLogin.x": "37",
    "btnLogin.y": "12",
    "CheckCode": ""
}

# 设置请求头，模拟浏览器登录（用处不大，教务系统没有robots协议，也没有任何反爬措施）
reqHeader = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "Content-Length": "306",
    "Content-Type": "application/x-www-form-urlencoded",
    "Host": "210.42.38.26:84",
    "Origin": "http://210.42.38.26:84",
    "Pragma": "no-cache",
    "Referer": "http://210.42.38.26:84/jwc_glxt/",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36"
}


# 解析成绩页面，返回一个二维列表
def htmlParse(html):
    soup = BeautifulSoup(html, "html.parser")
    score = soup.find("table", id = "ctl00_MainContentPlaceHolder_GridScore").findAll("td")
    scoreList = []
    for i in range(0, len(score) - 8, 8):
        temp = []
        for j in range (8):
            sc = score[i + j].string
            if j == 1:
                sc = ("春" if sc == "1" else "秋")
            temp.append(sc)
        scoreList.append(temp)
    scoreList.sort()  # x[] 表示按照第0列排序
    return scoreList

# 打印成绩
def printScoreList(scoreList):
    head = "{0:^4}\t{1:^4}\t{2:{8}^26}{3:^2}\t{4:^4}\t{5:^3}\t{6:^4}\t{7:^6}".format("学年", "学期", "课程名称", "课程学分", "考试类型", "考试成绩", "所获学分",	"成绩编号", chr(12288))
    print(head)
    for i in range(len(scoreList)):
        s = scoreList[i]
        bodyLine = "{0:^4}\t{1:{8}^4}{2:{9}^26}{3:^2}\t{4:{10}^4}\t{5:{11}^3}\t{6:^4}\t{7:^6}".format(s[0], s[1], s[2], s[3], s[4], s[5], s[6], s[7], chr(12288), chr(12288), chr(12288), chr(12288))
        print(bodyLine)

# 保存到文本
def save(sList):
    try:
        with open("./score.txt", "wb") as fw:
            for line in sList:
                fw.write((str(line) + "\n").encode("utf-8"))
    except Exception as ex:
        print("存入失败！" + ex)

def login(sno, pwd):
    print("正在连接服务器...")
    session = requests.session()  # 开启一次会话，确保获取验证码和登录的session是一致的
    url = "http://210.42.38.26:84/jwc_glxt/"   # 基础url
    loginUrl = url + "Login.aspx"              # 登录url
    scoreUrl = url + "Student_Score/Score_Query.aspx"  # 成绩url
    checkImgUrl = url + "ValidateCode.aspx"    # 验证码url
    filepath = "./validCodeImg.jpg"     # 图片保存路径
    cropPath = "./crop/"                # 图片分割保存路径
    trainPath = "./traindata/"          # 训练集路径
    flag = 0                            # 累计获取验证码次数

    print("正在识别验证码...")
    while flag < 99:  # 验证码识别不一定每次能成功，加个循环多次获取(当然，最好加代理，不然容易封ip)
        imgResponse = session.get(checkImgUrl)
        img = Image.open(io.BytesIO(imgResponse.content))
        img.save(filepath)
        ImgProcess.imgCrop(img, cropPath)  # 分割验证码
        code = MyKNN.dataTest(3, trainPath, cropPath)
        print("识别当前验证码为：{}".format(code))
        postData["CheckCode"] = code
        loginResponse = session.post(loginUrl, data = postData, headers = reqHeader)
        msg = BeautifulSoup(loginResponse.content, "html.parser").find("span", id = "lblMsg")
        if msg is None:
            print("识别成功！\n登陆中...")
            flag = 99
            scoreQueryResponse = session.get(scoreUrl)
            scoreList = htmlParse(scoreQueryResponse.content)
            print("登陆成功！")
            print("查询到您的成绩单如下：")
            printScoreList(scoreList)
        elif msg.string == "登录失败： 验证码不对！":
            flag += 1
            if flag == 99:
                print("已经尽力了，验证码无法识别！")
            else:
                print("正在识别，请稍候...")
        else:
            flag = 99
            print(msg.string)
        
def main():
    login(sno, pwd)

if __name__ == "__main__":
    main()
