using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

namespace VtbFacap
{
    using cls = VtbFacapDataReceiver;

    public class VtbFacapDataReceiver
    {
        public string ip;
        public int port;

        private Thread receiveThread;
        private UdpClient client;
    
        static private readonly object startListenLock = new object();
        static private HashSet<Tuple<string, int>> addressesBeingListened = new HashSet<Tuple<string, int>> {};
        static private Dictionary<string, string> lastMessages = new Dictionary<string, string> {};

        public void StartListen()
        {
            Tuple<string, int> address = new Tuple<string, int> (this.ip, this.port);

            lock (cls.startListenLock)
            {
                if (!cls.addressesBeingListened.Contains(address))
                {
                    cls.addressesBeingListened.Add(address);

                    this.receiveThread = new Thread(new ThreadStart(ReceiveData));
                    this.receiveThread.IsBackground = true;
                    this.receiveThread.Start();
                }
            }
        }
    
        private void ReceiveData()
        {
            Debug.Log($"[VtbFacap] Start listening to ip={this.ip} port={this.port}");

            this.client = new UdpClient(this.port);
            IPEndPoint ipEndpoint = new IPEndPoint(IPAddress.Parse(this.ip), this.port);

            while (true)
            {
                try
                {
                    byte[] data = this.client.Receive(ref ipEndpoint);
                    cls.lastMessages[$"{this.ip}:{this.port}"] = Encoding.ASCII.GetString(data);
                }
                catch (System.Threading.ThreadAbortException e)
                {
                    Debug.Log($"[VtbFacap] Stop listening ({e.ToString()})");
                }
            }
        }

        public string GetLastMsg()
        {
            string lastMsg = null;
            cls.lastMessages.TryGetValue($"{this.ip}:{this.port}", out lastMsg);
            return lastMsg;
        }
    }
}
