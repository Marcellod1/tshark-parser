import json
from datetime import datetime

# Returns the layer info for an input packet as a python dictionary
# Returns null if the information is not available in the packet
def getPacketInfo(packet_json, key):
    try:
        return packet_json["_source"]["layers"][key][0]
    except:
        return None


# Calculates the total transmission delay between the first packet in an input list and the last packet
# expects a list of python arrays as input
def get_total_bytes(json_packets):
    total_bytes = 0

    for packet in json_packets:
        packet_bytes = getPacketInfo(packet, "ip.len")

        if(packet_bytes != None):
            total_bytes += int(packet_bytes)
    
    return total_bytes


# Calculates the total transmission delay between the first packet in an input list and the last packet
# expects a list of python arrays as input
def get_total_delay(json_packets):
    # Calculate difference in time from the first packet in the frame to the last
    initial_time = getPacketInfo(json_packets[0], "frame.time")
    final_time = getPacketInfo(json_packets[len(json_packets)-1], "frame.time")

    initial_time = datetime.strptime(initial_time.split(".")[0], "%b %d, %Y %H:%M:%S")
    final_time = datetime.strptime(final_time.split(".")[0], "%b %d, %Y %H:%M:%S")

    # Calculate total delay of the transfer and avg throughput
    total_delay = final_time - initial_time
    total_delay = total_delay.total_seconds()
    return total_delay


# returns a dicitonary representing the total byte traffic on each dstport or srcport
# requires a port_type argument which can be "dst_port" or "src_port"
def get_traffic_by_port(json_packets, port_type):
    src_port_traffic = {}

    for packet in json_packets:
        
        port_key = ""
        tcp_port = getPacketInfo(packet, "tcp." + port_type)
        udp_port = getPacketInfo(packet, "udp." + port_type)
        packet_len = getPacketInfo(packet, "ip.len")

        if(packet_len == None):
            continue
    
        if(tcp_port != None):
            port_key = str(tcp_port)
        elif(udp_port != None):
            port_key = str(udp_port)
        else:
            continue

        if(port_key not in src_port_traffic.keys()):
            src_port_traffic[port_key] = 0
        
        src_port_traffic[port_key] += int(packet_len)

    return src_port_traffic



if __name__ == "__main__":

    #Open the json file for reading and load into an array of python dictionaries
    json_file = open("../json/trace.json", "r")
    json_packets = json.load(json_file)
    json_file.close()

    total_bytes = get_total_bytes(json_packets)
    total_packets = len(json_packets)

    # Print and caclulate  average packet size information
    print("---------------------")
    print("Total Bytes in trace: " + str(total_bytes))
    print("Total Packets in trace: " + str(total_packets))
    print("Average packet size(bytes): " + str(total_bytes // total_packets))
    print("---------------------")
    
    total_delay = get_total_delay(json_packets)
    throughput = total_bytes // total_delay

    print("Average throughput(bytes/sec): " + str(throughput))
    print("---------------------")
    
    # sort and print port traffic by src port number 
    print("port data by srcport number: ")
    port_dict = get_traffic_by_port(json_packets, "srcport")
    port_dict = sorted(port_dict.items(), key=lambda x: x[1], reverse=True)

    for i in port_dict:
        print("port {}, {} bytes, ({:.4f}%)".format(i[0], i[1], (i[1]/total_bytes)*100))

    print("---------------------")

    # sort and print port traffic by dst port number 
    print("port data by dstport number: ")
    port_dict = get_traffic_by_port(json_packets, "dstport")
    port_dict = sorted(port_dict.items(), key=lambda x: x[1], reverse=True)

    for i in port_dict:
        print("port {}, {} bytes, ({:.4f}%)".format(i[0], i[1], (i[1]/total_bytes)*100))

    print("---------------------")