using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace VtbFacap
{
    public class VtbFacap2D : MonoBehaviour
    {
        public TextAsset configFile;
        public VtbFacapConfig config = new VtbFacapConfig();
        public string ip = "127.0.0.1";
        public int port = 5066;

        private VtbFacapDataReceiver dataReceiver;
        private CubismModel model;
        private CubismParameter paramBreath;
        private float t = 0f;

        void Start()
        {
            this.model = this.FindCubismModel();
            this.paramBreath = this.model.Parameters.FindById("ParamBreath");
            this.dataReceiver = new VtbFacapDataReceiver { ip = this.ip, port = this.port };
            this.dataReceiver.StartListen();
        }

        void LateUpdate()
        {
            // update breath
            this.t += Time.deltaTime;
            this.paramBreath.Value = Mathf.Sin(t) * 0.5f + 0.5f;

            // get tracking data
            string msg = this.dataReceiver.GetLastMsg();
            if (msg == null) return;
            float[] facapValues = Array.ConvertAll(msg.Split(' '), float.Parse);

            // sync eye
            int leftEyeOpenIndex = this.config.faceMap.IndexOf("left_eye_open");
            int rightEyeOpenIndex = this.config.faceMap.IndexOf("right_eye_open");
            (float minEyeOpen, float maxEyeOpen, int maxEyeOpenIndex) = (facapValues[leftEyeOpenIndex] <= facapValues[rightEyeOpenIndex] ?
                                                                         (facapValues[leftEyeOpenIndex], facapValues[rightEyeOpenIndex], rightEyeOpenIndex) :
                                                                         (facapValues[rightEyeOpenIndex], facapValues[leftEyeOpenIndex], leftEyeOpenIndex));
            float eyeSync = this.config.eyeSync.Evaluate(maxEyeOpen - minEyeOpen);
            facapValues[maxEyeOpenIndex] = Mathf.LerpUnclamped(maxEyeOpen, minEyeOpen, eyeSync);

            // update model
            int i = 0;

            foreach (var blandshapeMap in this.config.faceMap)
            {
                float value = facapValues[i];
                foreach (var paramItem in blandshapeMap.Value)
                {
                    var paramValue = paramItem.Value;  // Q: copy?
                    paramValue.raw = value;
                    CubismParameter modelParam = this.model.Parameters.FindById(paramItem.Key);  // TODO if not exist ...

                    // calibrate
                    value = value - paramValue.calibrate;

                    paramValue.rawAfterCalibrate = value;

                    // scale by config
                    value = paramValue.control.Evaluate(value);
                    // scale by model min max
                    value = value * (modelParam.MaximumValue - modelParam.MinimumValue) + modelParam.MinimumValue;
                    // smooth
                    value = Mathf.LerpUnclamped(modelParam.Value, value, 1 - paramValue.smooth);

                    modelParam.Value = value;
                    
                    // Debug.Log(paramItem.Key + " raw: " + value + " final: " + modelParam.Value);
                }
                ++i;
            }
        }
    }
}
