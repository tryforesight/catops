#!/usr/bin/env -S python -u
"""
staging script
"""
import os, sys, datetime as dt, requests, time
from datetime import datetime as dt

token = os.getenv('DOCKER_TOKEN')

repo_name = os.getenv('DOCKER_REPO')

vm_name = os.getenv('VM_NAME')

def last_local_update():
    try:   f = open('last.update')
    except FileNotFoundError:
        return ''
    return f.readline().strip()

def utc_datetime():
    return dt.utcnow().isoformat()[:19]+'Z'

def save_local_update():
    return open('last.update', 'w').write(utc_datetime())

def last_remote_update():
    url = f'https://api.github.com/repos/{repo_name}'
    headers = dict(authorization="Bearer "+token)
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
    return response.json()['pushed_at']

def needs_update():
    llu = last_local_update()
    lru = last_remote_update()
    return llu < lru

def update_repo():
    dirname = f"repos/{utc_datetime()}"
    print("DO REPO ", dirname)
    directory = os.getpwd()
    try:
        def run(command):
            print("CMD", repr(command))
            assert 0==os.system(command)
        run(f'mkdir -p {dirname}')
        run(f'cd       {dirname} ; git clone git@github.com:{repo_name}.git')
        run(f'cd       {dirname}/{vm_name} ; git checkout stage')
        run(f'make  -C {dirname}/{vm_name} stage')
        run(f"ln   -sf {dirname}/{vm_name} {vm_name}")
        print("IT WENT OK!")
        save_local_update()
    except:  print("SOME ERROR HAPPENED")
    finally: os.chdir(directory)
    return

def maybe_update_repo():
    if needs_update():
        print("update it")
        update_repo()
    else:
        print("dont")


if __name__ == '__main__':
    while 1:
        maybe_update_repo()
        time.sleep(6)
