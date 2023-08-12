import json
import os
import sys
import socket
import re

MENU = """
端口转发管理:
1. 添加端口
2. 删除端口
3. 查看规则
4. 查看转发表
5. 菜单
"""
CMD_TEMPLATE = (
    "iptables -t nat -{model} PREROUTING -p {protocol} -d {local_ip} --dport {local_port} -j DNAT --to {remote_ip}:{remote_port}",
    "iptables -t nat -{model} POSTROUTING -p {protocol} -s {remote_ip} --sport {remote_port} -j SNAT --to {local_ip}"
)

PATH = "/etc/pynat"
config = []

l_ip = None

DEBUG = False


def generate_cmd(local_port, remote_ip, remote_port, model="A", protocol="TCP") -> tuple:
    global l_ip
    return (
        CMD_TEMPLATE[0].format(
            local_ip=l_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            protocol=protocol,
            model=model
        ),
        CMD_TEMPLATE[1].format(
            local_ip=l_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            protocol=protocol,
            model=model
        )
    )


def get_local_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


def run_cmd(cmd: str):
    os.system(cmd)


def resolve_params() -> dict:
    l_port = input("本地PORT:")
    r_port = input("远程PORT:")
    r_ip = input("远程IP:")

    match = re.match(r"^\d+\.\d+\.\d+\.\d+$", r_ip)
    if match == None or int(l_port) > 65534 or int(l_port) < 1 or int(r_port) > 65534 or int(r_port) < 1:
        return None
    return {"l_port": l_port, "r_ip": r_ip, "r_port": r_port}


def find_in_config(params: dict) -> int:
    global config
    count = 0
    for i in config:
        if i['local_port'] == params['l_port']:
            #  and i['remote_ip'] == params['r_ip'] and i['remote_port'] == params['r_port']
            return count
        count += 1
    return -1


def save_config():
    tmp_cmd = ""
    for i in config:
        tmp_cmd += " && ".join(list(generate_cmd(
            i["local_port"], i["remote_ip"], i["remote_port"], "A", "TCP"))) + "\n"
        tmp_cmd += " && ".join(list(generate_cmd(
            i["local_port"], i["remote_ip"], i["remote_port"], "A", "UDP"))) + "\n"
    with open(PATH, "w") as w:
        w.write("# " + json.dumps(config) + "\n\n")
        w.write(tmp_cmd)


def add():
    params = resolve_params()
    if params is None:
        print("输入参数不符合规范")
        return
    index = find_in_config(params)
    if index != -1:
        print("已有重复的规则")
        return
    else:
        config.append(
            {"local_port": params["l_port"],
             "remote_ip": params["r_ip"],
             "remote_port": params["r_port"]}
        )

    cmd = " && ".join(list(generate_cmd(
        params["l_port"], params["r_ip"], params["r_port"], "A", "TCP")))
    if DEBUG:
        print("add TCP -> \n", cmd)
    os.system(cmd)
    cmd = " && ".join(list(generate_cmd(
        params["l_port"], params["r_ip"], params["r_port"], "A", "UDP")))
    if DEBUG:
        print("add UDP -> \n", cmd)
    os.system(cmd)
    save_config()
    print("添加成功\n")


def remove():
    params = resolve_params()
    if params is None:
        print("输入参数不符合规范")
        return
    index = find_in_config(params)
    if index != -1:
        config.pop(index)
    else:
        print("没有匹配的规则")
        return

    cmd = " && ".join(list(generate_cmd(
        params["l_port"], params["r_ip"], params["r_port"], "D", "TCP")))
    if DEBUG:
        print("remove TCP -> \n", cmd)
    os.system(cmd)
    cmd = " && ".join(list(generate_cmd(
        params["l_port"], params["r_ip"], params["r_port"], "D", "UDP")))
    if DEBUG:
        print("remove UDP -> \n", cmd)
    os.system(cmd)
    save_config()
    print("删除成功\n")


def show():
    global config
    if len(config) > 0:
        for i in config:
            print(f"{i['local_port']}->{i['remote_ip']}:{i['remote_port']}")
    else:
        print("暂无规则")


def init():
    # 获取内网IP
    global l_ip, config
    l_ip = get_local_ip()
    if DEBUG:
        print("内网ip ->", l_ip)

    # 准备文件存储
    if not os.path.exists(PATH):
        with open(PATH, "w") as w:
            pass
    else:
        with open(PATH, "r") as r:
            txt = r.readline()
            if len(txt) > 2:
                config = json.loads(txt[2:])


def main():
    global DEBUG
    init()
    print(MENU)
    while True:
        tag = input()
        if tag == "1":
            add()
        elif tag == "2":
            remove()
        elif tag == "3":
            show()
        elif tag == "4":
            CMD = "iptables -t nat -L --line-numbers"
            os.system(CMD)
        elif tag == "5":
            print(MENU)
        elif tag == "clear":
            CMD = "clear"
            os.system(CMD)
        elif tag == "debug":
            DEBUG = not DEBUG
        


    return 0


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt as e:
        # 静默异常
        if DEBUG:
            print(e)
        print("\n")
