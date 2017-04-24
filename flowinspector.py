#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pcap, socket, struct
import numpy as np
from cymru import *

'''open a lot of pcaps at once, using a number of worker processes'''
def inspect_pcaps(pcaps, processes=1):
    from multiprocessing import Pool
    p = Pool(processes)
    flows = p.map(flow, pcaps)
    return flows

'''retrieves a 4-tupel identifying a tcp/ip connection'''
def _get_flow_tuple(ip_pkt):
    s_ip = ip_pkt[12:16]
    d_ip = ip_pkt[16:20]
    
    ihl = ord(ip_pkt[0]) % 16
    tcp = ip_pkt[ihl*4:]
    s_port, d_port = struct.unpack("!HH", tcp[:4])
    return (s_ip, s_port, d_ip, d_port)

'''returns a bytes/s array for the given data in the interval [start_ts, end_ts] with a given sampling_frequency'''
def computeTrafficGraph(data, start_ts, end_ts, sampling_frequency=1):
    duration = end_ts - start_ts
    if end_ts == float("inf"): duration = data[-1][0] - start_ts
    traffic = [0] * int(duration * sampling_frequency + 3)
    
    for ts, length, dscp in data:
        traffic[int((ts-start_ts) * sampling_frequency + 1)] += length * sampling_frequency
    return traffic

'''returns a number of gaps for the given traffic graph'''
def computeGapCount(traffic):
    gaps = 0
    inGap = True
    for i, t in enumerate(traffic):
        # entering gap
        if not inGap and t == 0:
            inGap = True
            gaps += 1
        # leaving gap
        if inGap and t > 0:
            inGap = False
    return gaps
    
def loadLabels(path):
    import csv
    labels = {}
    with open(path) as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";", quotechar='"')
        for row in reader:
            labels[row["filename"]] = row["label"]
    return labels

'''returns standart metrics for the given data.'''
def computeMetrics(data, start_ts, end_ts):
    metrics = {}
    if len(data) == 0:
        metrics["packets"] = 0
        metrics["bytes"] = 0
        metrics["bytes_avg"] = 0
        metrics["bytes_std"] = 1
        metrics["iat_avg"] = 0
        metrics["iat_std"] = 1
        metrics["traffic_avg"] = 0
        metrics["traffic_std"] = 1
        metrics["dscp_median"] = 0
        return metrics
        
    lengths = zip(*data)[1]
    dscps = zip(*data)[2]
    traffic = computeTrafficGraph(data, start_ts, end_ts)
    
    metrics["packets"] = len(lengths)
    metrics["bytes"] = sum(lengths)
    metrics["bytes_avg"] = np.average(lengths)
    metrics["bytes_std"] = np.std(lengths)
    
    interarrival = []
    last = 0.0
    for ts in zip(*data)[0][1:]:
        interarrival.append(ts-last)
        last = ts
    if len(interarrival) == 0:
        metrics["iat_avg"] = end_ts-start_ts
        metrics["iat_std"] = 0
    else:
        metrics["iat_avg"] = np.average(interarrival)
        metrics["iat_std"] = np.std(interarrival)
    
    metrics["traffic_avg"] = np.average(traffic)
    metrics["traffic_std"] = np.std(traffic)
    
    metrics["dscp_median"] = int(np.median(dscps))
    return metrics

'''representation of relevant information inside a tcp-flow'''
class flow:
    '''Creation of a flow object from a provided pcap-flow file.'''
    def __init__(self, filename):
        self._filename = filename
        # read file and save basic information
        self._readPcap(filename)
        # compute basic metrics
        self.fmetric = computeMetrics(self.forward, 0.0, self.duration)
        self.bmetric = computeMetrics(self.backward, 0.0, self.duration)
        
    def _readPcap(self, filename):
        thePcap = pcap.pcap(filename)
        self.forward = []
        self.backward = []
        
        ts, pkt = thePcap.next()
        ip = pkt[14:]
        dscp = ord(ip[1]) / 4
        
        # set flow tupel and cap start
        self.srcip, self.srcport, self.dstip, self.dstport = _get_flow_tuple(ip)
        self.start = ts
        self.end = ts

        # add syn packet
        self.forward.append((0.0, len(ip), dscp))
        
        for ts, pkt in thePcap:
            # skip over malformed packets
            if len(pkt) < 14+20: continue
            if ts < self.start: continue
        
            # set the latest packet as a potential end
            self.end = ts

            ip = pkt[14:]
            dscp = ord(ip[1]) / 4
            srcip = _get_flow_tuple(ip)[0]
            if srcip == self.srcip:
                self.forward.append((ts-self.start, len(ip), dscp))
            else:
                self.backward.append((ts-self.start, len(ip), dscp))
                
        del(thePcap)
        self.duration = self.end - self.start
        self.proto = struct.unpack("!B", ip[9:10])[0]

    INTERVALS = [0]+[2**x for x in range(12)]
    FEATURE_ORDER = ["packets","bytes","bytes_avg","bytes_std","iat_avg","iat_std","traffic_avg","traffic_std","dscp_median"]
    
    '''returns metrics for all defined flow.INTERVALS'''
    def _getIntervalMetrics(self, cumulative):
        '''maps flow.INTERVALS to the provided data indices'''
        def __mapDataToInterval(data):
            index_list = []
            interval_index = 0
            data_index = 0
            
            # add all indices, that relate to an existing timesstamp
            # either the the last ts is only < float("Inf") -> done
            for data_index, (ts, _, _) in enumerate(data):
                while ts >= flow.INTERVALS[interval_index]:
                    index_list.append(data_index)
                    if interval_index < len(flow.INTERVALS)-1: 
                        interval_index += 1
                    else:
                        break

            # or the last ts is eg < 16 -> added here (and padded with empty flows)
            for interval_index in range(interval_index, len(flow.INTERVALS)):
                index_list.append(data_index)
            
            return index_list
        
        '''compute the halfflow metrics for flow.INTERVALS and the provided data.'''
        def __halfflowMetrics(data):
            index_list = __mapDataToInterval(data)
            metrics = []
            for i in range(len(flow.INTERVALS)-1):
                if cumulative:
                    m = computeMetrics(data[:index_list[i+1]], 0.0, flow.INTERVALS[i+1])
                else:
                    m = computeMetrics(data[index_list[i]:index_list[i+1]], flow.INTERVALS[i], flow.INTERVALS[i+1])
                metrics.append(m)

            if len(metrics) != len(flow.INTERVALS)-1: raise Exception("At least one interval is missing in the metrics!")
            return metrics
        
        fmetrics = __halfflowMetrics(self.forward)
        bmetrics = __halfflowMetrics(self.backward)
        return (fmetrics, bmetrics)
        
    @staticmethod
    def getAutoencoderMetricsVectorHeader():
        out = []
        for direction in ["f","b"]:
            for ts in flow.INTERVALS[1:]:
                out += ["{}_{}_{}".format(ts, direction, attr) for attr in flow.FEATURE_ORDER]
        return out
    
    @staticmethod
    def getAutoencoderMetricsVectorLength():
        return len(flow.getAutoencoderMetricsVectorHeader())
    
    '''returns a vector of the concatenated interval metrics'''
    def getAutoencoderMetricsVector(self, cumulative=True):
        fmetrics, bmetrics = self._getIntervalMetrics(cumulative)
        out = []
        for metric in fmetrics+bmetrics:
            out += [metric[f] for f in flow.FEATURE_ORDER]
            
        return out

    @staticmethod
    def getCSVHeader(additionals=[]):
        return "duration_ms,f_bytes,b_bytes,f_packets,b_packets,proto,as_name,fb_ratio,f_port,b_port,f_bps,b_bps,filename,f_dscp,b_dscp,f_iat_avg,f_iat_std,b_iat_avg,b_iat_std,f_gaps,b_gaps".split(",") + sorted(additionals)
    
    def getCSVRepr(self, additionals={}):
        asname = self.as_name if hasattr(self, 'as_name') else ""
        try: fb_ratio = float(self.fmetric["bytes"])/float(self.bmetric["bytes"])
        except ZeroDivisionError: fb_ratio = "NaN"
        try: b_bps = int(float(self.bmetric["bytes"])/float(self.duration))
        except ZeroDivisionError: b_bps = "NaN"
        try: f_bps = int(float(self.fmetric["bytes"])/float(self.duration))
        except ZeroDivisionError: f_bps = "NaN"
        f_gaps, b_gaps = self.defaultGapCounts()
        return [
            int(self.duration*1000),
            self.fmetric["bytes"],
            self.bmetric["bytes"],
            self.fmetric["packets"],
            self.bmetric["packets"],
            self.proto,
            asname,
            fb_ratio,
            self.srcport,
            self.dstport,
            f_bps,
            b_bps,
            self._filename,
            self.fmetric["dscp_median"],
            self.bmetric["dscp_median"],
            self.fmetric["iat_avg"],
            self.fmetric["iat_std"],
            self.bmetric["iat_avg"],
            self.bmetric["iat_std"],
            f_gaps,
            b_gaps
        ] + [v for k,v in sorted(additionals.items())]
    
    '''lookup ASN information for the flow.'''
    def lookupASN(self):
        asn = lookup(socket.inet_ntoa(self.dstip))
        if asn:
            try: self.asn = int(asn["AS"])
            except ValueError: pass
            self.as_name = asn["AS Name"]
            self.bgp_prefix = asn["BGP Prefix"]
        
    def __repr__(self, header=False):
        out = []
        out.append("{}:{} -> {}:{}".format(socket.inet_ntoa(self.srcip), self.srcport, socket.inet_ntoa(self.dstip), self.dstport))
        out.append("forward metrics:  {}".format(str(self.fmetric)))
        out.append("backward metrics: {}".format(str(self.bmetric)))
        if hasattr(self, "asn"): out.append("asn: {} - {} [{}]".format(self.asn, self.bgp_prefix, self.as_name))
        return "flow({}\n     {})".format(out[0], "\n     ".join(out[1:]))
    
    '''show a plot of the traffic graphs'''
    def show(self, scale="linear"):
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
        
        sampling_frequency = 1.0
        x_axis = np.arange(0, int(self.duration + 20), 1.0/sampling_frequency)

        forward_traffic = computeTrafficGraph(self.forward, 0.0, self.duration, sampling_frequency)
        backward_traffic = computeTrafficGraph(self.backward, 0.0, self.duration, sampling_frequency)
        fig, ax1 = plt.subplots()
        ax1.plot(x_axis[:len(forward_traffic)], forward_traffic, lw=2, c="red")
        ax1.plot(x_axis[:len(backward_traffic)], backward_traffic, lw=2, c="blue")
        
        ax2 = ax1.twinx()
        ax2.scatter([t for t, s, _ in self.forward], [s for t, s, _ in self.forward], alpha=0.3, c="red")
        ax2.scatter([t for t, s, _ in self.backward], [s for t, s, _ in self.backward], alpha=0.3, c="blue")
        
        plt.legend(handles = [mpatches.Patch(color='red', label='forward'), mpatches.Patch(color='blue', label='backward')])
        ax1.set_xlabel('time (s)')
        ax1.set_ylabel('traffic (bytes/s)')
        ax2.set_ylabel('packet size (byte)')
        ax1.set_ylim(bottom=0)
        ax2.set_ylim(bottom=0)
        ax1.set_xlim(left=0, right=(len(forward_traffic)-1)/sampling_frequency)
        plt.yscale(scale)
        plt.show(block=False)

    def defaultGapCounts(self):
        forward_traffic = computeTrafficGraph(self.forward, 0.0, self.duration)
        backward_traffic = computeTrafficGraph(self.backward, 0.0, self.duration)
        return (computeGapCount(forward_traffic), computeGapCount(backward_traffic))

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="load flow-pcap and write out basic information")
    parser.add_argument("-q", "--quiet", action="store_true", help="don't show the bandwidth graph")
    parser.add_argument("pcap", help="flow pcap file")
    args = parser.parse_args()
    
    testflow = flow(args.pcap)
    testflow.lookupASN()
    print(testflow)
    print(testflow.getCSVRepr())
    testflow.show()
    raw_input("Press Enter to exit...")
    