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

            // get tracking data
            string msg = this.dataReceiver.GetLastMsg();
            if (msg == null) return;
            float[] shapeValues = Array.ConvertAll(msg.Split(' '), float.Parse);

            // update model
            int i = 0;

            foreach (var blandshapeMap in this.config.faceMap)
            {
                float value = shapeValues[i];
                foreach (var paramItem in blandshapeMap.Value)
                {
                    var paramValue = paramItem.Value;  // Q: copy?
                    CubismParameter modelParam = this.model.Parameters.FindById(paramItem.Key);

                    // scale by config
                    value = paramValue.control.Evaluate(value - paramValue.calibrate);
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
