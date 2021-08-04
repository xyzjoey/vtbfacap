using Live2D.Cubism.Core;
using Live2D.Cubism.Framework;
using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using VtbFacap;

namespace VtbFacap{
    public class VtbFacap : MonoBehaviour
    {
        public VtbFacapConfig facapConfig;

        VtbFacapDataReceiver dataReceiver = new VtbFacapDataReceiver();
        CubismModel model;
        CubismParameter paramBreath;
        float t = 0f;

        void Start()
        {
            this.model = this.FindCubismModel();
            this.paramBreath = this.model.Parameters.FindById("ParamBreath");
            this.dataReceiver.init();
        }

        void LateUpdate()
        {
            // update breath
            this.t += Time.deltaTime;
            this.paramBreath.Value = Mathf.Sin(t) * 0.5f + 0.5f;

            // update tracking
            string msg = this.dataReceiver.GetLastMsg();
            if (msg == null) return;
            float[] shapeValues = Array.ConvertAll(msg.Split(' '), float.Parse);
            // List<float> values = List<float>.ConvertAll(msg.Split(' '), float.Parse);

            int i = 0;

            foreach (var configPair in this.facapConfig.paramMap)
            {
                float value = shapeValues[i];
                // x.Index;
                // float value = shapeValues[x.Index];
                foreach (var outputConfigPair in configPair.Value)
                {
                    CubismParameter param = this.model.Parameters.FindById(outputConfigPair.Key);

                    // scale by config
                    value = value * (outputConfigPair.Value.max - outputConfigPair.Value.min) + outputConfigPair.Value.min - outputConfigPair.Value.mean;
                    // scale by model min max
                    value = value * (param.MaximumValue - param.MinimumValue) + param.MinimumValue;
                    // smooth
                    value = Mathf.Lerp(param.Value, value, 1 - outputConfigPair.Value.smooth);

                    param.Value = value;
                    
                    Debug.Log(outputConfigPair.Key + " raw: " + value + " final: " + param.Value);
                }
                ++i;
            }
        }
    }
}
