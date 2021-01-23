# -*- coding: utf-8 -*-

import json
import re
import subprocess
import sys
import time
from requests_oauthlib import OAuth1Session

# 取得したConsumer Key等と置き換えてください
CK = 'consumer_key'
CS = 'consumer_secret'
AT = 'access_token'
AS = 'access_token_secret'

FILTER_URL = 'https://stream.twitter.com/1.1/statuses/filter.json'

def usage():
    print('Usage: python %s Lv=<level>+Name=<name> ...' % sys.argv[0])
    print('Example: python %s Lv=120+Name=エウロペ Lv=120+Name=マキュラ' % sys.argv[0])
    sys.exit()

def unsupported_os():
    print("Don't understand this operating system.")
    print("Try on Windows or Mac.")
    sys.exit()

# stringをクリップボードにコピー
def set_clipboard(string, os_name):
    if os_name == 'win32':
        process = subprocess.Popen('clip', stdin = subprocess.PIPE, shell=True)
    elif os_name == 'darwin':
        process = subprocess.Popen('pbcopy', stdin = subprocess.PIPE, shell=False)
    else:
        unsupported_os()
    process.communicate(string.encode("utf-8")) # str型をbyte型に変換

patternID = re.compile(r'([0-9A-F]{8})\s:参戦ID')
patternLvName = re.compile(r'Lv([0-9]*)\s(.*)')
def parseText(text):
    result = {}
    lines = text.splitlines()
    for line in lines:
        res = patternID.match(line)
        if res:
            result["ID"] = res.group(1)
            continue

        res = patternLvName.match(line)
        if res:
            result["Lv"] = res.group(1)
            result["Name"] = res.group(2)
            break

        if "四大天司ＨＬ" in line:
            result["Name"] = "四大天司ＨＬ"
            break

        if "黄龍・黒麒麟HL" in line:
            result["Name"] = "黄龍・黒麒麟HL"
            break

    return result


def main():
    try:
        os_name = sys.platform
        if os_name != 'win32' and os_name != 'darwin':   # Windows / Mac
            unsupported_os()

        args = []
        if len(sys.argv) > 1:
            for i, arg in enumerate(sys.argv):
                if i == 0:
                    continue

                t = {}
                opts = arg.split("+")
                for opt in opts:
                    s = opt.split("=")
                    if s[0] == "Lv":
                        t["Lv"] = s[1]
                    elif s[0] == "Name":
                        t["Name"] = s[1]

                args.append(t)

        print(args)

        # OAuth
        oauth_session = OAuth1Session(CK, CS, AT, AS)
        params = {'track': "参加者募集！"}
        req = oauth_session.post(FILTER_URL, params=params, stream=True)
        
        print("read stream...")
        for line in req.iter_lines():
            line_decode = line.decode('utf-8')
            if line_decode != '':   # if not empty
                tweet = json.loads(line_decode)
                # pass tweets via the game page
                if tweet.get('source') != '<a href="http://granbluefantasy.jp/" rel="nofollow">グランブルー ファンタジー</a>':
                    continue

                pt = parseText(tweet.get('text'))
                #print(pt)
                if ("ID" in pt) and ("Name" in pt):
                    if args == []:
                        set_clipboard(pt["ID"], os_name)
                    else:
                        for arg in args:
                            checkLv = arg["Lv"] == pt["Lv"] if ("Lv" in arg) and ("Lv" in pt) else True
                            checkName = arg["Name"] in pt["Name"] if "Name" in arg else True

                            if checkLv and checkName:
                                set_clipboard(pt["ID"], os_name)
                                print(f"{pt}")
                                break

    except KeyboardInterrupt:
        print()
        sys.exit()

if __name__ == "__main__":
    main()
