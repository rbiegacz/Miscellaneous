#
# Copyright (c) 2017 Rafal Biegacz
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# pylint: disable = C0301

"""
    simple script to delete files from your slack account
    AGING specifies files for deletion - i.e. files older than AGING days
"""
import sys
import calendar
from datetime import datetime, timedelta
import json
import unicodedata
import requests


class SlackConfig(object):
    """
    this class configures parameters of this scipt
    - connection details
    - mode of operation of this script
    """
    aging = 360
    slack_file_list = "https://slack.com/api/files.list"
    slack_delete_file = ".slack.com/api/files.delete?t="
    http_string = "https://"
    file_type = {}
    # file_type = {"text", "jpg", "png", "pptx", "doc", "pdf"}
    proxies = {}
    token = ""
    slack_domain = ""


    def __init__(self):
        pass

    def config_check(self):
        """
        this function verifies if the script is configured in appropriate way
        :return:
        True if all the parameters are ok and False otherwise
        """

        def message(parameter_string):
            """
            simple function to display error messages
            :type parameter_string: string
            :param parameter_string:
            parameter string to use in error message
            :return:
            error string
            """
            return "Configure {} parameter in appropriate way.".format(parameter_string)

        if self.aging <= 1:
            print message("aging")
            return False
        if self.token == "":
            print message("token")
            return False
        if self.slack_domain == "":
            print message("slack_domain")
            return False
        self.config_info()
        return True

    def config_info(self):
        """
        print general info about configuration
        :return: no value returned
        """
        if len(self.file_type) == 0:
            print "Deleting all file types."
        else:
            print "Deleting select file types: {}".format(self.file_type)
        print "Deleting files older than {} days\n".format(self.aging - 1)
        print "Using following proxy config: {}".format(self.proxies)
        print "(empty proxy list means: no proxy)"

def send_request_post(slackcfg, request_url, request_data):
    """
    this function is a wrapper around requests.post method
    :param slackcfg: reference to object of SlackConfig class
    :param request_url: URL to the Web method that should be called
    :param request_data: data associated with a Web method call
    :return:
    Response object returned by requests.post call.
    More on Response object - http://docs.python-requests.org/en/master/api/#requests.Response
    """
    response = None
    try_without_proxy = False

    try:
        response = requests.post(request_url, data=request_data, proxies=slackcfg.proxies)
    except requests.exceptions.RequestException as exception_msg:
        try_without_proxy = True

    if try_without_proxy:
        try:
            response = requests.post(request_url, data=request_data)
        except requests.exceptions.RequestException as exception_msg:
            print "Error connecting to {}.".format(request_url)
            print "Take a look on error details below..."
            print exception_msg
            sys.exit(1)
        finally:
            pass

    return response


def interpret_slack_response(response):
    """
        this function interprets the error received from requests.post method.
    :param response:
        it's a response return from requests.post call.
        please, read more here: http://docs.python-requests.org/en/master/api/#requests.Response
    :return:
        this function will inte
    """

    result_boolean = True
    response_dict = json.loads(response._content)

    #
    #print "Chunks:"
    #for chunk in response.iter_content(chunk_size=128):
    #    print chunk

    if not response.ok:
        result_string = "Got error from the Web Service. Take a look on the error.\n"
        result_string += response._content
        result_boolean = False
    else:
        if response_dict["ok"]:
            result_string = "Operation successful."
        else:
            result_string = "Got error from the Web Service. Take a look on the error.\n"
            result_string += response._content
            result_boolean = False
    return result_boolean, result_string


def delete_files_on_slack(slackcfg):
    """
        this function deletes files on slack
        in a loop it calls Slack WEB API to get a list of available files
        and deletes them one by one
        Description of files.delete --> https://api.slack.com/methods/files.delete
    :return:
        this function doesn't return any value;
        if it fails it will stop program execution and will display the encountered error
    """

    while 1:
        files_list_url = slackcfg.slack_file_list
        date = str(calendar.timegm((datetime.now() + timedelta(-slackcfg.aging)).utctimetuple()))
        data = {"token": slackcfg.token, "ts_to": date}
        try:
            response = send_request_post(slackcfg=slackcfg, request_url=files_list_url, request_data=data)
        except requests.exceptions.RequestException as exception_msg:
            print "Error connecting to {}.".format(files_list_url)
            print "Take a look on error details below..."
            print exception_msg
            sys.exit(1)
        finally:
            pass

        if len(response.json()["files"]) == 0:
            print "No files to delete."
            break
        for file_to_delete in response.json()["files"]:
            #
            # print file_to_delete["filetype"]
            if len(slackcfg.file_type) == 0 or file_to_delete["filetype"] in slackcfg.file_type:
                pass
            else:
                #
                #file_name = unicodedata.normalize('NFKD', file_to_delete["name"]).encode('ascii', 'ignore')
                #print "File type is different from configuration {}".format(file_name)
                continue

            try:
                print u"Deleting file \"{0}\" (file id: {1})..." \
                    .format(file_to_delete["name"], file_to_delete["id"])
            except UnicodeDecodeError as exception_msg:
                file_name = unicodedata.normalize('NFKD', file_to_delete["name"]).encode('ascii', 'ignore')
                print u"Deleting file \"{0}\" (file id: {1})..." \
                    .format(file_name, file_to_delete["id"])
            except UnicodeEncodeError as exception_msg:
                file_name = unicodedata.normalize('NFKD', file_to_delete["name"]).encode('ascii', 'ignore')
                print u"Deleting file \"{0}\" (file id: {1})..." \
                    .format(file_name, file_to_delete["id"])

            timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
            delete_url = slackcfg.http_string + slackcfg.slack_domain + slackcfg.slack_delete_file + timestamp
            result = send_request_post(slackcfg=slackcfg, request_url=delete_url, request_data={
                "token": slackcfg.token,
                "file": file_to_delete["id"],
                "set_active": "true",
                "_attempts": "1"})
            op_result, op_message = interpret_slack_response(result)
            if not op_result:
                print op_message

if __name__ == '__main__':
    SLACKCONFIG = SlackConfig()
    if SLACKCONFIG.config_check():
        delete_files_on_slack(SLACKCONFIG)
