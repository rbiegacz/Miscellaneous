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

#pylint: disable = C0301

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

_AGING = 350
_TOKEN = ""
_SLACKDOMAIN = ""
_SLACKFILELIST = "https://slack.com/api/files.list"
_SLACKDELETEFILE = ".slack.com/api/files.delete?t="
_HTTPSTRING = "https://"
#_FILETYPE = {"text", "jpg", "png", "pptx", "doc", "pdf"}
_FILETYPE = {}

def interpret_slack_response(response):
    """
        this function interprets the error received from requests.post method.
    :param response:
        it's a response return from requests.post call.
        please, read more here: http://docs.python-requests.org/en/master/api/#requests.Response
    :return:
        this function will inte
    """

    resultstring = None
    resultboolean = True
    response_dict = json.loads(response._content)

    #for chunk in response.iter_content(chunk_size=128):
    #    print chunk

    if not response.ok:
        resultstring = "Got error from the Web Service. Take a look on the error.\n"
        resultstring += response._content
    else:
        if response_dict["ok"]:
            resultstring = "Operation successful."
        else:
            resultstring = "Got error from the Web Service. Take a look on the error.\n"
            resultstring += response._content
    return resultboolean, resultstring

def delete_files_on_slack():
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
        files_list_url = _SLACKFILELIST
        date = str(calendar.timegm((datetime.now() + timedelta(-_AGING)).utctimetuple()))
        data = {"token": _TOKEN, "ts_to": date}
        try:
            response = requests.post(files_list_url, data=data)
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

            #print file_to_delete["filetype"]
            if len(_FILETYPE) == 0 or file_to_delete["filetype"] in _FILETYPE:
                pass
            else:
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

            timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
            delete_url = _HTTPSTRING + _SLACKDOMAIN + _SLACKDELETEFILE + timestamp
            result = requests.post(delete_url, data={
                "token": _TOKEN,
                "file": file_to_delete["id"],
                "set_active": "true",
                "_attempts": "1"})
            op_result, op_message = interpret_slack_response(result)
            if not op_result:
                print op_message

def config_check():
    """
    this function verifies if the script is confiugured in appropriate way
    :return:
    True if all the parameters are ok and False otherwise
    """
    def message(parameter_string):
        """
        simple function to display error messages
        :param parameter_string:
        parameter string to use in error message
        :return:
        error string
        """
        return "Configure {} parameter in appropriate way.".format(parameter_string)
    if _AGING <= 1:
        print message("_AGING")
        return False
    if _TOKEN == "":
        print message("_TOKEN")
        return False
    if _SLACKDOMAIN == "":
        print message("_SLACKDOMAIN")
        return False
    if len(_FILETYPE) == 0:
        print "Deleting all file types."
    else:
        print "Deleting select file types: {}".format(_FILETYPE)
    print "Deleting files older than {} days\n".format(_AGING-1)
    return True

if __name__ == '__main__':
    if config_check():
        delete_files_on_slack()
