import argparse
import time
from pwn import process
import csv
import json

csv1 = "ping1.csv"
csv2 = "ping2.csv"
csv3 = "ping3.csv"
csvSpt = "spt.csv"
csvFast = "fast.csv"

def remove_non_ansi(input_string):
    output = ''.join(char for char in input_string if 32 <= ord(char) <= 126 or char == '\n')
    start = output.find("{")
    end = output.find("}")
    output = output[start:end+1]
    return output


def printRecv(p, recv):
    while True:
        try:
            recv = p.recvline().decode().strip()
            if not recv:
                break
            print(recv)
        except EOFError:
            break

    return recv

def endOfRecvBlock(p, recv):
    while True:
        try:
            recv = p.recvline().decode().strip()
            if not recv:
                break
        except EOFError:
            break

    return recv

def wholeRecv(p, recv):
    line = ""
    while True:
        try:
            line = p.recvline().decode().strip()
            if not line:
                break
            else:
                recv = recv + line
        except EOFError:
            break

    return recv
    

def append_to_csv(filename, data):
   
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([data])

def takeMeasurementPrint():
    recv = ""

    # ping
    p1 = process(["ping", "google.com", "-c", "3"])  # basic ping
    endOfRecvBlock(p1, recv)
    recv = endOfRecvBlock(p1, recv)[23:]
    recv = recv.replace("/", ",")
    recv = recv.replace(" ms", "")
    print(recv)
    # append recv to csv1
    append_to_csv(csv1, recv)

    p2 = process(["ping", "185.166.104.3", "-c", "3"])  # test Iran
    endOfRecvBlock(p2, recv)
    recv = endOfRecvBlock(p2, recv)[23:]
    recv = recv.replace("/", ",")
    recv = recv.replace(" ms", "")
    print(recv)
    # append recv to csv2
    append_to_csv(csv2, recv)

    p3 = process(["ping", "104.16.103.15", "-c", "3"])  # test PR
    endOfRecvBlock(p3, recv)
    recv = endOfRecvBlock(p3, recv)[23:]
    recv = recv.replace("/", ",")
    recv = recv.replace(" ms", "")
    print(recv)
    # append recv to csv3
    append_to_csv(csv3, recv)

    # speedtest
    p4 = process(["speedtest-cli", "--csv"])
    recv = endOfRecvBlock(p4, recv)
    print(recv)
    # append recv to csvSpt
    append_to_csv(csvSpt, recv)
    p4.kill()

    # fast
    recv = ""
    p5 = process(["fast", "-u", "--json"])
    recv = remove_non_ansi(wholeRecv(p5, recv))
    print(recv)
    recvJson = json.loads(recv)
    values = recvJson.values()
    csv_string = ','.join(map(str, values))
    # append recv to csvFast
    append_to_csv(csvFast, csv_string)
    p5.kill()

def main(runtime_hours):

    append_to_csv(csv1, "min(ms), mean(ms), max(ms), mdev(ms)")
    append_to_csv(csv2, "min(ms), mean(ms), max(ms), mdev(ms)")
    append_to_csv(csv3, "min(ms), mean(ms), max(ms), mdev(ms)")
    append_to_csv(csvSpt, "Server ID,Sponsor,Server Name,Timestamp,Distance,Ping,Download,Upload,Share,IP Address")
    append_to_csv(csvFast, "downloadSpeed,uploadSpeed,downloaded,uploaded,latency,bufferBloat,userLocation,userIp")


    runtime_seconds = runtime_hours * 3600
    print(f"Speedtest will run for {runtime_hours} hour(s) ({runtime_seconds} seconds).")
    
    start_time = time.time()
    while time.time() - start_time < runtime_seconds:
        sleep_time = time.time() + 600
        takeMeasurementPrint()
        try:
            print("reading at: "+ str(time.time()))
            # print(sleep_time, time.time(), sleep_time - time.time())
            time.sleep(sleep_time - time.time())  # wait till next 10 minute period
        except Exception as e:
            print(e)
        

    print("Runtime completed.")
    # takeMeasurementPrint()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a speedtest for a specified length of time in hours.")
    parser.add_argument("runtime_hours", type=float, help="The runtime length in hours.")
    args = parser.parse_args()
    
    try:
        if args.runtime_hours <= 0:
            raise ValueError("Runtime length must be greater than zero.")
        main(args.runtime_hours)
    except ValueError as e:
        print(f"Error: {e}")
