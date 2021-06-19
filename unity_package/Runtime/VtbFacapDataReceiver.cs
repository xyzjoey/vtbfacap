using System;
using System.Collections;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using UnityEngine;

namespace VtbFacap{
    public class VtbFacapDataReceiver {
    
        Thread receiveThread;
        UdpClient client;
        public string ip = "127.0.0.1";
        public int port = 5066;
        private string lastMsg = null;
    
        public void init()
        {
            receiveThread = new Thread(new ThreadStart(ReceiveData));
            receiveThread.IsBackground = true;
            receiveThread.Start();
        }
    
        private void ReceiveData()
        {
            this.client = new UdpClient(this.port);
            IPEndPoint ipEndpoint = new IPEndPoint(IPAddress.Parse(this.ip), this.port);

            while (true)
            {
                try
                {
                    byte[] data = client.Receive(ref ipEndpoint);
                    this.lastMsg = Encoding.ASCII.GetString(data);
                    // Debug.Log(this.lastMsg);
                }
                catch (Exception err)
                {
                    Debug.LogError(err.ToString());
                }
            }
        }

        public string GetLastMsg()
        {
            string lastMsg = this.lastMsg;
            this.lastMsg = null;
            return lastMsg;
        }
    }
}
