# -*- coding:utf-8 -*-
"""
@version: 1.0
@author: Roy
@contact: ruoyi_ran@foxmail.com
@file: fetch.py
@time: 2018/7/15 15:27
"""
import argparse

import os

import requests

from urllib import parse

import shutil

from html_parser import MyHTMLParser
from utils import unzip_file, remove_dir

DEFAULT_LANGUAGE = "en"
DEFAULT_DOWNLOAD_DIR = "./output"
DOWNLOAD_TEMP_DIR = r"/temp/subtitles"
YOUTUBE_HOST = "y%60%60%60be.com"
REQUEST_URL = "http://mo.dbxdb.com/Yang/mo.php?lang=%s&url=%s"
RESULT_SUBTITLE_PREFIX = "subtitle.php?vid="
HOST = "mo.dbxdb.com"
REFERER = "http://mo.dbxdb.com/Yang/"
SUBTITLE_DOWNLOAD_URL = "http://mo.dbxdb.com/Yang/%s"
SUBTITLE_PAGE = "subtitle.php"
SUBTITLE_FILE_EXTENSION = ".srt"
HTTP_REQUEST_TIMEOUT = 5


def get_headers():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Host": HOST,
        "Proxy-Connection": "keep-alive",
        "Referer": REFERER,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36"
    }
    return headers


def get_full_url(language, youtube_url):
    return REQUEST_URL % (language, youtube_url)


def request_url(url):
    print("Request url:", url)
    response = requests.get(url, timeout=HTTP_REQUEST_TIMEOUT, headers=get_headers())
    return response


def get_subtitle_download_url(response_content):
    download_url = ""
    parser = MyHTMLParser()
    parser.feed(response_content)
    for attr in parser.attrs:
        attr_name, attr_value = attr
        if attr_name == "src" and attr_value.find(SUBTITLE_PAGE) >= 0:
            download_url = SUBTITLE_DOWNLOAD_URL % attr_value
            break
    parser.close()
    return download_url


def get_content_type(headers):
    content_type = ""
    for key in headers:
        if key.lower() == "content-type":
            content_type = headers[key]
            break
    return content_type


def move_subtitle_to_download_dir(dir_path, name_list, target_dir, file_ext):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
    for filename in name_list:
        filepath = os.path.join(dir_path, filename)
        if os.path.exists(filepath) and \
            os.path.exists(target_dir) and \
            filepath.endswith(file_ext):
            target_filepath = os.path.join(target_dir, filename)
            shutil.move(filepath, target_filepath)
            return True, target_filepath
    return False, ""


def download_subtitle(download_url, download_dir):
    if not download_url:
        return False, ""
    print("Download url:", download_url)
    subtitle_vid = os.path.basename(download_url).split("=")[1]
    print("Subtitle vid:", subtitle_vid)
    temp_file_path = os.path.join(DOWNLOAD_TEMP_DIR, subtitle_vid + ".zip")
    if os.path.exists(temp_file_path):
        success, file_path = save_subtitle_file(download_dir, temp_file_path)
        return success, file_path
    response = request_url(download_url)
    content_type = get_content_type(response.headers)
    if content_type != "application/zip":
        print("Unknown content type:", content_type)
        return False, ""
    if not os.path.exists(DOWNLOAD_TEMP_DIR):
        os.makedirs(DOWNLOAD_TEMP_DIR)
    with open(temp_file_path, "wb") as writer:
        writer.write(response.content)
    success, file_path = save_subtitle_file(download_dir, temp_file_path)
    return success, file_path


def save_subtitle_file(download_dir, temp_file_path):
    dir_path, name_list = unzip_file(temp_file_path)
    success, file_path = move_subtitle_to_download_dir(dir_path, name_list, download_dir, SUBTITLE_FILE_EXTENSION)
    remove_dir(dir_path)
    return success, file_path


def fetching(language, youtube_url, download_dir):
    print("Youtube url:", youtube_url)
    youtube_url = parse.quote(youtube_url)
    youtube_url = youtube_url.replace("youtube.com", YOUTUBE_HOST)
    url = get_full_url(language, youtube_url)
    try:
        response = request_url(url)  # get subtitle vid
        content_type = get_content_type(response.headers)
        if content_type == "text/html":
            download_url = get_subtitle_download_url(response.content.decode())
            success, file_path = download_subtitle(download_url, download_dir)
            if success:
                print("Succeed to download youtube subtitle, subtitle has saved to: {}".format(file_path))
            else:
                print("Failed to download youtube subtitle")
            return success
    except Exception as e:
        print("Exception:", e)
        print("Failed to download youtube subtitle")
        return False


def fetching_urls(language, url_file_list, download_dir):
    try:
        with open(url_file_list, "r") as reader:
            download_failed_urls = list()
            lines = reader.readlines()
            total_url_count = 0
            for line in lines:
                url = line.strip()
                if not url:
                    return
                total_url_count += 1
                success = fetching(language, url, download_dir)
                if not success:
                    download_failed_urls.append(url)
                print()
        print("Total urls: {}\nDownloaded: {}".format(total_url_count, total_url_count-len(download_failed_urls)))
        if download_failed_urls:
            print("Download subtitle failed urls:")
            for url in download_failed_urls:
                print(url)
    except Exception as e:
        print("Exception:", e)


if __name__ == '__main__':
    # Description of this program.
    desc = "Auto fetch Youtube subtitles."
    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("--language", required=False, default=DEFAULT_LANGUAGE,
                        help="subtitle language")
    parser.add_argument("--download_dir", required=False, default=DEFAULT_DOWNLOAD_DIR,
                        help="subtitle download output directory")
    parser.add_argument("--youtube_url", required=False, default="",
                        help="youtube video url")
    parser.add_argument("--youtube_url_file_list", required=False, default="",
                        help="a text file contains youtube urls")
    args = parser.parse_args()
    if not args.youtube_url and not args.youtube_url_file_list:
        print("youtube_url or youtube_url_file_list can not be empty")
        exit(0)
    if args.youtube_url:
        fetching(args.language, args.youtube_url, args.download_dir)
    else:
        fetching_urls(args.language, args.youtube_url_file_list, args.download_dir)
