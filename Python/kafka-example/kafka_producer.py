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

import argparse
from math import sqrt
from kafka import KafkaProducer

def is_prime(x):
    if x < 2:
        return False
    for i in range(2, int(sqrt(x)+1)):
        if x % i == 0:
            return False
    return True


parser = argparse.ArgumentParser(description='Run Kafka client')
parser.add_argument('-topic', metavar='topic', nargs='?', default="test", help='name of Kafka topic')
parser.add_argument('-ip', metavar='serverIP', nargs='?', default="127.0.0.1", help='IP address of Kafka server')
parser.add_argument('-port', metavar='severPort', nargs='?', default="9092", help='Port of Kafka server')
args = parser.parse_args()


print("Parameters of connection:")
print("Server IP: {}".format(args.ip))
print("Server Port: {}".format(args.port))
print("Kafka topic: {}".format(args.topic))
print("To stop the program to run just press Ctrl-C")

producer = KafkaProducer(bootstrap_servers="{}:{}".format(args.ip, args.port))

try:
    for i in range(100):
        if is_prime(i):
            next_prime_str = "Next prime number is {}".format(i)
            producer.send(args.topic, bytes(next_prime_str, 'utf-8'))
        if i % 10 == 0:
            input("Press Enter to continue...")
except:
    pass
