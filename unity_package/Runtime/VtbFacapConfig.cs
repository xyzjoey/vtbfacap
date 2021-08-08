using Newtonsoft.Json;
using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;

namespace VtbFacap
{
    using BlendshapeName = System.String;
    using ParamName = System.String;

    [System.Serializable]
    public class ParamValue
    {
        [ClampedCurveAttribute(0f, 0f, 1f, 1f, "map value from x axis to y axis")]
        public AnimationCurve control = AnimationCurve.Linear(0f, 0f, 1f, 1f);
        [Range(0f, 1f)]
        public float smooth = 0.15f;
        [Range(-1f, 1f)]
        public float calibrate = 0f;
    }

    [System.Serializable]
    public class ParamItem : SerializableDictionary<ParamName, ParamValue> {}

    [System.Serializable]
    public class FaceMap : SerializableDictionary<BlendshapeName, ParamItem> {}

    [System.Serializable]
    public class VtbFacapConfig
    {
        public FaceMap faceMap = new FaceMap();

        public void LoadConfig(string data)
        {
            var result = JsonConvert.DeserializeObject<dynamic>(data);
            this.faceMap.Clear();
            
            foreach (var blandshapeMap in result["faceMap"])
            {
                this.faceMap[blandshapeMap.Name] = new ParamItem();
                foreach (var paramItem in blandshapeMap.Value)
                {
                    ParamValue paramValue = new ParamValue();
                    
                    // create curve
                    paramValue.control = new AnimationCurve();
                    foreach (var pt in paramItem.Value["controls"]) paramValue.control.AddKey((float)pt[0], (float)pt[1]);
                    if (paramValue.control.length < 2) paramValue.control.AddKey(1f, 1f);
                    Utils.SmoothCurve(paramValue.control);

                    paramValue.smooth = paramItem.Value["smooth"];
                    paramValue.calibrate = paramItem.Value["calibrate"];

                    this.faceMap[blandshapeMap.Name][paramItem.Name] = paramValue;
                }
            }
        }

        public void SaveConfigFile(string path)
        {
            File.WriteAllText(
                path,
                JsonConvert.SerializeObject(new Dictionary<string, dynamic> {{"faceMap", this.faceMap}}, Formatting.Indented)
            );
        }
    }
}
